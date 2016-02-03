#!/bin/bash

source /home/volttron/volttron-source/env/bin/activate
DISPLAY=:1 xvfb-run java -jar ~/.selenium/selenium-server-standalone-2.50.0.jar > selenium.log &
volttron -l volttron.log -vv&

pip install demo/entities/Plug

volttron-ctl start --name testagent-0.1
volttron-ctl start --name plug_openbms_entity-0.1
