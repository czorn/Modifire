
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import NetAddress

from collections import deque
from netcode.Packet import ReliablePacket
from netcode.PacketController import PacketController
from netcode.Packet import Packet
from event.ClientEvent import PeerTimeoutEvent 
import Settings
import time

# if streaming and haven't heard anything in 30 packets, queue packets in memory
# on packet received, handle missing, and send next 30

class PacketAndDest():
    
    def __init__(self, packet, destAddr):
        self.packet = packet
        self.destAddr = destAddr
        
class PeerData():
    
    def __init__(self):
        self.peerAddr = None
        self.mySeq = 1                  # The current seqNumber of the data I am sending
        self.mostRecentSeqRecvd = 0    # The most recent seqNumber of the peer I am receiving data from
        self.recvdSeq = deque(['0'] * ReliablePacketController.MAX_NUM_SEQ)         # A queue of seqNumbers I have received
        self.sentPackets = deque([None] * ReliablePacketController.MAX_NUM_SEQ)      # A queue of packets I have sent
        self.consecutiveReceivedWithoutNotification = 0
        self.timeOfLastSentPacketFromUs = 0
        self.timestamp = 0

class ReliablePacketController(PacketController):
    
    MAX_NUM_SEQ = 32
    
    def __init__(self, cWriter, conn, dataHandler, checkForPacketFunc = None):
        PacketController.__init__(self)
        self.cWriter = cWriter
        self.conn = conn
        self.dataHandler = dataHandler
        self.checkForPacketFunc = checkForPacketFunc
        
        taskMgr.setupTaskChain('RUDP_Heartbeat', numThreads = 1,
                       frameSync = False)
        
        taskMgr.doMethodLater(0.1, self.SendHeartBeats, 'SendHeartBeats', taskChain = 'RUDP_Heartbeat')
        taskMgr.doMethodLater(1, self.CheckForTimedOutClients, 'CheckForTimedOutClients')
        
    def OnPacketReceived(self, data, peerAddr):       
        peerSeqNum = data.getUint32()
        peerLastSeqRecvd = data.getUint32()
        recvdSeq = Packet.Int32ToBits(data.getUint32())
        code = data.getUint8()
        
        #print 'GOT PACKET FROM', Packet.PeerAddrToIpPort(peerAddr), ' ', code, ' ', peerSeqNum, ' ', peerLastSeqRecvd
        
        if(not self.HasPeerData(peerAddr)):
            print 'NO DATA'
            #self.CreatePeerData(peerAddr)
            return None
        
        self.SetCurrentPeer(peerAddr)
        
        self.currentPeer.timestamp = time.time()
        self.CheckForDroppedPackets(peerLastSeqRecvd, recvdSeq)
        
        if(peerSeqNum > self.currentPeer.mostRecentSeqRecvd):
            diff = peerSeqNum - self.currentPeer.mostRecentSeqRecvd - 1
            if(diff > 0 and diff < 7):
                print 'Lost Packet', diff, peerSeqNum
                self.AddMissedSeqNums(diff)
            self.AddRecvdSeqNum()
            self.currentPeer.mostRecentSeqRecvd = peerSeqNum
        else:
            index = self.currentPeer.mostRecentSeqRecvd - peerSeqNum
            print 'old rudp', index , self.currentPeer.mostRecentSeqRecvd, peerSeqNum
            if(not self.UpdatePriorSeqNum(index)):
                print 'DUPLICATE'
                return None
        
        self.dataHandler.OnDataReceived(data, peerAddr, code)
    
    def CheckForPeerFinishedStream(self, peerLastSeqRecvd):
        if(self.currentPeer.wasStreaming and peerLastSeqRecvd >= self.currentPeer.streamingSeqEnd):
            self.ResetStream()
    
    def CreatePeerData(self, peerAddr):
        print 'created data for', Packet.PeerAddrToIpPort(peerAddr)
        self.connections[Packet.PeerAddrToIpPort(peerAddr)] = PeerData()
        self.SetCurrentPeer(peerAddr)
        self.currentPeer.peerAddr = peerAddr
        self.currentPeer.mostRecentSeqRecvd = 0
        self.currentPeer.timestamp = time.time()
            
    def StartStream(self, peerAddr):
        if(not self.HasPeerData(peerAddr)):
            self.CreatePeerData(peerAddr)
            
        self.currentPeer.isStreaming = True
        self.currentPeer.streamedPackets = [None]
        self.currentPeer.streamingSeqStart = int(self.currentPeer.mySeq)
        print 'Start stream', self.currentPeer.streamingSeqStart
        
    def EndStream(self, peerAddr):
        self.SetCurrentPeer(peerAddr)
        self.currentPeer.isStreaming = False
        self.currentPeer.streamingSeqEnd = int(self.currentPeer.mySeq)
        self.currentPeer.wasStreaming = True

    def ResetStream(self):
        print 'ResetStream'
        self.currentPeer.wasStreaming = False
        self.currentPeer.streamedPackets = None
        self.currentPeer.streamedSeqStart = pow(2, 30)
        self.currentPeer.streamedSeqEnd = pow(2, 30)
        self.currentPeer.queuedStreamPackets = deque()
    
    def CheckForLackOfNotification(self):
        if(self.currentPeer.consecutiveReceivedWithoutNotification > ReliablePacketController.MAX_NUM_SEQ / 4):
            self.SendEmptyPacket()
            self.currentPeer.consecutiveWithoutNotification = 0
        
    def UpdatePriorSeqNum(self, index):
        index = ReliablePacketController.MAX_NUM_SEQ - index - 1
        li = list(self.currentPeer.recvdSeq)
        
        print 'update prior', index, li
        if(index < 0 or index > ReliablePacketController.MAX_NUM_SEQ -1):
            print 'RUDP INDEX ERROR:', index
            return False
        
        if(li[index] == '0'):
            li[index] = '1'
            self.currentPeer.recvdSeq = deque(li)
            print 'updated right one'
            return True
        return False
        
    def AddRecvdSeqNum(self):
        self.currentPeer.recvdSeq.popleft()
        self.currentPeer.recvdSeq.append('1')
        
    def AddMissedSeqNums(self, numMissed):
        for i in xrange(numMissed):
            self.currentPeer.recvdSeq.popleft()
            self.currentPeer.recvdSeq.append('0')
        
    # Loop through all of the recvdSeq numbers, if one is missing,
    # resend it
    def CheckForDroppedPackets(self, peerLastSeqRecvd, recvdSeq):
        for i, seq in enumerate(recvdSeq):
            if(seq != '1'):
                missingSeq = peerLastSeqRecvd - ReliablePacketController.MAX_NUM_SEQ + i + 1
                if(missingSeq > 0):
                    print 'MISSING', missingSeq
                    pas = list(self.currentPeer.sentPackets)[i]
                    self.ResendPacket(pas.packet, pas.destAddr)
                
    def CreateNewPacket(self, peerAddr, code):
        if(not self.HasPeerData(peerAddr)):
            self.CreatePeerData(peerAddr)
        else:
            self.SetCurrentPeer(peerAddr)
        
        p = ReliablePacket(self.currentPeer.mySeq, self.currentPeer.mostRecentSeqRecvd, Packet.BitsToInt32(self.currentPeer.recvdSeq), code)
        self.currentPeer.mySeq += 1
        return p
    
    def SendEmptyPacket(self):
        p = self.CreateNewPacket(self.currentPeer.peerAddr, Packet.PC_EMPTY)
        self.SendPacket(p, self.currentPeer.peerAddr)
        
    def SendHeartBeats(self, task = None):
        t = time.time()
        
        for peerData in self.GetPeers():
            self.SetCurrentPeer(peerData.peerAddr)
            if(t - self.currentPeer.timeOfLastSentPacketFromUs > 0.5):
                self.SendEmptyPacket()
                #print 'Sent Heartbeat'
        
        if(task):
            return task.again
        
    def StopHeartbeats(self):
        taskMgr.remove('SendHeartBeats')
        
    
    #------------------
    # Sending Packets
    #------------------
        
    def PacketSent(self, packet, destAddr):
        self.currentPeer.sentPackets.popleft()
        self.currentPeer.sentPackets.append(PacketAndDest(packet, destAddr))
        self.currentPeer.timeOfLastSentPacketFromUs = time.time()
        
    def SendPacket(self, packet, destAddr):
        self.outgoingPacketsInLastSecond += 1
        self.outgoingBytesInLastSecond += packet.GetLength()
        self.SetCurrentPeer(destAddr)
        self._SendPacket(packet, destAddr)
            
    def _SendPacket(self, packet, destAddr):
        self.cWriter.send(packet.GetDatagram(), self.conn, destAddr)
        self.PacketSent(packet, destAddr)
                
    def ResendPacket(self, packet, destAddr):
        print 'Resent Packet'
        self.cWriter.send(packet.GetDatagram(), self.conn, destAddr)
        
#    def SendQueuedPackets(self):
#        
#        for i in xrange(min(ReliablePacketController.MAX_NUM_SEQ - 2, len(self.currentPeer.queuedStreamPackets))):
#            pad = self.currentPeer.queuedStreamPackets.popleft()
#            self._SendPacket(pad.packet, pad.destAddr)
#            
#        
#        if(len(self.currentPeer.queuedStreamPackets) < 30):
#            self.currentPeer.consecutiveStreamedPackets = len(self.currentPeer.queuedStreamPackets)    
            
    def CheckForTimedOutClients(self, task):
        t = time.time()
        for peerData in self.GetPeers():
            if(t - peerData.timestamp > 2):
                self.RemovePeerData(peerData.peerAddr)
                print 'timed out rudp', peerData.peerAddr.getIpString(), t, peerData.timestamp
                PeerTimeoutEvent(peerData.peerAddr).Fire()
                
        return task.again
    
    
    
        