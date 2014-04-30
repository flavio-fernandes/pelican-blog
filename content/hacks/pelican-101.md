Title: Getting going on Pelican
Date: 2014-04-30 12:12
Author: flavio
Category: Hacks
Tags: tools
Slug: pelican-101

Quick and dirty steps I took to get Pelican going.

<!--more-->

# The Scenario

I needed to find a way to get content online. Inspired by [Dave Tucker's article][], I set out to use Pelican.

# Steps

I started by creating a Centos 6.x VM, minimal install. Turns out that Pelican requires Python 2.7 or higher, and Centos 6.x comes with
Python 2.6. So, you will need to get a newer version of Python. Good news here is that there is a handy link that gives us the stepping
stones: [Too much data][]:

    :::bash
    yum groupinstall -y "Development tools"
    yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
    yum install -y wget asciidoc

    # Python 2.7.6:
    wget http://python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
    tar xf Python-2.7.6.tar.xz
    cd Python-2.7.6
    ./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
    make && make altinstall

    # Get the setup script for Setuptools:
    cd
    wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
 
    # Then install it for Python 2.7:
    python2.7 ez_setup.py

    # Now install pip using the newly installed setuptools:
    easy_install-2.7 pip

    # Install virtualenv for Python 2.7
    pip2.7 install virtualenv 

At this point, your system is ready to get Pelican going! Because of pip and virtualenv, you need not to be user root to
get it going. Here are the steps, learned from [Patrick Dubroy][]:

    :::bash
    useradd foobar
    su - foobar

    virtualenv-2.7 ~/venv/pelican
    source ~/venv/pelican/bin/activate
    echo "source ~/venv/pelican/bin/activate" >> ~/.bashrc

    pip install pelican
    pip install Markdown
    pip install typogrify
    pip install Fabric

At this point, make your Pelican fly! Read up all about it at [Pelican][]:

    :::text
    mkdir ~/site && cd ~/site
    pelican-quickstart

    Welcome to pelican-quickstart v3.3.0.
    This script will help you create a new Pelican-based website.

    Please answer the following questions so this script can generate the files
    needed by Pelican.
    
    > Where do you want to create your new web site? [.] 
    > What will be the title of this web site? test
    > Who will be the author of this web site? foobar
    > What will be the default language of this web site? [en] 
    > Do you want to specify a URL prefix? e.g., http://example.com   (Y/n) 
    > What is your URL prefix? (see above example; no trailing slash) http://example.com/foobarBlog
    > Do you want to enable article pagination? (Y/n) 
    > How many articles per page do you want? [10] 
    > Do you want to generate a Fabfile/Makefile to automate generation and publishing? (Y/n) 
    > Do you want an auto-reload & simpleHTTP script to assist with theme and site development? (Y/n) 
    > Do you want to upload your website using FTP? (y/N) 
    > Do you want to upload your website using SSH? (y/N) y
    > What is the hostname of your SSH server? [localhost] example.com
    > What is the port of your SSH server? [22] 
    > What is your username on that server? [root] 
    > Where do you want to put your web site on that server? [/var/www] 
    > Do you want to upload your website using Dropbox? (y/N) 
    > Do you want to upload your website using S3? (y/N) 
    > Do you want to upload your website using Rackspace Cloud Files? (y/N) 
    Done. Your new project is available at /home/foobar/site

As far as publishing, I hit a little glitch when using Fabric. Here is the tweak I needed to do to the file:

**fabfile.py**

    :::patch
    (pelican)[foobar@test site]$ diff -u fabfile.py.orig fabfile.py 
    --- fabfile.py.orig   2014-04-30 08:17:26.682669968 -0400
    +++ fabfile.py	      2014-04-30 08:23:04.160681733 -0400
    @@ -22,14 +22,16 @@
             local('mkdir {deploy_path}'.format(**env))
     
     def build():
    -    local('pelican -s pelicanconf.py')
    +    ##BROKEN local('pelican -s pelicanconf.py')
    +    local('pelican ./content -o {deploy_path} -s pelicanconf.py'.format(**env))
     
     def rebuild():
         clean()
         build()
     
     def regenerate():
    -    local('pelican -r -s pelicanconf.py')
    +    ##BROKEN local('pelican -r -s pelicanconf.py')
    +    local('pelican ./content -r -s pelicanconf.py')
     
     def serve():
         local('cd {deploy_path} && python -m SimpleHTTPServer'.format(**env))
    @@ -39,7 +41,8 @@
         serve()
     
     def preview():
    -    local('pelican -s publishconf.py')
    +    ##BROKEN local('pelican -s publishconf.py')
    +    local('pelican ./content -s publishconf.py')
     
     def cf_upload():
         rebuild()
    @@ -51,7 +54,8 @@
     
     @hosts(production)
     def publish():
    -    local('pelican -s publishconf.py')
    +    ##BROKEN local('pelican -s publishconf.py')
    +    local('pelican ./content -o {deploy_path} -s publishconf.py'.format(**env))
         project.rsync_project(
             remote_dir=dest_path,
             exclude=".DS_Store",

Lastly, here is a link to where I keep all the source contents for this Pelican based site:

    :::url
    https://github.com/flavio-fernandes/pelican-blog
    

Enjoy!


# Good References

- [Too much data]: How to install Python 2.7 and Python 3.3 on CentOS 6
- [Vuong Nguyen]: Creating a Blog with Python Pelican
- [Patrick Dubroy]: So You Want to Install a Python Package
- [Virtualenv]: Virtual Python Environment builder
- [Markdown Syntax]: Markdown Syntax Documentation


  [Dave Tucker's article]: http://dtucker.co.uk/lifehack/migrating-from-wordpress-to-pelican-on-paas-part-1.html
  [Too much data]: http://toomuchdata.com/2014/02/16/how-to-install-python-on-centos/
  [Patrick Dubroy]: http://dubroy.com/blog/so-you-want-to-install-a-python-package/
  [Development Tools]: http://thehungrycoder.com/tutorial/yum-groupinstall-may-save-your-hours.html
  [Vuong Nguyen]: http://vuongnguyen.com/creating-blog-python-virtualenv-pelican.html
  [Pelican]: http://docs.getpelican.com/en/latest/getting_started.html
  [Virtualenv]: https://pypi.python.org/pypi/virtualenv
  [Markdown Syntax]: http://daringfireball.net/projects/markdown/syntax.text

