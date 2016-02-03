import sys
import datetime
import socket

import signal
from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod

import settings

def BatteryEntity(config_path, **kwargs):
    #config = utils.load_config(config_path)

    def get_config(name):
        try:
            return kwargs.pop(name)
        except KeyError:
            return config.get(name, '')


    #AGENT_ID = get_config('agent_id')
    AGENT_ID = 'remo'
    DELIMITER = '/'
    def run_on(port):
        print("Starting a server on port %i" % port)
        server_address = (socket.gethostname(), port)
        httpd = HTTPServer(server_address,BatteryHttpServer)
        httpd.serve_forever()


    class BatteryHttpServer(BaseHTTPRequestHandler):
        def do_PUT(self):
            print "received data"
            #print self.headers
            length = int(self.headers['Content-Length'])
            content = self.rfile.read(length)
            print 'content' + content
            print 'length' + length
            self.send_response(200)

    class Agent(PublishMixin, BaseAgent):
        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.batteryId = 1234;
            self.power     = 65
            self.voltage   = 130
            self.current   = 0.5
            self.remainingCapacity = 20
            self.status     = "charging"
            #self.tcpServer  = TcpServer(10001,self); # random port. TODO need to get from config file
            #Thread(target = tcpServer.startServer).start()
            server = Thread(target=run_on, args=[5000])
            server.daemon = True
            server.start()

        @periodic(settings.HEARTBEAT_PERIOD)
        def status_push(self):
            data = {
              'batteryId' : self.batteryId,
              'power'     : self.power,
              'voltage'   : self.voltage,
              'current'   : self.current,
              'remainingCapacity': self.remainingCapacity,
              'status'    : self.status,
            }
            prefix = settings.PREFIX + DELIMITER + AGENT_ID
            headers = {
              headers_mod.FROM: AGENT_ID,
              headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
              headers_mod.DATE: datetime.datetime.today().isoformat()
            }
            self.publish_all(data, prefix, headers)

        def publish_all(self, data, prefix, headers):
            for item in data.keys():
                topic = prefix + DELIMITER + item
                self.publish_json(topic, headers, str(data[item]))

        @matching.match_start(settings.PREFIX + DELIMITER + AGENT_ID + DELIMITER + 'operations/changeBatteryState')
        def on_switch(self, topic, headers, message, match):
            print 'Battery Entity got\nTopic: {topic}, {headers}, Message: {message}'.format(topic=topic, headers=headers, message=message)
            self.status = message[0]
  
    Agent.__name__ = 'BatteryEntity'
    return Agent(**kwargs)


def main(argv=sys.argv):
    """Main method called by the platform"""
    utils.default_main(BatteryEntity,
                       description='Battery Entity',
                       argv=argv)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
