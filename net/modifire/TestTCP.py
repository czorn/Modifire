from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties #@UnresolvedImport
from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionReader, ConnectionWriter, NetAddress, NetDatagram, QueuedConnectionListener, PointerToConnection
from direct.distributed.PyDatagram import PyDatagram

PORT = 5556
IP_ADDR = '68.59.144.180'

class Client():
    
    def __init__(self):
        self.cManager = QueuedConnectionManager()
        self.tcpWriter = ConnectionWriter(self.cManager,0)
        self.tcpReader = QueuedConnectionReader(self.cManager, 0)
        taskMgr.add(self.tskReaderPolling,"Poll the connection reader",-40)
        
        # This fails
        self.conn = self.cManager.openTCPClientConnection(IP_ADDR, PORT, 1000)
        if self.conn:
            print 'Successful connection to', IP_ADDR, ':', PORT
            self.tcpReader.addConnection(self.conn)
            
            self.SendPacket()
            
    def SendPacket(self):
        dg = PyDatagram()
        dg.addUint8(5)
        self.tcpWriter.send(dg, self.conn)
            
    def tskReaderPolling(self, task):
        if self.tcpReader.dataAvailable():
            datagram = NetDatagram()
            if self.tcpReader.getData(datagram):
                print 'client got data'
        return task.cont
        
class Server():
    
    def __init__(self):
        self.cManager = QueuedConnectionManager()
        self.tcpSocket = self.cManager.openTCPServerRendezvous(PORT, 1000)
        self.tcpWriter = ConnectionWriter(self.cManager,0)
        self.tcpListener = QueuedConnectionListener(self.cManager, 0)
        self.tcpListener.addConnection(self.tcpSocket)
        self.tcpReader = QueuedConnectionReader(self.cManager, 0)
        
        taskMgr.add(self.tskListenerPolling,"Poll the connection listener",-39)
        taskMgr.add(self.tskReaderPolling,"Poll the connection reader",-40)
        
    def SendPacket(self):
        dg = PyDatagram()
        dg.addUint8(5)
        self.tcpWriter.send(dg, self.conn)
        
    def tskReaderPolling(self, task):
        if self.tcpReader.dataAvailable():
            datagram = NetDatagram()
            if self.tcpReader.getData(datagram):
                print 'server got data'
                self.SendPacket()
        return task.cont
    
    def tskListenerPolling(self, task):
        if self.tcpListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
        
            if self.tcpListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.tcpReader.addConnection(newConnection)
                self.conn = newConnection
                print self.conn.getAddress().getPort()
        return task.cont



  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        wp = WindowProperties()
        wp.setSize(850, 480)
        wp.setTitle("GAME")
        base.win.requestProperties(wp)
        
        c = Client()
        #s = Server()

app = MyApp() 
app.run()


