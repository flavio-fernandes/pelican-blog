Title: Installing and running Sonar locally
Date: 2015-06-29 15:59
Author: flavio
Category: Work
Tags: work, tools, opendaylight
Slug: how-to-run-sonar-locally

Downloading and running SonarQube in local system

<!--more-->

With help from [Sam][1], I was able to have Sonar tool -- similar to the one
we have in [sonar.opendaylight.org][2] -- running locally. This is a quick
blurb on the details for doing that. In this particular case, I'm using
[ODL's ovsdb project][ovsdb].

### 1) Download and install Sonar

Go to: [http://www.sonarqube.org/downloads/][3]

    wget --quiet http://downloads.sonarsource.com/sonarqube/sonarqube-5.1.1.zip
    unzip sonarqube-5.1.1.zip > /dev/null

### 2) Start Sonar

    MY_OS='macosx-universal-64' ; ./sonarqube-5.1.1/bin/${MY_OS}/sonar.sh start

Using your browser, go to [http://localhost:9000][4] and login

![login](|filename|/images/sonar-login.jpg)

### 3) Grab OVSDB and build

See [wiki for better details on installing][5]

    git clone https://git.opendaylight.org/gerrit/ovsdb ovsdb.git

### 4) Generate unit test for sonar data from OVSDB project. Note we bulid twice, once to grab
all needed dependencies and again to build against sonar.

    cd ovsdb.git && mvn clean install -DskipTests
    mvn verify -Pcoverage,jenkins -Dsonar.host.url=http://localhost:9000 sonar:sonar

<span id=add_unit_test_coverage_widget_in_sonar />
### 5) Add Unit Test Coverage widget in Sonar

5.1) Select **Dashboard**, make sure you see **ovsdb** project, and select **configure widgets**.

![login](|filename|/images/sonar-config-widget.jpg)

5.2) Scroll list of widgets and locate **Unit Test Coverage** and click **Add Widget**. On field below, fill in **ovsdb** and click **save**.

![login](|filename|/images/sonar-config-widget-unit-test.jpg)

### 6) Generate integration test for sonar data from OVSDB project

In order to run integration test coverage, you will need a running instance of OVS,
so OVSDB can talk to. See [this link][6] and [this link][7] for different methods of running OVS.

Once OVS is running, do this from the integration directory in ovsdb.git

    cd ./integrationtest && \
    mvn verify -Pintegrationtest,coverage,jenkins -Dsonar.host.url=http://localhost:9000 \
    -Dovsdbserver.ipaddress=${OVS_IP} -Dovsdbserver.port=6640 -nsu -o sonar:sonar 

    cd ../southbound/southbound-it && \
    mvn verify -Pintegrationtest,coverage,jenkins -Dsonar.host.url=http://localhost:9000 \
    -Dovsdbserver.ipaddress=${OVS_IP} -Dovsdbserver.port=6640 -nsu -o sonar:sonar 

### 7) Add Integration test Coverage widget in Sonar

Repeat step [5 above](#add_unit_test_coverage_widget_in_sonar) except, that the widget added is called **Integration Tests Coverage**.


  [ovsdb]: https://wiki.opendaylight.org/view/OVSDB_Integration:Main "Open vSwitch Database Integration"
  [1]: https://trello.com/c/lPff5MP3/31-investigate-method-to-run-sonar-from-command-line-and-interpret-results "Run sonar from command line and interpret results"
  [2]: https://sonar.opendaylight.org/ "Opendaylight Sonar"
  [3]: http://www.sonarqube.org/downloads/ "Sonar Download"
  [4]: http://localhost:9000
  [5]: https://wiki.opendaylight.org/view/OVSDB:Installation_Guide "OVSDB Install"
  [6]: https://github.com/flavio-fernandes/docker-ovs "Userspace Open vSwitch containers"
  [7]: https://wiki.opendaylight.org/view/OVSDB_Integration:Mininet_OVSDB_Tutorial "Running mininet"
