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

RUN . /home/volttron/volttron-source/env/bin/activate && \
  pip install /home/volttron/demo/entities/Plug

WORKDIR /home/volttron/volttron-source

RUN . /home/volttron/volttron-source/env/bin/activate && \
  SOURCE=services/core/Platform CONFIG=services/core/Platform/config TAG=platform ./scripts/core/make-agent.sh enable
RUN . /home/volttron/volttron-source/env/bin/activate && \
  SOURCE=services/core/SQLHistorian CONFIG=services/core/SQLHistorian/config.sqlite.platform.historian TAG=historian ./scripts/core/make-agent.sh enable
RUN . /home/volttron/volttron-source/env/bin/activate && \
  SOURCE=~/demo/entities/Test CONFIG=~/demo/entities/Test/testagent.config TAG=testagent ./scripts/core/make-agent.sh enable
RUN . /home/volttron/volttron-source/env/bin/activate && \
  SOURCE=~/demo/entities/Plug CONFIG=~/demo/entities/Plug/plug-test.config TAG=plug ./scripts/core/make-agent.sh enable
RUN . /home/volttron/volttron-source/env/bin/activate && \
  SOURCE=~/demo/entities/Fan CONFIG=~/demo/entities/Fan/fan-entity-1.config TAG=fan ./scripts/core/make-agent.sh enable
EXPOSE 6600

WORKDIR /home/volttron

CMD ["bash"]
