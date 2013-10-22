
from netcode.Packet import Packet

class PacketController():
    
    def __init__(self):
        self.currentPeer = None
        self.connections = {}
        self.outgoingPacketsInLastSecond = 0
        self.outgoingBytesInLastSecond = 0
    
    def SetCurrentPeer(self, peerAddr):
        self.currentPeer = self.connections[Packet.PeerAddrToIpPort(peerAddr)]
        
    def HasPeerData(self, peerAddr):
        return Packet.PeerAddrToIpPort(peerAddr) in self.connections.keys()
    
    def GetPeers(self):
        return self.connections.values()
    
    def RemovePeerData(self, peerAddr):
        if(self.HasPeerData(peerAddr)):
            print 'removing', Packet.PeerAddrToIpPort(peerAddr)
            del self.connections[Packet.PeerAddrToIpPort(peerAddr)]
            del self.currentPeer
            self.currentPeer = None
            
    def RemoveAllPeerData(self):
        for key in self.connections.keys():
            del self.connections[key]
        self.connections = {}
        
    def CleanUp(self):
        self.RemoveAllPeerData()
        del self.currentPeer
        self.currentPeer = None
    
    def CreatePeerData(self, peerAddr):
        print 'OVERRIDE CreatePeerData'
        raise
    
    def ClearBandwidthInfo(self):
        self.outgoingBytesInLastSecond = 0
        self.outgoingPacketsInLastSecond = 0