import sys
import datetime
import logging
import os

from volttron.platform.vip.agent import Agent, PubSub, Core
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from zmq.utils import jsonapi

from boss_client import BossClient
import settings

utils.setup_logging() 
_log = logging.getLogger(__name__)

def plug_entity(config_path, **kwargs):
    BOSS_EMAIL = os.environ['BOSS_EMAIL']
    BOSS_PASSWORD = os.environ['BOSS_PASSWORD']

    config = utils.load_config(config_path)
    AGENT_ID = config.get("agent_id")
    BOSS_DEVICE_NAME = config.get('boss_device_name')

    class PlugEntity(Agent):
        def __init__(self, **kwargs):
            super(PlugEntity, self).__init__(**kwargs)
            self.boss_client = BossClient(BOSS_EMAIL, BOSS_PASSWORD, BOSS_DEVICE_NAME)

        @Core.periodic(settings.HEARTBEAT_PERIOD)
        def status_push(self):
            data = {
              'status': self.boss_client.status(),
              'power': self.boss_client.power()
            }
            prefix = settings.TYPE_PREFIX + '/' + AGENT_ID + '/data'
            headers = {
              headers_mod.FROM: AGENT_ID,
              headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
              headers_mod.DATE: datetime.datetime.today().isoformat(),
              "Location": config.get("location")
            }
            _log.debug("publishing heartbeat")
            self.publish_all(data, prefix, headers)

        def publish_all(self, data, prefix, headers):
            for item in data.keys():
                topic = prefix + '/' + item
                self.vip.pubsub.publish('pubsub', topic, headers, jsonapi.dumps(data[item]))

        @PubSub.subscribe('pubsub', settings.TYPE_PREFIX + '/' + AGENT_ID + '/operations/switch')
        def on_switch(self, topic, headers, message, match):
            print 'Plug got\nTopic: {topic}, {headers}, Message: {message}'.format(topic=topic, headers=headers, message=message)
            self.boss_client.switch(jsonapi.loads(message[0]))
  
    return PlugEntity(**kwargs)


def main(argv=sys.argv):
    """Main method called by the platform"""
    utils.vip_main(plug_entity)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
