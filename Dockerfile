FROM openbms/volttron:latest

# Install selenium and dependencies
RUN apt-get update
RUN apt-get install wget openjdk-7-jre-headless firefox xvfb -y --force-yes
RUN mkdir ~/.selenium
RUN wget http://selenium-release.storage.googleapis.com/2.50/selenium-server-standalone-2.50.0.jar -P ~/.selenium

ADD launch.sh /home/volttron/launch.sh
RUN chown -R volttron:volttron /home/volttron/launch.sh
RUN chmod +x /home/volttron/launch.sh

ADD make-agent-with-args.sh /home/volttron/volttron-source/scripts/core/make-agent-with-args.sh
RUN chown -R volttron:volttron /home/volttron/volttron-source/scripts/core/make-agent-with-args.sh
RUN chmod +x /home/volttron/volttron-source/scripts/core/make-agent-with-args.sh

USER volttron

ADD requirements.txt /home/volttron/demo/requirements.txt

RUN . /home/volttron/volttron-source/env/bin/activate && pip install -r /home/volttron/demo/requirements.txt

WORKDIR /home/volttron/volttron-source

ADD . /home/volttron/demo

RUN . /home/volttron/volttron-source/env/bin/activate && \
  SOURCE=services/core/Platform CONFIG=services/core/Platform/config TAG=platform COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=services/core/SQLHistorian CONFIG=services/core/SQLHistorian/config.sqlite.platform.historian TAG=historian COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/entities/Test CONFIG=~/demo/entities/Test/testagent.config TAG=testagent COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/entities/Plug CONFIG=~/demo/config/rpie/battery-lamp-plug.config TAG=battery-lamp-plug COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/entities/Plug CONFIG=~/demo/config/rpie/battery-plug.config TAG=battery-plug COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/entities/Plug CONFIG=~/demo/config/rpie/fan-plug.config TAG=fan-plug COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/entities/Plug CONFIG=~/demo/config/rpie/lamp-plug.config TAG=lamp-plug COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/agents/HouseCoordinator CONFIG=~/demo/config/rpie/housecoordinator.config TAG=hc COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/entities/Battery CONFIG=~/demo/config/rpie/battery-arduino.config TAG=battery COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable && \
  SOURCE=~/demo/entities/Fan CONFIG=~/demo/config/rpie/fan-arduino.config TAG=fan COMMAND_ARGS="-t 0" ./scripts/core/make-agent-with-args.sh enable

EXPOSE 5050
EXPOSE 6000
EXPOSE 6001

WORKDIR /home/volttron

CMD ["bash"]
