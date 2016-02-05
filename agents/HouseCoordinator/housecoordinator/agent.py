import sys
import random
import datetime
import os
import logging

from volttron.platform.vip.agent import Agent, PubSub
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
from zmq.utils import jsonapi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from ServerHTTP import HouseHTTPServer;
import SocketServer
import threading
import pprint

utils.setup_logging() 
_log = logging.getLogger(__name__)

AGENT_ID = os.environ.get("AGENT_UUID")
PORT = 5050

def start_server():
    print 'http server is starting...'
    #ip and port of server
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, HouseHTTPServer)
    print 'http server is running...'
    httpd.serve_forever()
    return


class HouseCoordinator(Agent):

    def __init__(self, config_path, **kwargs):
        super(HouseCoordinator, self).__init__(**kwargs)
        # dict which maintains state of agents connected to Home coordinator
        self.agents_context_map = {}
        # current mode (economy or comfort)
        self.mode = "comfort"
        # current power price (low, medium or high)
        self.power_price = "high"
        # Initialize Energy profile map, which indicates highest allowed operating 
        # states for each of the device, given a mode and price level
        self.init_energy_profile_map()
        HouseHTTPServer.set_instance(self)
        t = threading.Thread(target=start_server)
        t.start()   

    def init_energy_profile_map(self):
        self.energy_profile_map = {
            "economy": 
             {
                "low": 
                {
                    "battery-lamp-plug": "on",
                    "lamp-plug"        : "on",
                    "fan-arduino"      : "fast",
                    "fan-plug"         : "on",
                    "pump-arduino"     : "fast",
                    "battery-plug"     : "on"
                },
                "medium":
                {
                    "battery-lamp-plug": "on",
                    "lamp-plug"        : "on",
                    "fan-arduino"      : "medium",
                    "fan-plug"         : "on",
                    "pump-arduino"     : "slow",
                    "battery-plug"     : "off"
                },
                "high":
                {
                    "battery-lamp-plug": "on",
                    "lamp-plug"        : "on",
                    "fan-arduino"      : "slow",
                    "fan-plug"         : "off",
                    "pump-arduino"     : "off",
                    "battery-plug"     : "off"
                }
             },

            "comfort": 
             {
                "low": 
                {
                    "battery-lamp-plug": "on",
                    "lamp-plug"        : "on",
                    "fan-arduino"      : "fast",
                    "fan-plug"         : "on",
                    "pump-arduino"     : "fast",
                    "battery-plug"     : "on"
                },
                "medium":
                {
                    "battery-lamp-plug": "on",
                    "lamp-plug"        : "on",
                    "fan-arduino"      : "medium",
                    "fan-plug"         : "on",
                    "pump-arduino"     : "medium",
                    "battery-plug"     : "off"
                },
                "high":
                {
                    "battery-lamp-plug": "on",
                    "lamp-plug"        : "on",
                    "fan-arduino"      : "slow",
                    "fan-plug"         : "on",
                    "pump-arduino"     : "slow",
                    "battery-plug"     : "off"
                }
             }
        }

    def get_allowed_operating_states(self):
        mode_map = self.energy_profile_map.get(self.mode)
        if mode_map is None:
            raise ValueError("Invalid mode %s" %(self.mode))
        oper_states = mode_map.get(self.power_price)
        if oper_states is None:
            raise ValueError("Invalid power price %s"%(self.power_price))
        return oper_states
    
    def get_agents_context_map():
        return self.agents_context_map

    def is_transition_needed(self,location,highest_allowed_device_state,status,speed):
        # print "current_device_state %s , highest_allowed_device_state %s" %(current_device_state,highest_allowed_device_state) 
        # current device state is same as highest allowed device state. No action needed

        # TODO explore the possibility of merging status and speed into single state which 
        # HC can communicate to agent
        
        # capture current device state based on status and speed
        if status == 'off':
            current_device_state = status
        else:
            current_device_state = speed

        if (current_device_state == highest_allowed_device_state):
            return False

        # for battery always trigger a transition if current state is different from highest
        # allowed state
        if (location == 'battery'):
            return True
        
        # If device is off, no new actions are needed for that device
        if (current_device_state  == 'off'):
            return False

        # Take specific actions based on the device type and current state
        if ((location == 'pump') or (location == 'fan')):
            if (highest_allowed_device_state == 'off'):
                if (current_device_state != 'off'):
                    return True
            elif (highest_allowed_device_state == 'slow'):
                if (current_device_state not in ['off','slow']):
                    return True
            elif (highest_allowed_device_state == 'medium'):
                if (current_device_state in ['fast']):
                    return True
            else:
                return False

        elif (location == 'lamp'):
            if (highest_allowed_device_state == 'off'):
                if (current_device_state != 'off'):
                    return True
            else:
                return False

        else:
            raise ValueError("invalid location %s"%(location))

    # for now just maintaining a map to get property based on the value.
    def get_property_from_value(self, value):
        if value in ['on','off']:
            return 'status'
        if value in ['slow','medium','fast']:
            return 'speed'

    # compares operating states of devices against highest allowed operating
    # state for current energy profile. If needed triggers transitions to
    # ensure devices are within the operating limits
    def trigger_transitions(self):
        oper_states = self.get_allowed_operating_states()
        for agent in self.agents_context_map.keys():
            agent_state = self.agents_context_map[agent]
            # get the type of device associated with the agent
            device_type = agent_state['device_type']
            location = agent_state['location']
            # retreive allowed states for this device
            highest_allowed_device_state = oper_states.get(location)
            if highest_allowed_device_state is None:
                raise ValueError("invalid agent location %s"%(location))
            # based on highest allowed state and current device status evaluate if a transition is needed
            if (self.is_transition_needed(location,highest_allowed_device_state,agent_state['status'],agent_state['speed'])):
                # TODO trigger tranistion to move to appropriate state
                print "Transition triggered for agent %s on location %s to move to %s"%(agent,location,highest_allowed_device_state)
                params =  {
                    'device_id': agent,
                    'property': self.get_property_from_value(highest_allowed_device_state),
                    'value'   : highest_allowed_device_state
                }
                create_and_publish_topic(params)
                # agent_state['status'] = highest_allowed_device_state
            else:
                print "No transition needed"

    def set_mode(self,mode):
        self.mode = mode
        self.trigger_transitions()

    def set_price(self,power_price):
        self.power_price = power_price
        self.trigger_transitions()

    @PubSub.subscribe('pubsub', '')
    def on_match_all(self, peer, sender, bus, topic, headers, message):
        agent_id = headers.get(headers_mod.FROM)
        if agent_id is None or agent_id == AGENT_ID:
            return

        _log.debug("topic: {s}".format(s=topic))
        device_type = "/".join(topic.split("/")[0:2])
        _log.debug("device_type: {s}".format(s=device_type))
        if (not self.agents_context_map.has_key(agent_id)):
            self.agents_context_map[agent_id] = {}

        cur_agent_context = self.agents_context_map[agent_id]
        # TODO: We can think of adding the type only when the context is newly created
        cur_agent_context['device_type'] = device_type
        cur_agent_context.update({'location':headers.get('Location')})
        # extract specific property (such as voltage, power etc.) from the topic 
        cur_agent_context.update({topic.split("/")[-1]:  jsonapi.loads(message)})
        self.agents_context_map[agent_id].update(cur_agent_context)
        HouseHTTPServer.set_buffer(self.agents_context_map)

    def create_message_and_publish(self, topic, message):
        headers = {
            headers_mod.FROM: AGENT_ID,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
            headers_mod.DATE: datetime.datetime.today().isoformat()
        }
        self.vip.pubsub.publish('pubsub', topic, headers, jsonapi.dumps(message))
   
    def create_and_publish_topic(self, params):
        agent_id = params.get('device_id')

        agent_context = self.agents_context_map.get(agent_id)
        if agent_context is None:
            raise ValueError("Non existing context")

        topic = agent_context['device_type'] + '/' + agent_id + '/operations/' + params['property']

        headers = {
            headers_mod.FROM: AGENT_ID,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: datetime.datetime.today().isoformat()
        }
        self.vip.pubsub.publish('pubsub', topic, headers, jsonapi.dumps(params['value']))

    def toggle_lamp(self, lamp_prefix, status):
        target_status = 'ON' if status == 'OFF' else 'OFF'
        topic = lamp_prefix + "/operations/switch"
        self.create_message_and_publish(topic, target_status)

    def set_speed(self, prefix, target_speed):
        topic = prefix + "/operations/speed"
        self.create_message_and_publish(topic, target_speed)

    def toggle_battery_state(self, storage_prefix, status):
        if status == "discharging":
            target_status = "charging"
        else:
            target_status = "discharging"

        topic = storage_prefix + "/operations/changeBatteryState"
        self.create_message_and_publish(topic, target_status)


def getCurrentState():
    return currentState
  
def main(argv=sys.argv):
    """Main method called by the platform"""
    utils.vip_main(HouseCoordinator)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
