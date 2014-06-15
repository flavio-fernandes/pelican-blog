Title: ODL basic MD-SAL reference
Date: 2014-05-25 10:00
Author: flavio
Category: Work
Tags: work, sdn, opendaylight
Slug: how-to-odl-basic-md-sal-ref

Reference and comments on doing ping MD-SAL in OpenDayLight.

<!--more-->

As part of digging deeper into [OpenDayLight][1], I spent some time looking at the [MD-SAL][2] piece.
My original plan was to provide tutorials on that, but folks have already been doing a wonderful job
on that. See [here for links on MD-SAL tutorials][5].

So what I did instead, was to play with an example that is small and simple: [the ping tutorial][3]:

    :::url
    https://wiki.opendaylight.org/view/Ping

Since ping is just a tutorial, the code is not checked into the controller codebase. However, it was
made to be embedded in the controller repo. So, in case you feel lazy and don't feel like typing, you can
simply pull it off of gerrit, after [cloning the controller repo][4].

    :::bash
    # ref link: https://git.opendaylight.org/gerrit/#/c/6991/

    cd controller.git
    git fetch https://git.opendaylight.org/gerrit/controller refs/changes/91/6991/2 && git checkout FETCH_HEAD

After finished with that tutorial, I played a little more with the use of the **Future<> RPC** used in [MD-SAL][2].
I wanted to make the ping code able to continuously probe multiple destinations. So I enhanced the code to be async by
doing [this](https://git.opendaylight.org/gerrit/gitweb?p=controller.git;a=commit;h=e936e98189184f4d1268b89b040ca558d8e805c4):

    :::bash
    # ref link: https://git.opendaylight.org/gerrit/#/c/6992/2/    (Patch set 2)

    cd controller.git
    git fetch https://git.opendaylight.org/gerrit/controller refs/changes/92/6992/2 && git checkout FETCH_HEAD

    # Examples using async ping (based on patch set 2):
    for x in 127.0.0.1 128.0.0.1 192.168.1.1 ;
       do curl --user "admin":"admin" -X PUT http://localhost:8080/controller/nb/v2/ping/async/start/${x} ; echo ; done
    while : ; do for x in 127.0.0.1 128.0.0.1 192.168.1.1 ;
       do curl --user "admin":"admin" -X PUT http://localhost:8080/controller/nb/v2/ping/async/get/${x} ; echo ; done ; sleep 2 ; done
    for x in 127.0.0.1 128.0.0.1 192.168.1.1 ;
       do curl --user "admin":"admin" -X PUT http://localhost:8080/controller/nb/v2/ping/async/stop/${x} ; echo ; done

After a few comments from Devin and Rob, I made my changes simpler by removing the need for the extra thread and the concurrent map.
That removed the background capability of the ping implementation. But simpler is always better, especially in a tutorial arena. Those
simplifications are stored as the [latest patch set](https://git.opendaylight.org/gerrit/gitweb?p=controller.git;a=commit;h=76d8a66814be207ade5e4cba867a21bb5e06054a):

    :::bash
    # ref link: https://git.opendaylight.org/gerrit/#/c/6992/

    cd controller.git
    git fetch https://git.opendaylight.org/gerrit/controller refs/changes/92/6992/4 && git checkout FETCH_HEAD

<span id=few_good_links/>
A few good [links][5] for learning/using MD-SAL in [ODL][1]:

    :::url
    https://wiki.opendaylight.org/view/OpenDaylight_Controller:MD-SAL#MD-SAL_and_ODL_App_Tutorials

  [1]: http://www.opendaylight.org/
  [2]: https://wiki.opendaylight.org/view/OpenDaylight_Controller:MD-SAL
  [3]: https://wiki.opendaylight.org/view/Ping
  [4]: https://wiki.opendaylight.org/view/OpenDaylight_Controller:Pulling,_Hacking,_and_Pushing_the_Code_from_the_CLI
  [5]: https://wiki.opendaylight.org/view/OpenDaylight_Controller:MD-SAL#MD-SAL_and_ODL_App_Tutorials
