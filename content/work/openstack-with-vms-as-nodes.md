Title: OpenStack using VMs as nodes
Date: 2014-06-05 23:23
Author: flavio
Category: Work
Tags: work, devstack, openstack
Slug: creating-openstack-nodes

Steps for creating VMs that can be used with devstack and provide an Openstack environment.

<!--more-->

# The Scenario

Sounds silly, but I decided it was important to me to make pasta from the flour, instead
of getting it out of a package. In this particular case, I needed to make my own VMs to
run Openstack, instead of using the VMs that [Brent put together][1]. My reasoning for
taking that route was 1) to fully appreciate what it takes make the vms and 2) to have
better insight into what is in the VMs, to ideally make them as bare bones as possible.

The credit for doing this page goes to Sam Hague, one of my guru co-workers.
He set me out with these steps, so I could dive into the world of devstack.

    :::text
    Fedora 20 netinstall, 8Gb qcow2, 2Gb RAM, 2 CPUs
    - Used kvm to create the 8gb qcow2 img first, then selected it via virt-manager
    - Software Selection: select minimal install, make sure Gnome was deselected
    - Installation Destination: leave the automtic partitioning selected.
    - Set root pw to odl, create odl/odl user - add as Administrator
    - Finish install, reboot, shutdown

    - Add extra interfaces via virt-manager so it has three nics in total:

      1) eth0: default NAT: public, 172.16.18.0/24 (in my case)
      2) eth1: isolated - future tenant VMs traffic (no ip addresses needed by nodes)
      3) eth2: isolated, but accessible by laptop OS - 172.16.150.0/24 (in my case)

The nic eth0 is  NAT'ed and will initially use dhcp. Later on, I make it static, but that is not really
needed. That is so, because when we are done here, the vms can reached via their eth2 interfaces, using
static addresses.

The nics eth0, eth1 and eth2 are isolated into their own bridge instance. eth1 and eth2 are also
'host-only' so the only way for nodes to get out is via their eth0.

    - Get the dhcp's ip and then ssh into vm. The virt-manager console is a pain since it doesn't have 
    cut and paste.
    - Log in as odl/odl from the virt-manager console.
    ip addr   # to get ip 

    ssh root@172.16.18.XX  

    echo "odl        ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers

    yum update -y
    # Shouldn't find anything to update since the netinstall should be up to date.
    
    setenforce 0
    sed -i -e 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    
    # use iptables instead of firewalld. It is optional, but since I install samba and have vm isolated,
    # I spent very little time dealing with firewall rules 
    #
    systemctl stop firewalld.service
    systemctl disable firewalld.service

    yum install -y iptables-services
    touch /etc/sysconfig/iptables

    systemctl enable iptables.service
    systemctl start iptables.service
    #systemctl enable ip6tables.service

    iptables -nvL
    
    # network manager can be a pain... disable it
    #
    systemctl stop NetworkManager.service
    systemctl disable NetworkManager.service
    systemctl enable network
    systemctl restart network   ; ## okay to ignore complaints you may get from this command...

    ===

    ## Installing wireshark (and X11 support) in Fedora
    
    yum install -y wireshark xorg-x11-xauth xorg-x11-fonts-* xorg-x11-utils wireshark-gnome
    sed -i 's/#X11Forwarding\ no/X11Forwarding\ yes/'  /etc/ssh/sshd_config
    systemctl restart sshd.service
    
    # Link root’s .XAutority to odl’s
    ln -s /home/odl/.Xauthority /root/

    ===
    
    yum install -y emacs   ;  ## Ignore this if you do not care about emacs

    yum install -y git wget tar bc unzip net-tools bridge-utils
    yum install -y python-devel libffi-devel openssl-devel libxml2-devel libxslt-devel screen MySQL-python
    yum groupinstall -y "Development Tools"
   
    cd && wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
    python ez_setup.py && easy_install pip && pip install virtualenv && echo done

    yum install -y openvswitch && sleep 10
    systemctl enable openvswitch
    systemctl start openvswitch
    lsmod | grep openv

    ## Should look like this:
    ##
    ## [root@localhost ~]# lsmod | grep openv
    ## openvswitch            70953  0 
    ## vxlan                  37295  1 openvswitch
    ## gre                    13535  1 openvswitch
    ## libcrc32c              12603  1 openvswitch

    ===

    ## Install samba, so we can mount node's filesystem from host
    chmod 777 /opt
    yum install -y samba samba-client

    cat <<EOT >> /etc/samba/smb.conf
           [opt]
               path = /opt
               public = yes
               writeable = yes

    EOT
    
    smbpasswd -a root
    smbpasswd -a odl
    systemctl enable smb.service
    systemctl start smb.service

    ## or this if already started
    ## smbcontrol smbd reload-config

    ===

    reboot
    

Copy host's ssh key so you do not need password to get into nodes' shell. If you forget how to do these, google for:
[Setup the SSH server to use keys for authentication](http://www.g-loaded.eu/2005/11/10/ssh-with-keys/) or
[SSH with authentication key instead of password](http://www.debian-administration.org/article/530/SSH_with_authentication_key_instead_of_password) or
[SSH login without password](http://www.linuxproblem.org/art_9.html)

    [redhatlaptop:~]$ scp ~/.ssh/id_rsa.pub odl@172.16.18.X:/home/odl/hostKey
    
    ssh odl@172.16.18.X

    mkdir -p /home/odl/.ssh ; cat /home/odl/hostKey >> /home/odl/.ssh/authorized_keys ; rm -f /home/odl/hostKey
    chmod 700 /home/odl/.ssh ; chmod 600 /home/odl/.ssh/authorized_keys
    touch /home/odl/.Xauthority
    exit

    ## test ssh, sudo and X forwarding...
    ssh -XY odl@172.16.18.X
    sudo wireshark &

Fedora 20 uses bios' devnames instead of a 0 based notation (ie eth0, eth1, eth2...). This is optional, but I find eth0...eth2 much more useable. 
If you like that, [change the default “ens33” network device to old “eth0” on Fedora](http://unix.stackexchange.com/questions/81834/how-can-i-change-the-default-ens33-network-device-to-old-eth0-on-fedora-19). Look for "In Fedora 20, things seem to have changed..."

    sudo su -
    sed -i -e 's/:) rhgb quiet/:) net.ifnames=0 biosdevname=0 rhgb quiet/g' /etc/default/grub
    grub2-mkconfig -o /boot/grub2/grub.cfg

    ## Make hosts aware of each other. You may want to add this to your desktop/laptop OS as well...
    ##
    for x in 141 142 143 144 ; do
       sudo echo "172.16.150.${x} fedora${x}" >> /etc/hosts
    done

    # Rename and tinker /etc/sysconfig/network-scripts/ifcfg-eXXX to ifcfg-eth0, eth1, eth2

    cd /etc/sysconfig/network-scripts

    mv ifcfg-enoXXX ifcfg-eth0
    mv ifcfg-enoYYY ifcfg-eth1
    mv ifcfg-enoZZZ ifcfg-eth2

    THIS_HOST='141'  ## Change this to match the host you are tweaking!!!

    echo "IPADDR=172.16.18.${THIS_HOST}" >> ifcfg-eth0
    echo "NETMASK=255.255.255.0" >> ifcfg-eth0
    echo "GATEWAY=172.16.18.2" >> ifcfg-eth0
    echo "DNS1=8.8.8.8" >> ifcfg-eth0

    echo "IPADDR=172.16.150.${THIS_HOST}" >> ifcfg-eth2
    echo "NETMASK=255.255.255.0" >> ifcfg-eth2
    
    hostnamectl set-hostname "fedora${THIS_HOST}"

At this point, grab devstack from github. I bundled a few scripts and aliases that make life easier. Grab them as well.

    sudo su - odl
    cd /opt
    git clone git://github.com/openstack-dev/devstack.git
    git clone git://github.com/flavio-fernandes/odl_tools.git
    
    cd odl_tools
    mv odlaliases.sh odl_os_ovs.sh odl.sh osdbg.sh osreset.sh ostest.sh setlog.sh /opt/
    mv reallyunstack.sh /opt/devstack/
    
If you made it here, congrats: You are devstack ready!

In addition to the steps above, I did the following tweaks to customize devstack to my liking:

    echo ". /opt/odlaliases.sh" >> ~/.bashrc

    cd /opt/devstack
    git checkout 47ae725f1337ba76189604b685ccaec6c7b7bff9 && git checkout -b tweaks

    # Disable initial config creation
    sed -i -e 's/^\s*create_neutron_initial_network$/    # create_neutron_initial_network/' stack.sh

    # br-ex bug. Dave's patch -- https://review.openstack.org/#/c/99414/
    sed -i -e 's/sudo ovs-vsctl --no-wait -- --may-exist add-br $PUBLIC_BRIDGE/sudo ovs-vsctl -- --may-exist add-br $PUBLIC_BRIDGE/' lib/neutron_plugins/ovs_base
    sed -i -e 's/sudo ovs-vsctl --no-wait br-set-external-id $PUBLIC_BRIDGE/sudo ovs-vsctl br-set-external-id $PUBLIC_BRIDGE/' lib/neutron_plugins/ovs_base

    # Invoke create_nova_conf_neutron from odl-compute post-install only if nova is enabled.
    sudo yum install -y patch
    wget -O /tmp/create_nova_conf_neutron.patch https://gist.githubusercontent.com/anonymous/81dabb70dd6a3be37511/raw/f6c2860cc2dd0a85f2307070380a587154effbd4/gistify822855.txt
    patch -p1 < /tmp/create_nova_conf_neutron.patch


Do all the steps below 
Once you on the control+compute node, power down and then clone the VMs. The hostname and localhost fields will be wrong on the cloned nodes
and need to be changed. Here are the steps I took to remedy that:

    - Log in as root/odl from the virt-manager console.
    
    vi /opt/odl_tools/fixeth.txt

    - In fixeth.txt change THIS_HOST to be the value of the new clone. Make sure OLD_HOST is the value used by
    the host you cloned from.
    
    . /opt/odl_tools/fixeth.txt


PS. I'm sure folks who use Vagrant can do this in a much more elegant way... I will get there, eventually. :)
    
  [1]: http://networkstatic.net/opendaylight-openstack-integration-devstack-fedora-20/ "OpenDaylight OpenStack Integration with DevStack on Fedora"





