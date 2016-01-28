#!/bin/bash

source /home/volttron/volttron-source/env/bin/activate
volttron -l volttron.log -vv&

volttron-ctl start --name testagent-0.1
