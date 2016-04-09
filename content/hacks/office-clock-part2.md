Title: Office Clock Project part 2: software
Date: 2016-04-05 16:48
Author: flavio
Category: Hacks
Tags: raspberryPi
Slug: office-clock-part2

Software for an led matrix display and led RGB strip DIY project

<!--more-->

As a [continuation of part1][part1], this page will cover the software
I put together and how I use it to bring the display alive. From here, you can learn
about the main components of the application, as well as a few examples that show how I
currently use it.
If you are feeling impatient, go ahead and grab the [code from Github][code].

By running the program, an embedded web server handles requests that may come
from my desktop or any other program that may wish to control the display. 
When the server is 'left alone' it will run as what I call _clock mode_. Motion
and light sensors help conserving energy by keeping tabs on how bright the room is, as
well as how long it has been since there has been any activity near the display. After a while of
nobody around, the
display changes to the _screen saver mode_, and it stays that way until motion is detected.
A third mode, called _message mode_, is when we can do fun things to the display.
You can put the unit in that mode by sending an html [POST][post] [call](#messagemodeinfo).
The web server also offers some very simple pages, in case you
do not want to fiddle with variables and values. More on that in the [section below](#runoclock).

![displayModes](|filename|/images/office-clock-modes.jpg)

While in _message mode_, there are a bunch of knobs you can set. They are divided into
3 parts, which I will get into, as I describe the [message mode](#messagemodeinfo) in more detail:

1. main message
1. background messages
1. background images


Analogous to the led matrix display, I also have a strip of RGB leds.
It provides a number of built in animations, as well as a way for encoding info
representing external states such as weather, number of unread emails, generic countdowns, etc.
The interface for controlling it is similar to the one for the led matrix; that is,
using a [REST][rest]-like interface.

But I'm getting ahead of myself...
I should start off by visiting the steps to get these bits in the [Raspberry Pi][rpi].


## Section 1: Software Pre-requisites

#### Prepare sd with Raspbian

Since I have no need for the desktop environment, I am using [Jessie Lite][raspbian].
There are many good pages that [explain how][getraspi] to install Raspbian, so I will briefly list
the main steps I took (using a Mac laptop):

Use "diskutil list" to find the disk that corresponds to the sd card to be used by your [RPI][rpi]

    :::bash
    $ diskutil list
    $ diskutil unmountDisk /dev/diskX  ; # replace X with the disk number

Download Raspbian from [https://www.raspberrypi.org/downloads/raspbian/][raspbian]
and unzip the image.
To make the filename shorter, let's rename it to **raspbian.img**

    :::bash
    $ unzip 20*raspbian-jessie-lite.zip
    $ mv 20*raspbian-jessie-lite.img raspbian.img
    $ sudo dd bs=1m if=./raspbian.img of=/dev/diskX  ; # replace X with the disk number

Typing ^T (CTRL-T) will give you an update how how many blocks have been written.
Jessie Lite is 1.3 Gb, so you will need about 1300 "records out". Be patient!
In my system, it took about 25 minutes (883 Kbytes/sec) to complete:

    :::bash
    $ sudo dd bs=1m if=./raspbian.img of=/dev/diskX
    1298+0 records in
    1298+0 records out
    1361051648 bytes transferred in 1541.171302 secs (883128 bytes/sec)

Eject disk after _dd_ is finished and use it to boot your [RPI][rpi]

    :::bash
    $ diskutil eject /dev/diskX  ; # replace X with the disk number

#### First time boot commands

- Login (user: pi password: raspberry)
- Run **'sudo raspi-config'** and do these:
    - _[optional]_ Select 'Advanced Options' -> 'Hostname'
    - Select 'Internationalisation Options' -> 'Change Timezone'
    - Select 'Expand Filesystem'
    - Select 'Finish' and reboot the rpi
- After reboot, login again and configure network, if needed
    - For info on configuring wifi, look for **Command line set up** [in this page][wifiopen].
        - If you are configuring wifi for an ssid that has no password (open),
          you basically need to <br/>**'sudo nano /etc/wpa_supplicant/wpa_supplicant.conf'** and add the
following to that file:

<pre>
  network={
     ssid="whatever"
     key_mgmt=NONE
  }
</pre>
   
- If your wifi is configured to not broadcast its ssid, make sure to add scan_ssid=1 and mode=0
as shown [below][gistwpa]

<pre>
$ sudo cat /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
 
network={
        ssid="whatever"
        psk="secret"
        scan_ssid=1
        mode=0
}
</pre>

- Don't forget that you will need to bounce wlan0 in order to have your changes take effect:

<pre>
sudo ifdown wlan0 && sudo ifup wlan0
</pre>

- Once you are connected to the internet, do an update to ensure you got the [latest][distupg]
and greatest packages.

Note that you may want to reboot after that, to potentially load new linux kernel

    :::bash
    $ sudo apt-get update ; sudo apt-get -y dist-upgrade
    $ sudo reboot

- Install git, libevent-devel, wiringPi

Once logged in again, there are just a few more pieces to be added to the [RPI][rpi].
I use a nice little web server implementation called [pulsar][pulsar], which is based in the [libevent][libevent]
[html][libeventhtml] framework. In order to control the GPIOs in the [RPI][rpi], I rely on the nice api provided by
[WiringPi][wiringpi]. All easy to install due to **apt-get** and **git**.
Life is good when you can ride on the [shoulder of giants][giants]. :)

    :::bash
    $ sudo apt-get install -y git libevent-dev

    $ cd someDir
    $ git clone git://git.drogon.net/wiringPi wiringPi.git
    $ cd wiringPi.git && ./build

- Download and compile the main application

As mentioned earlier, the source code is available at [Github][code]. In order to keep the info
in this page from going stale, I will be using the branch **rpi-0.1.y**, which I will not mess with.
Unless a nasty bug shows up. :)
I will talk more about the code itself in [section 3](#codenav).

    :::bash
    $ cd ; # not really important where, but oclock.service may need to be edited
    $ git clone -b rpi-0.1.y https://github.com/flavio-fernandes/oclock oclock.git
    $ cd oclock.git && make


With that finished, you are ready to rumble! The executable is called oclock (short for office clock):

      ~/oclock.git/oclock

As you will soon see, it is more than a clock, really. I must confess I'm not good with names. :)
The application provides a simple way of displaying any kind of information and images.
Since access to GPIO pins is privileged, the Makefile will make that executable
owned by root and set the [sticky bit][stickybit].

There are a few files that you may want to modify, depending on the GPIO pins
you end up using. I will cover that as I visit each component of the code, in the [code navigation section](#codenav).

<span id=runoclock />
## Section 2: Running oclock

It is very easy to make the application start automatically. More on that is explained in the
[section below](#systemd) (called _Make it a systemd service_).
Once it is running -- either by invoking **~/oclock.git/oclock** or starting the linux service -- you should be able
to interact with the display as I show in this section.

Perhaps one of easiest ways to see what you can do is by running the [stickManAnimation][stickManAnimation] script:

![stickMenAnimation](|filename|/images/office-clock-stick-men.jpg)

    :::bash
    $ # start program in background, if you have not already done so
    $ ~/oclock.git/oclock &

    $ # add some people to the dance floor :)
    $ ~/oclock.git/misc/stickManAnimation.sh

    $ # you can stop animation by typing ^C (CTRL-C)

    $ # if you started it above, you can stop oclock program by running killall
    $ killall oclock

Another really easy way, is by using the browser and connecting to the server running in the [RPI][rpi], as shown here:

    :::uri
    http://RPI_ADDRESS/msgMode

![helloMsgMode](|filename|/images/office-clock-hello-world.jpg)

It is actually easy to control the display from a shell prompt. For an example on how that is done, check out
these commands:

    :::bash
    $ RPI='192.168.2.236' ; # change this with the ip address of your rpi, or "localhost" if doing it from the rpi
    $ MSG='hello world'   ; # say hello
    $ TIMEOUT=10          ; # in seconds. 0 means forever
    $ X=10                ; # X coordinate in the display
    $ curl --request POST "http://${RPI}/msgMode" --data \
         "msg=${MSG}&noScroll=1&bounce=1&timeout=${TIMEOUT}&x=${X}"

There are more knobs you can tweak than the example above; but that should give you an idea of how to make it go.

<span id=messagemodeinfo />
### The message mode of the led matrix display

As mentioned earlier, while in **message mode** there 3 parts that you can tweak:

1. main message
1. background messages
1. background images

By the way, the code that serves the pages that provide these options is in [webHandlerInternal.cpp][webHandlerMsgMode].
The code that handles the options and make it happen is in [displayInternal.cpp][doHandleMsgModePost].

Let me talk a bit about each one of the 3 parts mentioned above.

#### Main Message ####

    :::uri
    http://${RPI}/msgMode

This represents the _main_ text you want displayed in the screen. When it comes to attributes, the sky
is the limit on what you can implement, but these are the ones I started with:

- **msg**: what characters to display
- **font**: font to use for the message text. That is [enumerated here][fontsEnum]
- **alternateFont**: as the text scrolls (or bounce) out, change the font used (boolean)
- **confetti**: use to sprinkle random dots around display. The biggest the value, the more dots (integer)
- **bounce**: indicate whether text has the jumping effect (boolean)
- **noScroll**: indicate whether text moves like a stock market ticker effect (boolean)
- **blink**: make it flash (boolean)
- **color**: the matrix display has leds that can go green and red. By turning both colors on we get yellow.
As the text scrolls or bounce, you can make the color change by selecting _alternate_.
That is [enumerated here][colorEnum]
- scroll **repeats**: similar to **timeout**, this gives a way of leaving _message mode_ after
the message scrolled by a finite number of times (integer)
- **timeout**: number of seconds until text is to end (can be infinite, if you set it to 0)
- **X** and **Y**: zero based coordinates of where text will start from. You can use negative values if you
want to crop from the left (or top)

#### Background Messages and Images ####

    :::uri
    http://${RPI}/msgBackground
    http://${RPI}/imgBackground

While in message mode, you can also _stamp_ text and images around the display. While there are separate
URLs for the text (i.e. message) and the image, they are very similar in terms of the parameters
you would provide:

- **index**: a zero based value to represent the text/image you are setting (integer)
- **msg or imgArt **: what characters to display (background message) or what to draw (background image)
- **enabled**: set this to false to not display the provided text/image index (boolean)
- **clear all**: set this to _true_ and all other text/image entries will be disabled and cleared (boolean)
- **color**: red, green or yellow. That is [enumerated here][colorEnum]
- **font**: font to use for the message text. This does not apply to image. That is [enumerated here][fontsEnum]
- **X** and **Y**: zero based coordinates of where text/image will start from. You can use negative values if you
want to crop from the left (or top)
- **animation**: see below.

One interesting caveat here is that these are only visible when display is in message mode, and that is
controlled by the _main message_ url we talked above. So, it is possible that you may want to set message mode
with an _empty_ **msg** attribute, so the display provides you with a clean canvas to draw upon. the
[stickMan animation][stickmanchange] example does exactly that, while taking advantage of the **confetti**
behavior.

##### Animation: speed, number of frames and frame id.

To provide the ability of animating the background msg and images, I came up with the idea of using multiple
**indexes** that can be orchestrated using 3 parameters. Let's say I want an animation that says: "this", then "is"
and then "fun". And I would like it to rotate every 500 milliseconds, and then an extra 500ms before starting over.
With that in mind, the parameters would look like this:

- **index:** 10 **msg:** this **animationStep:** 500ms **animationPhase:** 4 **animationPhaseValue:** 0 
- **index:** 11 **msg:** is   **animationStep:** 500ms **animationPhase:** 4 **animationPhaseValue:** 1
- **index:** 12 **msg:** fun  **animationStep:** 500ms **animationPhase:** 4 **animationPhaseValue:** 2 

The **index** -- as long as it's unique and within the number of [supported indexes][maxIndexes] -- is not important.
Animation step is actually an [enumerated type][enumAnimationStep] used to represent the frame rate.
In this case, 500ms is actually the [value 3][enumAnimationStep].
Animation phase is the number of entries you want in the animation (i.e. number of frames).
Since we need to introduce a 'blank' frame in the animation, we use the value of 4 (3 entries plus an empty phase value).
Lastly, we use **animationPhaseValue** to indicate _when_ each of the entries provided are to be shown in the
animation (i.e. frame id).

[These commands][animateExample] would do that trick:

    :::text
    RPI='192.168.2.236' ; # change this with the ip address of your rpi, or "localhost" if doing it from the rpi
    urlBase="http://${RPI}:80"
    urlImgBg="${urlBase}/imgBackground"
    urlMsgBg="${urlBase}/msgBackground"
    urlMsgMode="${urlBase}/msgMode"

    STEP=3  ; # 500ms
    PHASE=4 ; # four frames of animation

    curl --request POST  ${urlMsgBg}  --data 'clearAll=1'
    curl --request POST  ${urlMsgMode} --data 'timeout=120'  ; # enter message mode for 2 minutes

    ANIM_COMMON="enable=y&animationStep=${STEP}&animationPhase=${PHASE}"

    IDX=10; ANIM_VALUE=0
    curl --request POST  ${urlMsgBg}  --data "${ANIM_COMMON}&index=${IDX}&animationPhaseValue=${ANIM_VALUE}&msg=this"

    IDX=$((IDX + 1)); ANIM_VALUE=1
    curl --request POST  ${urlMsgBg}  --data "${ANIM_COMMON}&index=${IDX}&animationPhaseValue=${ANIM_VALUE}&msg=is"

    IDX=$((IDX + 1)); ANIM_VALUE=2
    curl --request POST  ${urlMsgBg}  --data "${ANIM_COMMON}&index=${IDX}&animationPhaseValue=${ANIM_VALUE}&msg=fun"


So, if we wanted to have an extra 500ms delay between each animation cycle, all that is needed would be to use PHASE=5.
Hopefully this will make sense to you. In my defense, this implementation allows for a lot of variations when doing animations.
To have some more fun, try playing with the background images instead of messages. For that,
the main difference is that you use the **[imgArt][enumImgArt]** instead of **msg**. That is a zero based list that can be found
[in this file][enumImgArt].

#### Postman

A handy tool for interacting with a device that responds to HTTP requests is called [Postman][postman].
I use that as an efficient way of testing various attributes and values for this program.
What is also great is that we can easily share a group of HTTP requests as a postman _collection_.
If you never used [Postman][postman], give it a try!
All in all, here is a collection you can use for interacting with the oclock application:

    :::uri
    https://www.getpostman.com/collections/f3117dd8a2924ede21cb

Or, you can also import from the [collection][postmanColl] and [environment][postmanEnv] files I added to the Github repo,
under the [misc][miscDir] directory.
Just make sure that **rpiAddr** and **rpiPort** are correct for your postman environment and you will be good to go.

Yet another way for getting this collection is by pressing on the orange looking button here:

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/f3117dd8a2924ede21cb#?env%5BofficeClock%5D=W3sia2V5IjoicnBpQWRkciIsInZhbHVlIjoiMTkyLjE2OC4yLjIzNiIsInR5cGUiOiJ0ZXh0IiwiZW5hYmxlZCI6dHJ1ZX0seyJrZXkiOiJycGlQb3J0IiwidmFsdWUiOiI4MCIsInR5cGUiOiJ0ZXh0IiwiZW5hYmxlZCI6dHJ1ZX1d)


<span id=systemd />
#### Make it a systemd service

To make this  application start automatically upon system boot, do the following
steps to make it known by systemd. First, edit the file **oclock.service**
so that the lines that read _ExecStart=.../oclock_ and _WorkingDirectory=_ are correct
for your [RPI][rpi]. Once that is done, copy it to the proper place and enable the service:

    :::bash
    $ nano ./misc/oclock.service
    $ sudo cp misc/oclock.service /lib/systemd/system/
    $ sudo systemctl enable oclock.service

You can start and check the status of the service by doing these commands:

    :::bash
    $ sudo systemctl start oclock.service
    $ sudo systemctl status oclock.service
   
You can always check if the server is running properly by sending some http requests to it:

    :::bash
    $ wget -O - -q -4 --spider http://localhost
    $ wget -q -O - http://localhost:80/status
    $ curl -X GET -o /dev/null -sL -w "%{http_code}" http://localhost 2>&1  ; echo ""

To stop application, any of these would work:

    :::bash
    $ wget -q -O - http://localhost/stop
    $ sudo systemctl stop oclock.service

If you want to stop it from starting automatically, disable it:

    :::bash
    $ sudo systemctl disable oclock.service


<span id=codenav />
## Section 3: Code Navigation

oclock code is written in c and c++11. Python would have been a good candidate, but I started off
with the need for porting some libraries in c++ and decided to keep the language somewhat homogenous.
Coming from my past experiences on developing for the Arduino platform, I am blown away with
the level of stability,
speed and memory I get while using the [RPI][rpi].
Having the ability to attach a debugger to the running process is
priceless. While I had some initial success in using Valgrind, I ran into a brick wall due to a
[known issue][vgbug]. Overall, I still find the [RPI][rpi] to be
awesome in handling the GPIO pins and giving
me a rock solid TCP/IP stack. Definitely a keeper. ;)

#### Led Matrix Display

One of the bigger chunks of the work was the porting of libraries from Arduino to [RPI][rpi]. The code I
used to handle the lower levels of the [led matrix][matrixmanual] comes from the
[HT1632 for Arduino][ht1632project] repo. One of the issues while doing the port had to do with the
bit shift operator (i.e. **>>**). For some reason, the Arduino CPU is okay with shifting values by negative
values, like **VAR = 0x123 >> -2**. [RPI][rpi] was not giving a compiler warning, yet a very different
result when performing that operation.
Even though I pushed the [changes into the Arduino repo][ht1632rpi],
I kept the HT1632 code embedded in the oclock as well, under the [ht1632][ht1632dir] directory.
The [interface exposed][ht1632h] from the HT1632 is pretty easy to understand. I would love to add
more to that someday. Something like "**drawLine(...)**", "**drawRectangle(...)**" and
"**drawCircle(...)**" could be useful. I have that in my todo list, but not at a high priority.

If you **were using fewer or more than 4 bicolor displays**, all you need to change is the
[NUM_OF_BICOLOR_UNITS][ht1632units] value. The place where you specify what GPIOs pins are
used for controlling the HT1632 are located in the [display.cpp][ht1632gpios] file.

If you look in the code, you will see that the HT1632 object is instantiated and handled by the
Display class, also in the [display.cpp][displayClass] file. There is a dedicated thread which is constantly
monitoring what changes need to be done to HT1632. While in _message mode_, every [fast tick][displayFastTick]
will cause the main message and all the background images/messages to be drawn. If that is not happening
fast enough for you, all that needs to be tweaked is the [timerTick::millisPerTick][timerTickFast] value.
No biggie! ;)
The speed of the [RPI][rpi] -- even with the 'little' Pi zero -- together with the "vast"
amounts of memory to hold the [shadow space][ht1632shadow] for the 4 bicolor displays was a great upgrade
from using Arduino boards.


#### Analog to Digital Converter (ADC)

As mentioned in [part 1][part1] of this blog, the [RPI][rpi]
does not have a native way of reading analog values, which is something I needed for fetching the
brightness level of the light sensor.

[Ladyada][ada] has an awesome video on youtube that [talks about ways of working around this limitation][analogread].
For the fun of it, I connected the photo resistor to an [MCP3002][mcp].
Thanks to [awesome resources][mcpblog], it was pretty easy to write a little c++ class to abstract
the reading of the 10 bit value from that chip. While I'm aware that there are already other implementations
for doing this (see [wiringPi MCP3002][wiringpiMcp]), I opted for a native c++ code and did not want to require
the use of [hardware SPI][hardwareSpi] pins. Using any available GPIO pin and performing the needed bit bangs works out
just fine.
Besides being a lot of fun to write, of course. :) The result of
that was the creation of the [mcp300x repo][mcpcode], which is small enough to make me go ahead and simply
duplicate it under the oclock repo as well.
That is under the [mcp300x directory][mcp300xdir] and to be fair, I needed to add an extra knob for using it in the
oclock context.
Specifically, I wanted a way of coordinating among all the threads of the code that use the GPIOs.
That is likely a non-issue, but for debugging sake it is good to ensure access atomicity among the bit bangers: HT1632,
LPD8806 and the MCP3002. Thus, I extended them to acquire a lock before they did any bit banging on the GPIO pins.
That mutex is provided to MCP300x upon its constructor, in the file [lightSensor.cpp][lightSensorMcptor].

To diminish the jitter in the values read by the MCP3002, the light sensor code keeps the [last N][lightSensorLastN]
reads from a [periodic interval][lightSensorInterval]. It then computes an average from that history
[on demand][ligthSensorAvg].

Lastly, I should mention that the place where you specify what GPIO pins are
used for controlling the MCP3002 are located in the [lightSensor.cpp][lightSensorgpios] file.

#### Embedded Web Server

In my quest for a web server code with a clean and small footprint
-- yet powerful enough to handle multiple connections --
I began browsing Github.
A quote I really like fits nicely in this context:

    :::text
    "Don't think outside the box, go box shopping" (Dan and Chip Heath; Made to Stick)

I found many [good candidates][webservers] but settled with [abhinavsingh/pulsar][pulsar]
due to a few reasons -- which reminded me of rule **7a** of [RFC 1925][rfc1925]

- small, but not too small
- easy to embed
- robust
- written in C (C++ would be fine too...)

Porting it over was trivial. After [addressing a couple of minor issues][pulsarpull], I had that running within the oclock
process. As it is written to be event driven, it spawns a few worker threads that handle http requests in parallel.
The working model is common: each worker thread registers itself as a [callback handler][pulsarworkercallback]
for the one listening socket created by the [server thread][pulsarservercode].
There are lots of good documentation on [libevent][libeventhtml], which made this server even easier to understand.
The worker thread executes a function called [handleRequest][workerhandlerequest],
which integrates with the rest of the c++ code, called [WebHandlerInternal][workerhandlerequest2].
Critical sections of that code are protected by using mutex or a [mailbox-like message queue][mailboxcode].

There are just a few parameters you can tweak:

- number of worker threads
- server's tcp port
- verbosity
- logfile

Look [here][pulsarargv] to see the parameters you can pass into it without having to recompile the program. Otherwise, just
edit [conf.h][pulsarconfh] and [pulsar.c][pulsarargv] to make some more permanent tweaks.

To keep it self contained but yet embedded in the oclock program, I added the
[Pulsar codebase in a directory by itself][pulsardir].
Not much more to say on that... it just works perfectly! Big thanks to [Abhinav][abhinavsingh] for putting that code
together. And to [libevent][libevent] as well. :)

#### Led Strip

Another [porting I did][ledstripcode] was to use the code that [Ladyada][ada] and [PaintYourDragon][paintYourDragon] wrote to
control a strip of RGB leds. That code -- [adafruit/LPD8806][adalpd8806] in Github -- was implemented to run in 2 different ways:
using hardware SPI or using _any GPIO_ pins.
Once again I decided going the _any GPIO_ route, since it is plenty fast
and gives us the freedom to use any pair of GPIO pins (clock and data). As I studied that code, I made some enhancements to
not do 'bit bang' for all the pixels on every refresh. Instead, I added a variable that keeps tabs on the
_[largest pixel][largestChangedLed]_
referenced since the last refresh (called _[LPD8806::show()][lpd8806show]_). The API is even simpler than the one
used by HT1632, so it was no big deal getting that working. In fact, I must confess I spent more time
playing with the RGB animations than actually coding this stuff. ;)

A thread in the program is allocated to control the entire strip. It ticks off on its own [timer][ledstriptick] and
will bit bang all the 3 bytes per pixel -- on all 240 pixels -- within a millisecond. It can do that non-stop
without breaking a sweat (no hardware SPI involved).

Like I mentioned before, the LPD8806 code is what does the real work here, and that has been embedded under the
[its own][lpd8806dir] directory. The c++ wrapper code that runs the ledStrip thread and 'owns' LPD8806 is located
in the file... you guessed it: [ledStrip.cpp][ledstripcpp]. ;) If you need to use different GPIO pins, look no further
than lines 16 and 17 of [that file][ledstripgpios].
It is also in there (line 15) where we specify the total number of LEDs in the strip.
Lastly, look at this [Github commit][ledstripBinCount] for the stepping stones on how to add a new animation.

#### Threads

Using threads, I separated the different functionalities of this program into their own corner:

- master timer tick
- led matrix display
- led strip
- light sensor
- motion sensor
- web server

These threads are known and dispatched by the main() function by using the [threadsMain.h][threadsMainh] file,
using a common [start function][threadMainFunction].

In order to share a common timer, we have the master timer tick thread which provides a [registry][timertickregistry]
API for all the threads that need to do something at a given interval. Special care is needed to stop the
timer tick last, so all threads can exit gracefully upon receiving the [terminate message][terminatemsg]. That
final message is sent after the pulsar server stops running; due to a [signal trap][webserversignal]. Such signal
may come externally, or artificially generated when handling the _[stop url][stophandler]_
([server_stop function is here][webserverstop]).

Another category of functionality -- for the lack of a better word -- is the **[inbox][mailboxcode]**. Through
that, all threads can asynchronously queue messages for each other, or
[broadcast][inboxbcast] whatever it deems important. The motion sensor thread, for instance, [uses the mailbox][motionevent]
to broadcast situations when motion detection starts or stops.

And that is pretty much all I got on the description of the code for making oclock do its thing! My hope is that
folks will not have trouble using/changing it for whatever purposes they can think of.

## Future enhancements

##### Led strip encoding

Probably on the top of my laundry list is the addition of a parser that can take a string of values to represent
a group of pixels and colors for the led strip. I already made the [html form able to provide][ledstriprawvalues]
expose that, but the code behind it is still absent. Sorry!
A step beyond this goal will be to have another set of values
to indicate what the pixels should become bright and dim in a loop on their on; like a heartbeat. And blink.
Adding animations is an endless and big ball of fun. :)

##### Sound

I did not get around to that yet, but we can easily add another thread in the program to handle requests
for playing mp3s or text synthesizer. With the [RPI][rpi], this is actually very easy to do, thanks to the
helpful blogs available, [like this one][synthesizer].

##### Add more images, fonts

Get creative and add more fonts and images!
[Gaurav][gaurav] wrote some nice [javascript][leddrawsrc] that generates the binary value
that represents the pixels selected.
I made a convenient place in my server where you can [just use it][leddrawpage].

![ledImageDraw](|filename|/images/office-clock-led-image-draw.jpg)

Start by deciding on the size.
Then, pixel dot away to your heart's content.
Once done, you can simply paste the generated string into a header file in
the [ht1632][ht1632dir] directory, tweak a few lines of the display code and recompile the program.
As a concrete example, look at the [Github commit][stickmanchange], where I added the stick man drawings.

##### Connecting from the Clouds

In a nutshell, the oclock program's purpose in life is to provide a "dumb" interface that lets smarter
things/people control the display and the led strip. Thus, showing the time and date is just a side job, really. ;)
These smart people/devices can delegate out on the details
of how the display works, and get what she/he/it needs by using simple http requests. 
I have actually written a controller program for doing that in [Erlang](http://www.erlang.org/),
but it was for a different "dumb" device. Playing with one for the oclock will be another blast of fun.

There is also room for having the oclock program integrate with [MQTT][mqtt] and send notifications about motion
detected, for instance. By subscribing to MQTT, we can offer an alternate way of controlling the display too.
Using [Adafruit.io][adaio] would be a nice and easy way to get going on that.

## Final thoughts

Hopefully this was useful and will inspire you to build an awesome "Office clock"; much better than what I got.
If I can clarify something that was not well described, don't be shy in reaching out to me. There are lots of
great resources out there for learning on how to DIY.
Adafruit's [learn][adalearn] and [Adafruit Pi Zero Contest videos][adavideos],
[Hackaday](https://hackaday.io/),
[Collins Lab](https://youtu.be/9cps7Q_IrX0?list=PL6F433DD9F964C78A) to name a very few.

Enjoy!



[part1]: http://www.flaviof.com/blog/hacks/office-clock-part1.html "Office Clock Project Blog part 1"
[code]: https://github.com/flavio-fernandes/oclock/tree/rpi-0.1.y "Office Clock Project Github (branch rpi-0.1.y)"
[post]: https://en.wikipedia.org/wiki/POST_%28HTTP%29 "html post"
[rest]: https://en.wikipedia.org/wiki/Representational_state_transfer "rest interface"
[wifiopen]: https://www.maketecheasier.com/setup-wifi-on-raspberry-pi/ "Raspbian WIFI config"
[gistwpa]: https://gist.github.com/anonymous/821e36c79c00e88b83f10e984c9aee41/ "wpa_supplicant.conf"
[distupg]: http://askubuntu.com/questions/194651/why-use-apt-get-upgrade-instead-of-apt-get-dist-upgrade "dist-upgrade"
[stickybit]: https://en.wikipedia.org/wiki/Sticky_bit "Sticky bit"
[rpi]: https://www.raspberrypi.org/ "Raspberry Pi"
[raspbian]: https://www.raspberrypi.org/downloads/raspbian/ "Raspbian Download"
[getraspi]: http://lmgtfy.com/?q=install+raspbian+jessie+lite "Installing raspbian"
[pulsar]: https://github.com/abhinavsingh/pulsar "Pulsar web server"
[libevent]: https://www.monkey.org/~provos/libevent/doxygen-2.0.1/index.html "libevent Documentation"
[libeventhtml]: https://www.monkey.org/~provos/libevent/doxygen-2.0.1/http_8h.html "include/event2/http.h File Reference"
[wiringpi]: http://wiringpi.com/ "WiringPi"
[giants]: http://www.aerospaceweb.org/question/history/q0162b.shtml "If I have seen further it is by standing on the shoulders of giants."
[stickManAnimation]: https://raw.githubusercontent.com/flavio-fernandes/oclock/rpi-0.1.y/misc/stickManAnimation.sh  "stickManAnimation.sh"
[gaurav]: https://github.com/gauravmm "Gaurav Manek"
[leddrawsrc]: https://github.com/flavio-fernandes/HT1632-for-Arduino/blob/master/Utilities/Image%20drawing/LED_image_drawing_utility.html "Led Matrix Utility Raw"
[leddrawpage]: http://www.flaviof.com/ledMatrixUtillity/ "Led Matrix Utility"
[ht1632dir]: https://github.com/flavio-fernandes/oclock/tree/rpi-0.1.y/ht1632 "oclock/ht1632/ directory"
[stickmanchange]: https://github.com/flavio-fernandes/oclock/commit/d43a7cf83768c8a83fa46962d94925e0e2d56b73 "add stickMan picture and test script"
[webHandlerMsgMode]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/webHandlerInternal.cpp#L488 "WebHandlerMsgMode"
[doHandleMsgModePost]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/displayInternal.cpp#L856 "doHandleMsgModePost"
[fontsEnum]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/displayTypes.h#L14 "Fonts enumerator"
[colorEnum]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/displayTypes.h#L7 "Colors enumerator"
[maxIndexes]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/displayTypes.h#L64 "Max background values"
[enumAnimationStep]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/displayTypes.h#L28 "Animation Step enum, 500ms"
[animateExample]: https://gist.githubusercontent.com/anonymous/6a4ac9b09e30c3f414b24ce13e2a3209/raw/351c94db94c5819331ece2ec17cc9d59a1023dae/gistify62565.txt "Animation Example gist"
[enumImgArt]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/displayTypes.h#L34 "enum image art"
[postman]: https://www.getpostman.com/ "Postman"
[postmanColl]: https://raw.githubusercontent.com/flavio-fernandes/oclock/rpi-0.1.y/misc/officeClock.json.postman_collection "Postman Collection"
[postmanEnv]: https://raw.githubusercontent.com/flavio-fernandes/oclock/rpi-0.1.y/misc/officeClock.postman_environment "Postman Environment"
[miscDir]: https://github.com/flavio-fernandes/oclock/tree/rpi-0.1.y/misc ".../misc"
[synthesizer]: https://learn.adafruit.com/speech-synthesis-on-the-raspberry-pi/introduction "Speech Synthesis on the Raspberry Pi"

[vgbug]: https://bugs.kde.org/show_bug.cgi?id=322935 "Valgrind issue in RPI"
[matrixmanual]: http://store3.sure-electronics.com/de-dp14211 "3216 Bicolor Red and Green LED"
[ht1632project]: https://github.com/flavio-fernandes/HT1632-for-Arduino "HT1632 for Arduino"
[ht1632rpi]: https://github.com/flavio-fernandes/HT1632-for-Arduino/commit/eb86caf5f988b4ab9c237981c95b8ac80871876c "Porting HT1632 to RPI"
[ht1632h]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/ht1632/HT1632.h#L161 "HT1632.h"
[ht1632units]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/ht1632/HT1632.h#L23 "NUM_OF_BICOLOR_UNITS"
[ht1632gpios]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/display.cpp#L14 "HT1632 GPIO pins"
[displayClass]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/display.cpp#L160 "HT1632 instantiation"
[displayFastTick]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/display.cpp#L137 "Display fast tick"
[timerTickFast]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/timerTick.cpp#L21 "TimerTick::millisPerTick"
[ht1632shadow]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/ht1632/HT1632.cpp#L113 "Shadow memory used for bicolor display"
[ada]: https://en.wikipedia.org/wiki/Limor_Fried "Limor"
[paintYourDragon]: http://www.paintyourdragon.com/ "Phillip Burgess"
[analogread]: https://youtu.be/xhnUXJ9w2XQ?t=3m39s "Analog on Raspberry Pi"
[mcp]: http://www.digikey.com/short/38q81t "Microchip Technology MCP3002-I/P"
[mcpblog]: https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/ "Analog Inputs for Raspberry Pi"
[wiringpiMcp]: http://git.drogon.net/?p=wiringPi;a=blob;f=wiringPi/mcp3002.c;h=8e191b6225fab8cabb82b3636c66a6bc61513c53;hb=HEAD "wiringPi mcp3002"
[hardwareSpi]: https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md#hardware "RPI hardware SPI"
[mcpcode]: https://github.com/flavio-fernandes/mcp300x "c++ codebase to control analog to digital converter in Raspberry Pi"
[mcp300xdir]: https://github.com/flavio-fernandes/oclock/tree/rpi-0.1.y/mcp300x "mcp300x dir"
[lightSensorMcptor]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/lightSensor.cpp#L100 "mcp300x constructor by lightSensor class"
[lightSensorLastN]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/lightSensor.cpp#L11 "light sensor value history"
[lightSensorInterval]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/lightSensor.cpp#L91 "light sensor read interval"
[ligthSensorAvg]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/lightSensor.cpp#L79 "Light sensor average calculation"
[lightSensorgpios]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/lightSensor.cpp#L12 "MCP3002 GPIO pins"
[webservers]: https://gist.github.com/caa9f8dea249ad53c3bd221cd65bbe39 "Web server candidates"
[rfc1925]: http://www.faqs.org/rfcs/rfc1925.html "The Twelve Networking Truths"
[pulsarpull]: https://github.com/abhinavsingh/pulsar/pull/1 "Pulsar minor fixes"
[pulsarworkercallback]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/pulsar/worker.c#L76 "Pulsar worker callback"
[pulsarservercode]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/pulsar/server.c#L116 "Pulsar Server"
[workerhandlerequest]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/webHandlerInternal.cpp#L36 "Pulsar Worker Handle Request"
[workerhandlerequest2]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/webHandlerInternal.cpp#L254 "WebHandlerInternal"
[mailboxcode]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/inbox.h "oclock inbox codebase"
[pulsarconfh]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/pulsar/conf.h#L14 "Pulsar conf.h"
[pulsarargv]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/pulsar/pulsar.c#L22 "Pulsar params"
[abhinavsingh]: https://github.com/abhinavsingh "Abhinav Singh"
[pulsardir]: https://github.com/flavio-fernandes/oclock/tree/rpi-0.1.y/pulsar "Pulsar Directory in oclock codebase"
[ledstripcode]: https://github.com/adafruit/LPD8806/pull/19 "Github adafruit/LPD8806"
[adalpd8806]: https://github.com/adafruit/LPD8806 "adafruit/LPD8806"
[largestChangedLed]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/lpd8806/LPD8806.h#L32 "Led Strip: largest pixel"
[lpd8806show]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/lpd8806/LPD8806.cpp#L85 "LPD8806::show()"
[ledstriptick]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/ledStrip.cpp#L149 "LedStrip timer Tick"
[lpd8806dir]: https://github.com/flavio-fernandes/oclock/tree/rpi-0.1.y/lpd8806 "LPD8806 directory"
[ledstripcpp]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/ledStrip.cpp#L140 "ledStrip.cpp"
[ledstripgpios]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/ledStrip.cpp#L14 "ledStrip GPIO pins"
[ledstripBinCount]: https://github.com/flavio-fernandes/oclock/commit/4c1fdc434b9bd69f0de3e7c8044c4f1400fc38ed "Example on adding led strip animation: 64 bit binary counter"

[threadsMainh]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/threadsMain.h "threadsMain.h"
[threadMainFunction]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/main.cpp#L29 "thread function pointer"
[timertickregistry]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/timerTick.h#L73 "TimerTick registry"
[terminatemsg]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/main.cpp#L69 "Termination Message" 
[webserversignal]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/pulsar/server.c#L100  "Web server signal handler"
[stophandler]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/webHandlerInternal.cpp#L702  "Web Server Stop URL handler"
[webserverstop]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/pulsar/server.c#L131 "Web Server Stop Code"
[inboxbcast]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/inbox.cpp#L121 "Inbox Broadcast" 
[motionevent]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/motionSensor.cpp#L115 "Motion Event Broadcast"
[ledstriprawvalues]: https://github.com/flavio-fernandes/oclock/blob/rpi-0.1.y/src/webHandlerInternal.cpp#L647 "Parsing discrete values on led strip"
[mqtt]: http://mqtt.org/ "mqtt"
[adaio]: https://learn.adafruit.com/mqtt-adafruit-io-and-you/overview "Adafruit.io"
[adalearn]: https://learn.adafruit.com/ "Adafruit Learn"
[adavideos]: https://hackaday.io/contest/9326/logs "Adafruit Pi Zero Contest"
