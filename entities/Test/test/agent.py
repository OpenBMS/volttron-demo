import logging
import sys

from volttron.platform.vip.agent import Agent, PubSub
from volttron.platform.agent import utils

utils.setup_logging() 
_log = logging.getLogger(__name__)

class TestAgent(Agent):
  def __init__(self, config_path, **kwargs):
    super(TestAgent, self).__init__(**kwargs)

  @PubSub.subscribe('pubsub', '')
  def on_heartbeat_topic(self, peer, sender, bus, topic, headers, message):
    _log.debug("TestAgent got\nTopic: {topic}, {headers}, Message: {message}".format(topic=topic, headers=headers, message=message))

def main(argv=sys.argv):
  '''Main method called by the platform.'''
  utils.vip_main(TestAgent)

if __name__ == '__main__':
  # Entry point for script
  try:
    sys.exit(main())
  except KeyboardInterrupt:
    pass
