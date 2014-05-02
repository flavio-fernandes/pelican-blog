Title: ODL module add part 1
Date: 2014-04-30 12:40
Author: flavio
Category: Work
Tags: work, sdn, opendaylight
Slug: how-to-odl-controller-module-part1

Adding a module to ODL controller part 1.

<!--more-->

# The Scenario

While coming up to speed on [OpenDayLight][] (aka ODL), I found many useful sites and demos. A particular one that helped me a lot is [SDNHub].
To illustrate the inner workings of ODL, the [SDNHub] tutorial provides a VM with all the need software installed. With help from ODL developers, 
I took a few steps back from what is provided in the VM and learned how the folks at [SDNHub] create an [OSGI] bundle for the tutorial.

So, I thought of documenting how one could add a generic [OSGI] bundle that interfaces with the the ODL [controller], without having to be part of
the [controller repository] itself. A second stage to this page would be to extend the newly added java module to do something with the [MD-SAL][] api.
That will be explored later some day, in part 2 of this series.

***NOTE:*** With the introduction of Karaf and OBR, this info may be out of date! What I mean is that while this page can be useful for learning
Hydrogen, it lacks all the changes to bundling that Karaf introduces in ODL 0.1.2+

# Step 1: Getting started

   - Get [git]
   - Get [Maven] 3+
   - Get [Java JDK] 1.7+
   - Config environment similar to what is mentioned in the [ODL's devel page][]

#Step 2: Grab odl bare bones repo

Bare bones is a minimalist repo that contains references to the ODL controller, as well as a hello_world [OSGI] bundle

    :::url
    https://github.com/flavio-fernandes/odl_bare_bones

To clone it:

    :::bash
    git clone git@github.com:flavio-fernandes/odl_bare_bones.git

# Step 3: hack away!

The heart of this exercise is actually about learning Maven. Using _pom.xml_ files, we can refer to external artifacts. In Hydrogen release, [OpenDayLight]
uses [OSGI] to connect the various bundles within the controller. In a nutshell, [OSGI] complements jar files with a manifest so that bundles can explicltly
tell that services it needs and what services it provides.

There are 3 pom.xml files in the repo:

    :::text
    A) build/pom.xml
    B) controller/pom.xml
    C) hello_world/pom.xml

Both (B) and (C) refer to (A) as their parent. (A) uses an external module -- commons.opendaylight -- as its parent.
That external module is what allows Maven to locate all pieces of the controller that we need, besides (C).
(B) is the pom.xml that we are really interested in, at the end. (B) relies on (A) for 2 purposes: 1) to get opendaylight's
pieces that are needed to create a functional controller and 2) to know how to pull in the hello_world [OSGI] module that we
create via (C). The module (C) uses (A) as a parent so it can grab external pieces it needs and to allow itself to be
resolved by (B). (C) does not need (B), but (B) has a dependency on getting (C).

## A) build/pom.xml ##

     <!-- The parent section points to the commons.opendaylight 1.4.1 at the external ODL repository -->
     <parent>
       <groupId>org.opendaylight.controller</groupId>
       <artifactId>commons.opendaylight</artifactId>
       <version>1.4.1</version>
     </parent>
   
     <!-- This section is the 'id' of this module. Note its group id as well as artifactId and version values -->
     <groupId>org.example.hello_world</groupId>
     <artifactId>hello_world</artifactId>
     <version>0.0.1-SNAPSHOT</version>
     <packaging>pom</packaging>
   
     ... 
   
     <!-- The modules section below indicates the two 'children' that this pom contains. One interesting
          caveat here is that other than making hello_world 'build' before controller, this is also a
          way in which controller knows how/where to pull hello_world (aka main.hello_world) module.
          At the end of the day, all that we use to run is the product of controller module -->
     <modules>
       <module>../hello_world/</module>
       <module>../controller</module>
     </modules>
   
     <repositories>
       <!-- This section tells Maven where to go in order to get artifacts that are external and not cached -->
       ...
       </repository>
     </repositories>
   
     <pluginRepositories>
        <!-- This section is very similar to the repositories, except it represents the external location
             of Maven plugins -->
        ...
     </pluginRepositories>
   </project>

One interesting caveat about (B) is in regards to how it is made to have (C) embedded. That happens because of
the dependency clause inside (B).

## B) controller/pom.xml ##

     <!-- The link between parent and child modules is expressed in the parent section below -->
     <parent>
       <groupId>org.example.hello_world</groupId>
       <artifactId>hello_world</artifactId>
       <version>0.0.1-SNAPSHOT</version>
       <relativePath>../build/</relativePath>
     </parent>
   
     <!-- This section is the 'id' of this module. Note its group id as well as artifactId and version values -->
     <artifactId>controller.hello_world</artifactId>
     <packaging>pom</packaging>
     <name>controller_plus_hello_world</name>
   
     <dependencies>
       <!-- This dependency is what makes this controller grab Hydrogen package --> 
       <dependency>
         <groupId>org.opendaylight.controller</groupId>
         <artifactId>distribution.opendaylight</artifactId>
         <version>0.1.1</version>
         <type>zip</type>
         <classifier>osgipackage</classifier>
         <!-- Make sure this isn't included on any classpath-->
         <scope>provided</scope>
       </dependency>
   
       <!-- This dependency is what pulls hello_world into the odl plugins directory -->
       <dependency>
         <groupId>org.example.hello_world</groupId>
         <artifactId>main.hello_world</artifactId>
         <version>0.0.3-SNAPSHOT</version>
       </dependency>
   
     </dependencies>

     <build>
         <!-- Hand waving for this section of the file... but this is the section that pulls in the various pieces
              of the controller, in addition to main.hello_world. Then is builds an [OSGI] distribution -->
         ...
     </build>
   </project>

(C) is the module that produces the artifact id main.hello_world. Given enough tinkering, this
OSGI module can do anything that all [OSGI] modules in the controller can. That includes, looking at incoming packets,
configuring flows, sending packets, etc.

## C) hello_world/pom.xml ##

     <!-- The link between parent and child modules is expressed in the parent section below -->
     <parent>
       <groupId>org.example.hello_world</groupId>
       <artifactId>hello_world</artifactId>
       <version>0.0.1-SNAPSHOT</version>
       <relativePath>../build/</relativePath>
     </parent>

     <!-- This section is the 'id' of this module. Note its group id as well as artifactId and version values -->
     <artifactId>main.hello_world</artifactId>
     <version>0.0.3-SNAPSHOT</version>
     <name>main_hello_world</name>
     <packaging>bundle</packaging>

     <build>
       <plugins>
         <plugin>
           <groupId>org.apache.felix</groupId>
           <artifactId>maven-bundle-plugin</artifactId>
           <version>2.3.6</version>
           <extensions>true</extensions>
           <configuration>
             <instructions>
               <Import-Package>
                 <!-- This is a bit of a rant from me, but I find it extremely ugly that felix plugin needs to
                      expose the dependencies of the [OSGI] packages. That can be a maintance headache and a
                      duplication of info that could be extracted form the .java file(s)... Yuck! -->
                 org.opendaylight.controller.sal.core,
                 org.opendaylight.controller.sal.utils,
                 org.opendaylight.controller.sal.packet,
                 ...
                 org.slf4j,
                 org.eclipse.osgi.framework.console,
                 org.osgi.framework
               </Import-Package>

               <Export-Package>
                 org.opendaylight.controller.hello_world
               </Export-Package>
   
               <Bundle-Activator>
                 org.opendaylight.controller.hello_world.internal.Activator
               </Bundle-Activator>
             </instructions>
             <manifestLocation>${project.basedir}/META-INF</manifestLocation>
           </configuration>
         </plugin>
       </plugins>
     </build>

     <dependencies>
       <dependency>
         <groupId>org.opendaylight.controller</groupId>
         <artifactId>switchmanager</artifactId>
         <version>0.5.0</version>
       </dependency>

       <dependency>
         <groupId>org.opendaylight.controller</groupId>
         <artifactId>sal</artifactId>
         <version>0.5.0</version>
       </dependency>

       <dependency>
         <groupId>equinoxSDK381</groupId>
         <artifactId>org.eclipse.osgi</artifactId>
       </dependency>

       <dependency>
         <groupId>junit</groupId>
         <artifactId>junit</artifactId>
       </dependency>
     </dependencies>
   </project>

Lastly, the [OSGI] needs an Activator class, which allows the bundle to be started after all the services it requires
are available. For the hello_world bundle that file is:

    :::text
    https://github.com/flavio-fernandes/odl_bare_bones/blob/master/hello_world/src/main/java/org/opendaylight/controller/hello_world/internal/Activator.java

    public class Activator extends ComponentActivatorAbstractBase {
       ...
       public void configureInstance(Component c, Object imp, String containerName) {
          ...
       }
    }

That is it folks! Hope you find this useful.

  [OpenDayLight]: http://www.opendaylight.org/
  [SDNHub]: http://sdnhub.org/tutorials/opendaylight/
  [Chris]: http://en.wikipedia.org/wiki/Chris_Wright_%28programmer%29
  [OSGI]: https://wiki.opendaylight.org/view/GettingStarted:Starter_OSGI_Bundle_Projects
  [controller]: https://wiki.opendaylight.org/view/OpenDaylight_Controller:Main
  [controller repository]: https://git.opendaylight.org/gerrit/p/controller.git
  [MD-SAL]: https://wiki.opendaylight.org/view/OpenDaylight_Controller:MD-SAL
  [git]: http://git-scm.com/downloads
  [Maven]: http://maven.apache.org/download.cgi
  [Java JDK]: http://www.oracle.com/technetwork/java/javase/downloads/jdk7-downloads-1880260.html
  [ODL's devel page]: https://wiki.opendaylight.org/view/GettingStarted:Development_Environment_Setup


