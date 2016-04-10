Title: Office Clock Project part 1: hardware 
Date: 2016-03-28 16:48
Author: flavio
Category: Hacks
Tags: raspberryPi
Slug: office-clock-part1

Hardware for a Led Matrix Display and Led RGB Strip DIY Project

<!--more-->

I decided to build a led matrix based display for my home office.
So after quitting my job, I took the luxury of not looking for a new one.
Instead, I began the fun packed adventure of _do it yourself_ (DIY) electronics!
As I will soon need to get a real job, I thought of blogging what I built, to hopefully
inspire whoever may be interested in building something similar. Note: quitting
your job is _not_ a requirement! :)

I have played with Arduinos a bunch before. While they will
always have a special place in my heart, I made the switch to using something
much more powerful and cheaper: Raspberry Pi (aka RPI). With that, a big chunk of
my project on the software side involved porting the Arduino based code
to work under the RPI. I will talk more about that in the [part 2][part2] of this blog.
For this portion, I will focus on the hardware I cobbled together and provide you
with some pictures for setting the context.

![clockFrontView](|filename|/images/office-clock-front-view.jpg)

For starters, let me begin with a list of the main components used, and then elaborate
a little on each one.

#### Ikea BRIMNES [Wall Cabinet][ikea]

<IMG SRC="/blog/images/office-clock-cabinet.jpg" ALT="cabinet" WIDTH=90 HEIGHT=90 BORDER=0>

    :::uri
    http://www.ikea.com/kw/en/catalog/products/40218078/
    BRIMNES Wall cabinet with sliding door, white -- KD 9 
    Article Number : 402.180.78

This is the structure I'm using for holding it all together. In order to attach the
display and the sensors, my super duper wife helped me out by cutting a perfect rectangle
out of the back of the cabinet.
By swapping the sliding door with the back panel we can create a perfect front.
The back piece is a lot slimmer, thus easier to cut.
For doing the cutting, she used an oscillating tool like the [DeWalt Oscillating saw][dewalt] DWE315K.
Still, I think that with a cutting knife [and patience] one can do that job as well.
The dimensions of the cutout for the display are 20 and 5/16, by 2 and 5/8 inches.

As you can see in the picture above, I used the holes that came with the back panel to hold the light and
motion sensors. For the motion sensor, the squared cutout is 7/8th of an inch.

In the near future, we will tape around the edges to make the display and the panel seamless.

#### Led Strip (and power adapter)

<div style="height:90px;">
<IMG SRC="/blog/images/office-clock-led-strip.jpg" ALT="ledStrip" WIDTH=90 HEIGHT=90 BORDER=0>
<IMG SRC="/blog/images/office-clock-led-strip-power.jpg" ALT="ledStripPower" WIDTH=90 HEIGHT=90 BORDER=0>
</div>

I plan on stretching a long and animated line of RGBs across the wall where the office clock will
be located. For that, I got a 5 meter reel of the [LPD8806 from Adafruit][ledstrip]. To power that, I
am using a 5 volts, 10 amp switching [power supply][ledstrippower]. You can use a smaller -- or no --
strip, of course.

In order to control the strip with a RPI using c++, I did small
[tweaks to the code that Ladyada and PaintYourDragon wrote][ledstripcode].
More on that when we cover the [software piece][part2].

#### 4x Bicolor Led Matrix Display (and power adapter)

<div style="height:120px;border:0">
<IMG SRC="/blog/images/office-clock-led-matrix.jpg" ALT="ledMatrix" WIDTH=120 HEIGHT=120 BORDER=0>
<IMG SRC="/blog/images/office-clock-led-strip-power.jpg" ALT="ledStripPower" WIDTH=90 HEIGHT=90 BORDER=0>
</div>

After considering a couple of options, I ended up using a daisy chain of four [32x16 bicolor displays][matrix],
from [Sure Electronics][sure].
I really liked the price of them on Ebay, which is a lot cheaper than the price in their official website. Go figure!
Another reason that made me go for this display is the fact that I got it working with an Arduino in the past, so I have a good
handle on porting [that code][matrixcode] to the RPI. More on that in the [part 2][part2] of this blog.

By the way, there is nothing magical about 4 here. You can can go as small as 1 and all that means is that you will
get fewer pixels to play with. I will certainly not judge. ;)

Just like the led strip, you will need to have a dedicated 5 volts power adapter to feed the led matrix. I started off
by using a [cheap-o adapter][badacdc] off of Ebay and that turned out to be a mistake. The thing was outputting more
than 5 volts and I failed to notice that before **destroying one of my matrix boards. @#$%#!!!** :( I guess I'm
lucky that only one was damaged; to look at it from the bright side. Anyways... what I use now
is a [VSK-S10-5UA][matrixpower], which can handle up to 2 amps. I bought that at [Digi-Key][digikeyMatrixPower].
According to the [matrix manual][matrixmanual], the max usage of a single board is 1.37 amps, so I will likely run into
trouble when attempting to light up all leds on 100% PWM duty cycle. A better idea may be to get a [power adapter
similar][ledstrippower] to the one used by the led strip. Thus, do what I say -- not what I do on that one. :)

#### Raspberry Pi and case (plus power adapter)

<div style="height:100px;border:0">
<IMG SRC="/blog/images/office-clock-pi-zero.jpg" ALT="piZero" WIDTH=120 HEIGHT=120 BORDER=0>
<IMG SRC="/blog/images/office-clock-zero-case.jpg" ALT="zeroCase" WIDTH=90 HEIGHT=90 BORDER=0>
<IMG SRC="/blog/images/office-clock-pi-power.jpg" ALT="piPower" WIDTH=90 HEIGHT=90 BORDER=0>
</div>

I think any model of the RPI can be used for this project. In this case, I am using the RPI zero because that is
the cheapest and I was lucky enough to find one [available at Adafruit][rpizerokit].
As I will talk about later on, I use a simple web server to handle rest-like calls and cause interesting things to
occur.
In order to better protect the RPI from my greasy fingers, I also bought a [protector case][zerocase] for it.

#### Micro SD Memory Card

<IMG SRC="/blog/images/office-clock-micro-sd.jpg" ALT="microSd" WIDTH=90 HEIGHT=90 BORDER=0>

The card I'm using came as part of the [kit that I bought at Adafruit][rpizerokit]. Its is 8Gb and made by
[Sandisk][ssd].

#### USB Hub

<IMG SRC="/blog/images/office-clock-usb-hub.jpg" ALT="usbHub" WIDTH=90 HEIGHT=90 BORDER=0>

This is something you may only need when using a RPI zero. In my case, I had an [old USB 2.0 hub][usbhub] from Belkin that works just fine.
One good thing about the hub I'm using is that it has its own power supply, which makes it less taxing on the power used by the RPI.

#### WIFI Dongle

<IMG SRC="/blog/images/office-clock-wifi.jpg" ALT="wifi" WIDTH=90 HEIGHT=90 BORDER=0>

The wifi dongle I'm using can be [bought at Adafruit][wifidongle] as well. Since I'm using a RPI zero, I have it
attached to the usb hub.

#### USB Audio Adapter 

<IMG SRC="/blog/images/office-clock-usb-audio.jpg" ALT="usbAudio" WIDTH=90 HEIGHT=90 BORDER=0>

Another item that you would only need if you are using a RPI zero. This is also something you [can get at Adafruit][audiousb]. There
are [other ways that Ladyada beautifully explains][audiochoices] in regards to getting audio from RPI zero. I chose this
path because it seemed the easiest for what I intend to do. To be honest, I'm yet to write the code that handles audio, but I
think that should work. ;)

#### Audio Speakers

<IMG SRC="/blog/images/office-clock-speakers.jpg" ALT="speakers" WIDTH=90 HEIGHT=90 BORDER=0>

A simple set of speakers that hooks up to the USB based audio adapter or the RPI (if you are not using a RPI zero).
I just purchased [these from AmazonBasics][speakers] for 14 bucks.

#### PIR Motion

<IMG SRC="/blog/images/office-clock-pir.jpg" ALT="pir" WIDTH=90 HEIGHT=90 BORDER=0>

I wanted a way of detecting when there is nobody around, so the clock can go on power saver mode. For that, I
attached a [PIR motion sensor][pir]. Hooking it up is quite simple, as I will show down below.

#### Light Sensor

<IMG SRC="/blog/images/office-clock-photo-resistor.jpg" ALT="photoResistor" WIDTH=90 HEIGHT=90 BORDER=0>

As yet another way of saving power, I wanted the ability to see how bright the room is, so I can adjust the intensity
of the LEDs (aka PWM duty cycle). For that, I use a simple [photo resistor][photocell]. A caveat here is that the RPI
does not have a native way of reading analog values, which is something needed to work with this sensor.
[Ladyada has an awesome video on youtube that talks about ways of working around this limitation][analogread].
For the fun of it, I connected the photo resistor to an [MCP3002][mcp], listed below.

#### Analog Reader (MCP3002)

<IMG SRC="/blog/images/office-clock-mcp3002.jpg" ALT="mcp3002" WIDTH=90 HEIGHT=90 BORDER=0>

As a way of providing an 10 bit value that represents the analog 'intensity' of the light from the light sensor, this chip
offers 2 input and SPI (with data output) pins that can interface with the Raspberry Pi.
I will go on more details on how that works in [part 2][part2] of this blog. 
I only need one analog input, so I actually connected the 2 input pins to the same photo resistor. With that, the code reads
from the 2 pins and take an simple average.
You can use the version of this chip that offers 8 analog inputs (ie [MCP3008][mcp3008]), but that
felt like too much of a waste for this project, so I bought the 2 pin version [from Digi-Key][mcp].

Thanks to [awesome resources][mcpblog] on this chip, it was pretty easy to write a little c++ program to have
the [RPI talking to this chip][mcpcode]. Sorry for sounding like a broken record, but there is more on that
code in [part 2][part2] of this blog.

#### Small Breadboard

<IMG SRC="/blog/images/office-clock-bread-board.jpg" ALT="breadBoard" WIDTH=90 HEIGHT=90 BORDER=0>

Given my poor dexterity in handling a soldering iron, I rather go for the breadboard whenever possible. :) On that account,
I needed a vessel to hold the MCP3002 as well as the [Cobbler Plus][cobbler]. These are very easy to find, including the one
at the [Adafruit shop][bread].

#### Raspberry Pi GPIO Breakout

<IMG SRC="/blog/images/office-clock-cobbler.jpg" ALT="cobbler" WIDTH=120 HEIGHT=120 BORDER=0>

The easiest way to hook the GPIO (aka General Purpose Input/Output) is by using one of [these breakouts][cobbler].
The one sold by Adafruit already comes with a 40 pin cable.

#### Power Strip, Wires, etc

<div style="height:120px;border:0">
<IMG SRC="/blog/images/office-clock-power-strip.jpg" ALT="powerStrip" WIDTH=120 HEIGHT=120 BORDER=0>
<IMG SRC="/blog/images/office-clock-wires.jpg" ALT="wires" WIDTH=120 HEIGHT=120 BORDER=0>
<IMG SRC="/blog/images/office-clock-yoyo.jpg" ALT="yoyo" WIDTH=120 HEIGHT=120 BORDER=0>
<IMG SRC="/blog/images/office-clock-glue-gun.jpg" ALT="glueGun" WIDTH=120 HEIGHT=120 BORDER=0>
</div>

As you can see in the pictures, I connected all the power supplies to a simple [power strip][powerStrip].
To help myself with the soldering iron phobia, I used a couple of [Phantom Yoyo][yoyo] wires to hookup the
displays to the breadboard.
I also used [22 AWG core wires][wires] to daisy chain the power for the led matrix displays,
as well as extending the connections from the sensors to the breadboard.
To bond the pieces together -- such as the display panels, sensors and breadboard -- I used a simple [hot glue gun][glue].

## Pictures and Hookup Diagrams

I took a bunch of pictures while doing this project and uploaded them to Flickr. **[Click here][flickr] to see them.**

#### Motion and Light Sensors

![diagSensors](|filename|/images/office-clock-diag-sensors.jpg)

#### Led Strip

![diagLedStrip](|filename|/images/office-clock-diag-led-strip.jpg)

#### Led Matrix Display

![diagLedMatrix](|filename|/images/office-clock-diag-led-matrix.jpg)

#### USB Hub Devices

![diagUsb](|filename|/images/office-clock-diag-usb.jpg)


[ikea]: http://www.ikea.com/us/en/images/products/brimnes-wall-cabinet-with-sliding-door__0107522_PE257204_S4.JPG
[ikea2]: http://www.ikea.com/kw/en/catalog/products/40218078/ "BRIMNES Wall cabinet with sliding door"
[dewalt]: http://www.dewalt.com/tools/woodworking-oscillating-tools-dwe315k.aspx "Oscillating Multi-Tool Kit"
[rpizerokit]: https://www.adafruit.com/products/2816 "Raspberry Pi Zero Starter Pack"
[zerocase]: https://www.adafruit.com/products/2883 "Adafruit Pi Protector for Raspberry Pi Model Zero"
[ssd]: https://www.adafruit.com/product/2692 "8GB Class 10 SD/MicroSD Memory Card"
[wifidongle]: https://www.adafruit.com/products/814 "Miniature WiFi (802.11b/g/n) Module"
[usbhub]: http://smile.amazon.com/dp/B000TTTJ36 "Belkin 2 in 1 USB 2.0 7-PORT HUB"
[audiousb]: https://www.adafruit.com/products/1475 "USB Audio Adapter"
[audiochoices]: https://youtu.be/3gW3tPCTsiQ?t=3m52s "Ladyada talking audio output"
[speakers]: http://smile.amazon.com/dp/B00GHY5F3K "AmazonBasics USB Powered Computer Speakers"
[matrixpower]: http://www.cui.com/product/resource/vsk-s10-series.pdf "CUI AC-DC POWER SUPPLY"
[digikeyMatrixPower]: http://www.digikey.com/product-detail/en/cui-inc/VSK-S10-5UA/102-2392-ND/2718953 "CUI Inc. VSK-S10-5UA"
[ledstrip]: https://www.adafruit.com/products/306 "Digital RGB LED Weatherproof Strip"
[ledstripcode]: https://github.com/adafruit/LPD8806/pull/19 "github adafruit/LPD8806"
[ledstrippower]: https://www.adafruit.com/products/658 "5V 10A switching power supply"
[matrix]: http://r.ebay.com/W4m1js "P4 32X16 3216 RG Dual Color LED Led Matrix Unit Display Board"
[matrixcode]: https://github.com/flavio-fernandes/HT1632-for-Arduino/commit/eb86caf5f988b4ab9c237981c95b8ac80871876c "Dual Color LED Led Matrix code"
[matrixmanual]: http://store3.sure-electronics.com/de-dp14211 "3216 Bicolor Red and Green LED"
[sure]: http://store3.sure-electronics.com/ "Sure Electronics"
[badacdc]: http://r.ebay.com/VPzPEB "Bad AC Adapter -- DO NOT USE!"
[pir]: https://www.adafruit.com/products/189 "PIR (motion) sensor"
[photocell]: https://www.adafruit.com/products/161 "Photo cell (CdS photoresistor)"
[analogread]: https://youtu.be/xhnUXJ9w2XQ?t=3m39s "Analog on Raspberry Pi"
[mcp]: http://www.digikey.com/short/38q81t "Microchip Technology MCP3002-I/P"
[mcp3008]: https://www.adafruit.com/products/856 "MCP3008 - 8-Channel 10-Bit ADC With SPI Interface"
[mcpcode]: https://github.com/flavio-fernandes/mcp300x "c++ codebase to control analog to digital converter in Raspberry Pi"
[mcpblog]: https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/ "Analog Inputs for Raspberry Pi"
[bread]: https://www.adafruit.com/products/65 "Tiny breadboard"
[cobbler]: https://www.adafruit.com/products/2029 "Assembled Pi Cobbler Plus - Breakout Cable - for Pi B+/A+/Pi 2/Pi 3"
[pics]: http://example.com/ "Office clock project pictures"
[powerStrip]: http://www.walmart.com/c/kp/power-strips "Power Strips"
[yoyo]: http://smile.amazon.com/dp/B00CTQ8PVY "Phantom YoYo 40p Dupont Cable Male to Female"
[wires]: https://www.adafruit.com/products/1311 "Hook-up Wire Spool Set"
[glue]: http://www.walmart.com/c/kp/hot-glue-guns "Hot Glue Guns"
[flickr]: https://flic.kr/s/aHskxgSqtB "Office Clock Project"
[part2]: http://www.flaviof.com/blog/hacks/office-clock-part2.html "Office Clock Project Blog part 2"
