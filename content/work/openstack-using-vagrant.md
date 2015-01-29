Title: OpenStack using Vagrant
Date: 2015-01-25 10:11
Author: flavio
Category: Work
Tags: work, vagrant, virtual-box, packstack, openstack
Slug: how-to-openstack-from-vagrant

Using Vagrant to create vm nodes; packstack to start openstack and then create tenant [nested] vms.

<!--more-->

<span id=the_scenario />
## The Scenario ##

I needed a way to easily bring up a bunch of Centos 7 vms to be used as Juno openstack nodes. Using Virtual
Box as hypervisor, I came up with a Vagrant file and packstack's answer file to accomplish that. Also, I wrote
simple scripts to test out the openstack install by creating tenants, launching vms in a couple of subnets,
and associating these tenant vms with floating ips.

Thinking that this could be useful to folks out there, I'm jolting down the steps I used. My goal is to
use Opendaylight instead of neutron with ovs; but I will do that in a separate stage.

To get things going, here is a network topology of the openstack nodes we will be using for this experiment.

<span id=topologyMap />
![topology](|filename|/images/openstack-vagrant-provider-topology.jpg)

In order to connect the future tenant vms to the outside world, I used an additional network and connected it
to a vm that runs as a router + named + dhcpd. As you can see in the picture above, that network is labeled
*Provider Net*.

To get things going faster, I'm assuming that you have a *hypervisor* and *[Vagrant][vagrant]* installed.
I use [Virtual Box][vbox], but you should be able to use anything supported by [Vagrant][vagrant].
The only caveat on that is that you may need to hunt for a Centos 7 distro of Vagrant box that suits your hypervisor.
The [Bento project][bento] may be a good place for that, if you are in such predicament. :) To help folks running
[Vmware fusion][vmfusion], I've already added hooks in the Vagrantfile; *but did not try it out!*.

As part of the provisioning, the vm is expected to be rebooted, because it will do _yum update_ and that will pick up
a new kernel, among some much needed bugfixes. To reload during provisioning, I chose the vagrant's
[reload plugin][vagrantReload]. If you have not done so, install this by issuing the following command:

    $ vagrant plugin install vagrant-reload

<span id=installing_router_vm />
## Installing Router VM ##

If you do not care about connecting the tenant vms to the internet, you can skip the install of the router VM
and continue to the [section below](#installing_rdo_nodes).

To get the router vm instantiated you can use -- guess what?!? -- another github project I put together:
[router-node][routerNode]. The [readme file][routerNodeReadme] spells out most of what you need to do.

In brief, this should be all you need to have router running:

    $ cd some_dir
    $ git clone https://github.com/flavio-fernandes/router-node.git router-node.git && cd router-node.git
    $ # optional: change whatever configuration knob you would like
    $ vagrant up

<span id=installing_rdo_nodes />
## Installing RDO Nodes ##

Start off by cloning this github project:

    $ cd some_dir
    $ git clone https://github.com/flavio-fernandes/rdo-nodes.git rdo-nodes.git && cd rdo-nodes.git

The Vagrantfile is [here][rdoVagrant]
<button class="toggle-start-hidden">Show/hide</button>

[gist:id=c3c9c519b090c4099455]

You can see that I hard coded the ip addresses to my liking. If you do not like the values I used,
simply _grep -ilr 192.168. *_ and replace all the values with what you like. There should not be many
of these. You can see what values to grep for by looking at the [topology figure above](#topologyMap).

If you are using the router vm [mentioned above](#installing_router_vm), be mindful of 2 configuration caveats:

1. Make sure that the [name of the internal network][internalNetNameRtr] is the same on both router's vm and the
   [second network used by the neutron node][internalNetNameNeutron]

1. Make sure that the static ip address given to the [second network used by the neutron node][internalNetNameNeutron] -- aka **neutron_ex_ip** -- is valid for the network of the router.

I made sure that these two assumptions are met, if you chose to leave the values as I have them.

By default, the topology will create 2 compute nodes. If you would like to use 1, or more than 2, all you need
is to set the environment variable as shown:

    $ export RDO_NUM_COMPUTE_NODES=1

If you decide to use more than 4 compute nodes, make sure to add their name and address in the [hosts.json file][hostsJson]

At this point, all you need to do is:

    $ time vagrant up  ;  # this can take a little over 20 minutes on my macbook pro (Late 2013) ...

Once you finish vagrant up for the very first time, consider using [Vagrant Sahara][sahara] so you do not have to
wait long in order to get a clean set of openstack nodes. To install that plugin, all you need is:

    $ vagrant plugin install sahara

The command to get a sahara sandbox setup is:

    $ vagrant sandbox on

The command to get the vms back to the time when you did *vagrant sandbox on* is:

    $ vagrant sandbox rollback

Pretty handy stuff! :)

<span id=goPackstack />
## Go Packstack! ##

In order to configure Openstack with the nodes we are going to be using, I installed packstack -- currently 
the Juno release -- and generated an answers.txt file. Then, I modified a few attributes in the answers.txt
file to reflect the nodes used. I did not manage to automate the list of compute nodes, so **if you used more
or less than 2 compute nodes, you will need to edit the answers.txt file as shown below**:

    $ vagrant ssh
    $ sudo su -
    $ grep COMPUTE_HOSTS /root/answers.txt
    $
    $ vi /root/answers.txt   ;  # make sure COMPUTE_HOSTS has the list you need!


By the way, should you need to know what values I tweaked from the original answers.txt file, you just can diff
them:
<button class="toggle-start-hidden">Show/hide</button>

[gist:id=fe996638affbece80cfd]

    $ diff -Nau /root/answers.txt{.orig,}

It may be a good idea to spend a little time admiring the hard work that packstack does for you... or not. :)
Regardless of what you do here, one thing is certain: Puppet rules! Joke aside, the diff above can teach you a
great deal about the attributes you must change in order to configure the overlay topology, as well as the
interface config for the external bridge (br-ex). On that subject specifically, pay attention to the fact that
openstack expects the provided name for the shared network to match what we provided in the answer file:

    # in answers.txt
    CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS=physnetext:br-ex
    
    # in openstack_part1.sh (referred down below)
    neutron net-create ext --shared  --provider:network_type flat --provider:physical_network physnetext

At this point, once you get everything to look the way you want, run the following scripts as show below:

    $ vagrant ssh
    $ sudo su -
    # cd /root/ && ./openstack_part0.sh
    # cd /root/ && ./openstack_part1.sh
    # su - vagrant
    $ cd /home/vagrant && openstack_part2.sh
    $ cd /home/vagrant && openstack_part3.sh

A brief description of what each bash script does:

**openstack_part0.sh**: install openstack-packstack package and run packstack, using the file in /root/answers.txt.
This step takes 23 minutes on my laptop.<button class="toggle-start-hidden">Show/hide</button>

[gist:id=a2b4ff8e34972986f994]

**openstack_part1.sh**: create tenants and deploy admin network. Note the comment that points out how openstack expects the name of the share network to be what was provided in answers.txt.
<button class="toggle">Show/hide</button>

[gist:id=aa6dc98388efb1b6f76f]

**openstack_part2.sh**: deploy tenant vms for tenant1
<button class="toggle">Show/hide</button>

[gist:id=85c044b52de65f67ba00]

**openstack_part3.sh**: deploy tenant vms for tenant2
<button class="toggle-start-hidden">Show/hide</button>

[gist:id=efd152010ba873cd0309]

<span id=tenantTopology />
## Tenants Topology ##

![topology](|filename|/images/openstack-vagrant-tenants.jpg)

You can see the tenant one's view of the world by clicking on this button: 
<button class="toggle-start-hidden">Show/hide</button>

![topology](|filename|/images/openstack-vagrant-tenant1.jpg)

You can see the tenant two's view of the world by clicking on this button: 
<button class="toggle-start-hidden">Show/hide</button>

![topology](|filename|/images/openstack-vagrant-tenant2.jpg)


As you can see on the figure above, the tenants share the same compute hosts, but are completely isolated
from each other. Using the overlay network, each tenant's subnet is assigned a unique VNI, so the there
is no issue in overlapping the addresses. Because of that, the subnet 3.0.0.0/24 can be re-used and yet
each one of the tenant's router knows how that address range applies to its unique LAN.

Also, you can notice that each vm is given an floating ip out of the provider's network. Since these
addresses are *public* and *unique* to all tenants of this openstack deployment, tenants can potentially
reach each other, but not before getting routed through the shared network, thus using the floating ips.

---
<span id=inspecting />
## Inspecting ##

### Navigating Horizon ###

To login into horizon, simply point your browser to the ip address of your control node. As configured
in the answers.txt file the password we used for admin is _admin_.

    http://192.168.50.20/dashboard/ 

Info on all Tenant VMs
<button class="toggle">Show/hide</button>

![topology](|filename|/images/openstack-vagrant-horizon-tenants.jpg)

There is not a whole lot more to say on these, except that my original drawing
ended up reversing which vms ended up on each of the compute nodes.
No big deal, I hope. :)

Networks and Network Service Agents
<button class="toggle-start-hidden">Show/hide</button>

![topology](|filename|/images/openstack-vagrant-horizon-networks.jpg)
![topology](|filename|/images/openstack-vagrant-horizon-net-services.jpg)

Tenant 1's Network topology
<button class="toggle">Show/hide</button>

![topology](|filename|/images/openstack-vagrant-horizon-tenant1.jpg)

Tenant 2's Network topology
<button class="toggle-start-hidden">Show/hide</button>

![topology](|filename|/images/openstack-vagrant-horizon-tenant2.jpg)

### Looking at interfaces and OVS ###

**NB:** You may notice that every vm instantiated by Vagrant has an interface in the 10.0.2.0/24 subnet. That is
the management interface and you can ignore it for all openstack nodes. In the case of the router vm, that
interface is actually used to forward packets in and out of the internal network. Kinda, sleazy... I know. :) 

Even though the br-ex bridge is created on all compute nodes, it only really matters
on the neutron node. That is because I did not attempt to use [DVR][dvr], but maybe packstack
is trying to anticipate that. Because there is no DVR here, a classic complaint folks have is
that vms of the same tenant but different subnets need to go through the neutron node in order
to reach each other; even if they are on the same compute node. [Opendaylight L3 fwd][odll3] and
[DVR][dvr] can do better on that. More on that in a future post.

#### Peeking at the interfaces and bridges of the control node ####

** Noting to see here, as ovs is not ever installed in this node **
<button class="toggle-start-hidden">Show/hide</button>

[gist:id=47ccc461c619b2515fd8]

#### Peeking at the interfaces and bridges of the neutron node ####

Raw dump can be seen here <button class="toggle-start-hidden">Show/hide</button>

[gist:id=621366f473b79354191c]

There are 3 ovs bridge instances:

1. **br-ex**: this connects the interfaces to the external network. In this case, the shared -- and flat -- provider
network. Note how the br-ex interface actually takes ownership of the address that was once configured at the eth2
interface and makes eth2 a member port of the bridge. This possession occurs due to what we specified in the answers.txt file (look for br-ex in there).

1. **br-tun**: this bridge is used to provide connectivity between all compute nodes and network (aka neutron) nodes.
It is a bit interesting to see the openflow rule that takes care of encapsulating and decapsulating the VNI in the packet before it leaves the node. You can see that in the output of **sudo ovs-ofctl -O OpenFlow10 dump-flows br-tun** command:

      # Decapsulating and sending to br-int
      actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:1

      # Encapsulating and sending to other nodes     

      vlan_tci=0x0004/0x0fff,dl_dst=fa:16:3e:08:bc:10 actions=load:0->NXM_OF_VLAN_TCI[],load:0xd->NXM_NX_TUN_ID[],output:2
      vlan_tci=0x0002/0x0fff,dl_dst=fa:16:3e:7d:87:48 actions=load:0->NXM_OF_VLAN_TCI[],load:0xb->NXM_NX_TUN_ID[],output:3

1. **br-int**: this is called the _integration_ _bridge_. It is used to demux all the interfaces that sit on the overlay
network. Router interfaces, dhcp server interfaces -- in addition to the interfaces of the tenant vms -- are hooked to this
bridge.

There are no linux bridges created in the neutron nodes; only ovs based bridges. Together with that, the iptables
in the neutron node have nothing much to show.  <button class="toggle-start-hidden">Show/hide</button>

[gist:id=339e61824b390f8cf42c]

An interesting fact is that dhcp servers run in their own namespace and use an ip address from the pool. Thus, every
subnet that has dhcpd enabled gets to instantiate an extra namespace. As expected, every router instance also gets
its own namespace.

#### Peeking at the interfaces and bridges of the compute node 1 ####

Raw dump can be seen here <button class="toggle-start-hidden">Show/hide</button>

[gist:id=b8d12e91d922ec5a17f8]

Linux bridges and iptables in the compute node are quite rich <button class="toggle-start-hidden">Show/hide</button>

[gist:id=25b9fed2664d7c967e3e]

One of the interesting findings I get out of the output is that Junos uses Openflow 1.0 protocol, instead of 1.3.
It is also surprising the number of bridge ports needed to represent a single interface in the the tenant vm.

The reason for linux _and_ ovs bridges being used together is related to security groups. The current implementation
of how security groups is enforced relies in the ip tables functionality. Trouble is, ip tables only work on interfaces
provided by linux bridges. While ovs is needed to handle the overlay/underlay encapsulation, the bridge ports are tied
with linux bridge ports to leverage the ip tables rules. As you can see in the output above, this makes for a bit of
a complicated world. I would not be surprised if that gets a re-visit and simplification in the near future. Looking
at solutions like [Opendaylight][odl] makes for an attractive alternative, but probably not as mature... yet. 

#### Peeking at the interfaces and bridges of the compute node 2 ####

Raw dump can be seen here <button class="toggle-start-hidden">Show/hide</button>

[gist:id=a160b91fee224cc4aae5]

Linux bridges and iptables in the compute 2 are here <button class="toggle-start-hidden">Show/hide</button>

[gist:id=3ecf11a250a11af5d449]

This is all very similar to compute 1; as expected.

### Looking at Packets ###

An interesting experiment would be to ping from tenant 1 to tenant 2 and
look at the packets at wireshark. The only possible way of doing that is
by using the floating ip address. To make it more fun -- and
hopefully not too confusing -- I'll ping across the vms that have the same
local ip address.

To have wireshark installed on any of the nodes, this is what you can do:
<button class="toggle">Show/hide</button>

    NODENAME='rdo-neutron'  ; # rdo-neutron used as an example

    vagrant ssh ${NODENAME}
    sudo su -
    ln -s /home/vagrant/.Xauthority /root/  ;  # link root's .Xauthority to vagrants'

    yum install -y wireshark xorg-x11-xauth xorg-x11-fonts-* xorg-x11-utils wireshark-gnome
    sed -i -e 's/#.*X11Forwarding\ no/X11Forwarding\ yes/'  /etc/ssh/sshd_config
    systemctl restart sshd.service
    exit  ;  # back to vagrant user
    exit  ;  # back to host. (In my case, my laptop)

    vagrant ssh ${NODENAME} -- -XY   ;  # the -- -XY matters, don't forget that!

    # Note: you can safely ignore the message that says:
    # /usr/bin/xauth:  file /home/vagrant/.Xauthority does not exist
    # That is so, because .Xauthority will be created now

    sudo wireshark &

There is a neat trick for looking at vxlan encapsulated packets. You can make wireshark
decode the inner packet by doing the steps shown in this [youtube link from David Mahler][dmahler]:

- filter capture display on **udp.port==4789**
- right click on one of the packets, and select **Decode as...**
- select **Destination -> 4789**
- on table shown on the right, select **VXLAN**
- click on **OK**


In order to get to the tenant vm, I used the neutron node. Any system attached to
the provider network should be able to do this.

These are the steps to get ping going from vm3 of tenant 2 to [floating ip of] vm3 of tenant 1
<button class="toggle-start-hidden">Show/hide</button>

[gist:id=cc9b2770ed619589bee5]

Looking at the wireshark packets, after decoding the VXLAN headers. Pay close attention
to the VNI values to keep track of the tenant boundaries.
<button class="toggle">Show/hide</button>

![topology](|filename|/images/openstack-vagrant-wireshark1.jpg)
![topology](|filename|/images/openstack-vagrant-wireshark2.jpg)

Hope this is useful. ;)
Enjoy and don't be shy to comment or ask me for clarification on anything that does not
make sense.

---
    
Some related links you may find interesting:

  * [OpenStack Installation Guide for Red Hat Enterprise Linux 7, CentOS 7, and Fedora 20](http://docs.openstack.org/juno/install-guide/install/yum/content/)
  * [Introduction to Cloud Overlay Networks - VXLAN -- David Mahler](http://youtu.be/Jqm_4TMmQz8)
  * [OpenStack Juno Scripted Install with Neutron on CentOS 7](http://behindtheracks.com/2014/11/openstack-juno-scripted-install-with-neutron-on-centos-7/)
  * [RDO: Multinode OpenStack using Packstack](http://youtu.be/DGf-ny25OAw?list=LL7CxI6QV3lwXTST4ophOSKA)
  * [Red Hat OpenStack Administration](http://www.redhat.com/en/services/training/cl210-red-hat-openstack-administration)

  [vagrant]: https://www.vagrantup.com/ "Get Vagrant"
  [vbox]: https://www.virtualbox.org/ "Get Virtual Box"
  [bento]: https://github.com/chef/bento "Bento project"
  [vmfusion]: http://www.vmware.com/products/fusion/ "VMware Fusion"
  [vagrantReload]: https://github.com/aidanns/vagrant-reload "Vagrant Reload Provisioner"
  [routerNode]: https://github.com/flavio-fernandes/router-node "Router Node"
  [routerNodeReadMe]: https://github.com/flavio-fernandes/router-node/blob/master/README.md "Router Node Read Me"
  [internalNetNameRtr]: https://github.com/flavio-fernandes/router-node/blob/master/Vagrantfile#L40 "Internal Network Name Router"
  [internalNetNameNeutron]: https://github.com/flavio-fernandes/rdo-nodes/blob/master/Vagrantfile#L53 "Internal Network Name Neutron" 
  [hostsJson]: https://github.com/flavio-fernandes/rdo-nodes/blob/master/puppet/hieradata/hosts.json "hosts.json"
  [sahara]: https://github.com/jedi4ever/sahara 
  [rdoVagrant]: https://github.com/flavio-fernandes/rdo-nodes/blob/master/Vagrantfile "rdo-nodes Vagrantfile"
  [dvr]: https://wiki.openstack.org/wiki/Neutron/DVR "Neutron DVR"
  [odll3]: https://wiki.opendaylight.org/view/OVSDB_Integration:L3Fwd "Opendaylight L3 forwarding feature"
  [odl]: http://www.opendaylight.org/software "Opendaylight"

  [dmahler]: http://youtu.be/Jqm_4TMmQz8?t=12m20s "Introduction to Cloud Overlay Networks - VXLAN -- David Mahler"
