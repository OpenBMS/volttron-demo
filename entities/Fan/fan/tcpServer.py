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
            (self.clientSocket,self.clientAddress) = self.serverSocket.accept()
            print self.clientSocket 
            self.clientHandler()

    def sendData(self,data):
       totalSent = 0
       sentBytes = self.clientSocket.send(data)

    def clientHandler(self):
        print 'New connection from %s:%d' % (self.clientAddress[0], self.clientAddress[1])
        while True:
            data = self.clientSocket.recv(1024).strip()
            if not data:
                self.clientSocket.close()
                break;
            else:
                self.agent.process_data(data)

