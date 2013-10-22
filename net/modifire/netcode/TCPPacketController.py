
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import NetAddress

from netcode.PacketController import PacketController
from netcode.Packet import Packet, TCPPacket
import Globals
import Settings
import time
       
class PeerData():
    
    def __init__(self):
        self.peerAddr = None
        self.conn = None

class TCPPacketController(PacketController):
    
    def __init__(self, tcpWriter, tcpReader, cManager, dataHandler):
        PacketController.__init__(self)
        self.tcpWriter = tcpWriter
        self.tcpReader = tcpReader
        self.cManager = cManager
        self.dataHandler = dataHandler
        self.connections = {}
        
    def OnPacketReceived(self, data, peerAddr):  
        code = data.getUint8()
        self.dataHandler.OnDataReceived(data, peerAddr, code)
        
    def AddConnection(self, conn, peerAddr):
        pd = PeerData()
        pd.peerAddr = peerAddr
        pd.conn = conn
        print 'adding connection', conn.getAddress().getIpString(), conn.getAddress().getPort(), peerAddr.getIpString(), peerAddr.getPort()
        self.connections[Packet.PeerAddrToIpPort(peerAddr)] = pd
                
    def CreateNewPacket(self, code):
        return TCPPacket(code)
    
    def CloseTCPConnection(self, peerAddr):
        pd = self.connections[Packet.PeerAddrToIpPort(peerAddr)]
        self.cManager.closeConnection(pd.conn)
        del self.connections[Packet.PeerAddrToIpPort(peerAddr)]
    
    def OpenTCPConnection(self, peerAddr):
        conn = self.cManager.openTCPClientConnection(peerAddr.getIpString(), Globals.PORT_SERVER_LISTENER, 1000)
        self.tcpReader.addConnection(conn)
        print 'created tcp conn', peerAddr.getIpString(), Globals.PORT_SERVER_LISTENER
        
        if(not self.HasPeerData(peerAddr)):
            self.AddConnection(conn, peerAddr)
#        else:
#            self.SetCurrentPeer(peerAddr)
#            self.currentPeer.conn = conn
        
    #------------------
    # Sending Packets
    #------------------
        
    def SendPacket(self, packet, peerAddr):
        if(Packet.PeerAddrToIpPort(peerAddr) in self.connections.keys()):
            self.tcpWriter.send(packet.GetDatagram(), self.connections[Packet.PeerAddrToIpPort(peerAddr)].conn)
                