## TODO Try to push the tcpServer into a generic library that can be used in all agents
import settings
import socket,sys
import SocketServer

class TcpServer():
    """
    Server responsible for communicating with battery equipment to receive relevant data and perform necessary control
    """

    def __init__(self,portNumber,agent):
        self.portNumber = portNumber
        # current architecture, we have an agent instance for every device. So, by extension, we are having a server
        # for each device.
        self.clientSocket  = None
        self.clientAddress = None
        self.serverSocket  = None
        self.agent = agent

    def isClientConnected(self):
        if self.clientSocket is None or self.clientAddress is None:
            return False
        return True

    def startServer(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((socket.gethostname(),self.portNumber))
        self.serverSocket.listen(1)
        while (True):
            # our server can serve onlt one client. It is intended by design to have this 1:1 mapping
            (self.clientsocket,self.clientAddress) = self.serverSocket.accept()
            self.clientHandler()
    
    def clientHandler(self):
        print 'New connection from %s:%d' % (self.clientAddress[0], self.clientAddress[1])
        while True:
            data = self.clientsocket.recv(1024).strip()
            if not data:
                self.clientsocket.close()
                break;
            else:
                # Having the processData as part of agent object will enable us to have agent specific processing
                self.agent.process_data(data)
