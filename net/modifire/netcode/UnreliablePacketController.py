
from netcode.Packet import UnreliablePacket, Packet
from netcode.PacketController import PacketController



class PeerData():
    
    def __init__(self):
        self.peerAddr = None
        self.lastRecvdSeq = 0
        self.mySeq = 0


class UnreliablePacketController(PacketController):
    
    MAX_SEQ_NUM = 256

    def __init__(self, cWriter, conn, dataHandler):
        PacketController.__init__(self)
        self.cWriter = cWriter
        self.conn = conn
        self.dataHandler = dataHandler
        
        self.outgoingSeqNum = 1

    def OnPacketReceived(self, data, peerAddr):

        seqNum = data.getUint8()        
        code = data.getUint8()
        
        if(not self.HasPeerData(peerAddr)):
            self.CreatePeerData(peerAddr)
        self.SetCurrentPeer(peerAddr)

        if(not self.seqNumMoreRecent(seqNum, self.currentPeer.lastRecvdSeq)):
            print 'OLD packet ', seqNum, ' ', self.currentPeer.lastRecvdSeq, ' ', Packet.PeerAddrToIpPort(self.currentPeer.peerAddr)
            # If we recvd an old packet and the reliable pkt controller doesn't know this person
            if(not self.dataHandler.rUDP.HasPeerData(peerAddr)):
                self.RemovePeerData(peerAddr)
                print 'Got old packet from unknown person', Packet.PeerAddrToIpPort(peerAddr)
                return
                
            if(seqNum - self.currentPeer.lastRecvdSeq > 30):
                self.currentPeer.lastRecvdSeq = seqNum
            else:
                return
        else:
            self.currentPeer.lastRecvdSeq = seqNum
            
        self.dataHandler.OnDataReceived(data, peerAddr, code)

    def SendPacket(self, packet, addr):
        self.outgoingPacketsInLastSecond += 1
        self.outgoingBytesInLastSecond += packet.GetLength()
        self.cWriter.send(packet.GetDatagram(), self.conn, addr)

    def CreateNewPacket(self, code):
        p = UnreliablePacket(self.outgoingSeqNum, code)
        self.outgoingSeqNum = self.IncreaseSequenceNumber(self.outgoingSeqNum)
        return p
    
    def CreatePeerData(self, peerAddr):
        self.connections[Packet.PeerAddrToIpPort(peerAddr)] = PeerData()
        self.connections[Packet.PeerAddrToIpPort(peerAddr)].peerAddr = peerAddr
        self.SetCurrentPeer(peerAddr)

    def IncreaseSequenceNumber(self, seq):
        return (seq + 1) % (UnreliablePacketController.MAX_SEQ_NUM)
    
    def GetSeqNum(self):
        return self.outgoingSeqNum

    def seqNumMoreRecent(self, seq1, seq2):
        return (( seq1 > seq2 ) and ( seq1 - seq2 <= UnreliablePacketController.MAX_SEQ_NUM / 2 ) or
               ( seq2 > seq1 ) and ( seq2 - seq1 > UnreliablePacketController.MAX_SEQ_NUM / 2  ))

    def CleanUp(self):
        PacketController.CleanUp(self)
        self.outgoingSeqNum = 1