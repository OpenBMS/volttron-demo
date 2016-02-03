#!/bin/bash

source /home/volttron/volttron-source/env/bin/activate
DISPLAY=:1 xvfb-run java -jar ~/.selenium/selenium-server-standalone-2.50.0.jar > selenium.log &

pip install demo/entities/Plug

cd volttron-source

SOURCE=services/core/Platform CONFIG=services/core/Platform/config TAG=platform ./scripts/core/make-agent.sh enable
SOURCE=~/demo/entities/Test CONFIG=~/demo/entities/Test/testagent.config TAG=testagent ./scripts/core/make-agent.sh enable
SOURCE=~/demo/entities/Plug CONFIG=~/demo/entities/Plug/plug-test.config TAG=plug ./scripts/core/make-agent.sh enable

cd ~

volttron -l volttron.log -vv&

