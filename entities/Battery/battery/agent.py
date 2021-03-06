import sys
import datetime
import os
import logging

from threading import Thread
from tcpServer import TcpServer

from volttron.platform.vip.agent import Agent
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
from zmq.utils import jsonapi
from pint import UnitRegistry

import settings

utils.setup_logging() 
_log = logging.getLogger(__name__)
_units = UnitRegistry()

def battery_entity(config_path, **kwargs):
    config = utils.load_config(config_path)
    AGENT_ID = config.get("agent_id")

    class BatteryEntity(Agent):
        def __init__(self, **kwargs):
            super(BatteryEntity, self).__init__(**kwargs)

            self.tcpServer = TcpServer(config.get('port'), self)
            Thread(target=self.tcpServer.startServer).start()

        def process_data(self, msg):
            components = msg.split('&')
            data = {}
            # Extract individual fields from the message and create to dictionary for publishing
            for component in components:
                if '=' in component:
                    (key, value) = component.split('=')
                    quantity = _units(value)
                    data.update({
                      key: {
                        'magnitude': quantity.magnitude,
                        'unit': 'V'
                      }
                    })
            self.status_push(data) 

        def status_push(self, data):
            prefix = settings.TYPE_PREFIX + '/' + AGENT_ID + '/data'
            headers = {
              headers_mod.FROM: AGENT_ID,
              headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
              headers_mod.DATE: datetime.datetime.today().isoformat(),
              "Location": config.get('location')
            }
            self.publish_all(data, prefix, headers)
            _log.debug("publishing status: %s", str(data))

        def publish_all(self, data, prefix, headers):
            for item in data.keys():
                topic = prefix + '/' + item
                self.vip.pubsub.publish('pubsub', topic, headers, jsonapi.dumps(data[item]))

    return BatteryEntity(**kwargs)


def main(argv=sys.argv):
    """Main method called by the platform"""
    utils.vip_main(battery_entity)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
