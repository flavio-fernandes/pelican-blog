Title: Adding show/hide button to pelican-bootstrap3 theme
Date: 2014-06-17 01:20
Author: flavio
Category: Hacks
Tags: tools
Slug: pelican-show-hide-button

Easy button for collapsing blobs of data in a pelican page

<!--more-->

I like having blobs of data in the page, but sometimes they get in the way.

For instance, lets say I have some text below that is a bit long, and I would like
to have a button to make it hidden until I need it

<button class="toggle-start-hidden">Show/hide</button>

    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...
    this is a bunch of stuff I would like to hide...


The ability to do that is quite simple: [jQuery][1]! Feel free to look in the repo
I keep my pelican posts to [see examples of how I use it][2], but in essence, this
is what you need to add to the pelican-bootstrap3 theme:

    $ cat themes/pelican-bootstrap3/static/js/show_hide_toggler.js
    
    $(document).ready(function () {
       $("button.toggle-start-hidden").parent().next().hide();
       $("button.toggle-start-hidden").click(function(){ $(this).parent().next().toggle(); });
       $("button.toggle").click(function(){ $(this).parent().next().toggle(); });
     });

Then, add the following lines to themes/pelican-bootstrap3/templates/base.html

    :::patch
    diff --git a/themes/pelican-bootstrap3/templates/base.html b/themes/pelican-bootstrap3/templates/base.html
    index bfbaa62..7e4e5c8 100644
    --- a/themes/pelican-bootstrap3/templates/base.html
    +++ b/themes/pelican-bootstrap3/templates/base.html
    @@ -147,6 +147,9 @@
     <!-- Enable responsive features in IE8 with Respond.js (https://github.com/scottjehl/Respond) -->
     <script src="{{ SITEURL }}/theme/js/respond.min.js"></script>
     
    +<!-- Enable show/hide toggler -->
    +<script src="{{ SITEURL }}/theme/js/show_hide_toggler.js" type="text/javascript"></script>
    +
     {% include 'includes/github-js.html' %}
     {% include 'includes/disqus_script.html' %}
     {% include 'includes/ga.html' %}

To use this feature, simply add either one of these above the blob you want to hide/show.
Make sure to have an empty line between this and the blob itself:

    <button class="toggle-start-hidden">Show/hide</button>
    <button class="toggle">Show/hide</button>

As the name suggests, the difference between these two is what should the the initial state of the
blob controlled by the button.

<button class="toggle">Enjoy or not...</button>

Enjoy!

  [1]: http://jquery.com/
  [2]: https://raw.githubusercontent.com/flavio-fernandes/pelican-blog/master/content/work/openstack-experiment1.md

