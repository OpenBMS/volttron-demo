FROM openbms/volttron:latest

# Install selenium and dependencies
RUN apt-get update
RUN apt-get install wget openjdk-7-jre-headless firefox xvfb -y --force-yes
RUN mkdir ~/.selenium
RUN wget http://selenium-release.storage.googleapis.com/2.50/selenium-server-standalone-2.50.0.jar -P ~/.selenium

ADD . /home/volttron/demo
RUN chown -R volttron:volttron /home/volttron/demo

ADD launch.sh /home/volttron/launch.sh
RUN chown -R volttron:volttron /home/volttron/launch.sh
RUN chmod +x /home/volttron/launch.sh

USER volttron

CMD ["bash"]
