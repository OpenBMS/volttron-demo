import sys
import datetime
import os

from volttron.platform.vip.agent import Agent as BaseAgent, PubSub, Core
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from zmq.utils import jsonapi

from boss_client import BossClient
import settings


def PlugEntity(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            return kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    AGENT_ID = get_config("agent_id")
    BOSS_DEVICE_NAME = get_config('boss_device_name')

    BOSS_EMAIL = os.environ['BOSS_EMAIL']
    BOSS_PASSWORD = os.environ['BOSS_PASSWORD']

    class Agent(BaseAgent):
        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
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
              "Location": get_config("location")
            }
            self.publish_all(data, prefix, headers)

        def publish_all(self, data, prefix, headers):
            for item in data.keys():
                topic = prefix + '/' + item
                self.vip.pubsub.publish_json('pubsub', topic, headers, str(data[item]))

        @PubSub.subscribe('pubsub', settings.TYPE_PREFIX + '/' + AGENT_ID + '/operations/switch')
        def on_switch(self, topic, headers, message, match):
            print 'Plug got\nTopic: {topic}, {headers}, Message: {message}'.format(topic=topic, headers=headers, message=message)
            self.boss_client.switch(jsonapi.loads(message[0]))
  
    Agent.__name__ = 'PlugEntity'
    return Agent(**kwargs)


def main(argv=sys.argv):
    """Main method called by the platform"""
    utils.vip_main(PlugEntity)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
