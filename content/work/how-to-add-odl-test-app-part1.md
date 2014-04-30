Title: ODL module add part 1
Date: 2014-04-30 12:40
Author: flavio
Category: Work
Tags: test, sdn, opendaylight
Slug: how-to-odl-controller-module-part1

Adding a module to ODL controller part 1.

<!--more-->

# The Scenario

While coming up to speed on [OpenDayLight][] (aka ODL), I found many useful sites and demos. A particular one that helped me a lot is [SDNHub].
To illustrate the inner workings of ODL, the [SDNHub] tutorial provides a VM with all the need software installed. With help from [Chris], 
I took a few steps back from what is provided in the VM and learned how the folks in [SDNHub] create a self contained java project for the tutorial.

So, I thought of documenting how one could add a generic module to the ODL controller, without having to be part of the controller repository
itself. A second stage to this page would be to extend the newly added java module to do something with the [MD-SAL][] api. That will be explored
later, in part 2 of this series.

# Step 1: Getting started

* Get all the devel stuff you would need, as if you were going to develop code for [OpenDayLight][]:

Devel page:

    :::url
    https://wiki.opendaylight.org/view/GettingStarted:Developer_Main

***TO BE CONTINUED SOON...***

  [OpenDayLight]: http://www.opendaylight.org/
  [SDNHub]: http://sdnhub.org/tutorials/opendaylight/
  [Chris]: http://en.wikipedia.org/wiki/Chris_Wright_%28programmer%29
  [MD-SAL]: https://wiki.opendaylight.org/view/OpenDaylight_Controller:MD-SAL

