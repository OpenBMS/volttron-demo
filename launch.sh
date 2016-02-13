#!/bin/bash

source /home/volttron/volttron-source/env/bin/activate

DISPLAY=:1 xvfb-run java -jar .selenium/selenium-server-standalone-2.50.0.jar > selenium.log &

wget -O /dev/null http://127.0.0.1:4444/wd/hub/status
while [ $? -ne 0 ]
do
  wget -O /dev/null http://127.0.0.1:4444/wd/hub/status
done

volttron -l volttron.log -vv&

