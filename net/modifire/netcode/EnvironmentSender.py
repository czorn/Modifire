
from environment.ChunkOfBlocks import ChunkOfBlocks
from environment.Environment import Environment
from netcode.Packet import Packet
from event.ServerEvent import FinishedSendingEnvironmentEvent

import time

# Sends the entire environment to a client.
class EnvironmentSender():
    
    def __init__(self, peerAddr, tcp, environment):
        self.peerAddr = peerAddr
        self.tcp = tcp
        self.environment = environment
        self.x = 0
        self.y = 0
        self.z = 0
        
    def SendTask(self, task):
        for j in xrange(2):
            i = 0
            p = self.tcp.CreateNewPacket(Packet.PC_CONT_ENVIRONMENT_STREAM)
            for i in xrange(1024):
                #print self.x, self.y, self.z
                p.AddUint8(self.blocks[self.x][self.y][self.z].GetId())
                i += 1
                
                self.z = (self.z + 1) % self.numBlocksZ
                if(self.z == 0):
                    self.y = (self.y + 1) % self.numBlocksY
                    if(self.y == 0):
                        self.x = (self.x + 1) % self.numBlocksX
                        
                if(self.x == 0 and self.y == 0 and self.z == 0):
                    self.tcp.SendPacket(p, self.peerAddr)
                    p = self.tcp.CreateNewPacket(Packet.PC_END_ENVIRONMENT_STREAM)
                    self.tcp.SendPacket(p, self.peerAddr)
                    return task.done
                        
            self.tcp.SendPacket(p, self.peerAddr)
        return task.cont
#        for x in xrange(self.x, self.numBlocksX):
#            self.x = x
#            for y in xrange(self.y, self.numBlocksY):
#                self.y = y
#                for z in xrange(self.z, self.numBlocksZ):
#                    self.z = z
#                    if(i == 1024):
#                        self.tcp.SendPacket(p, self.peerAddr)
#                        p = self.tcp.CreateNewPacket(Packet.PC_CONT_ENVIRONMENT_STREAM)
#                        j += 1
#                        i = 0
#                        
#                    if(j == 2):
#                        return task.cont
#                    
#                    p.AddUint8(self.blocks[x][y][z].GetId())
#                    i += 1
#                self.z = 0
#            self.y = 0
#        self.x = 0
        #self.tcp.SendPacket(p, self.peerAddr)
        
        p = self.tcp.CreateNewPacket(Packet.PC_END_ENVIRONMENT_STREAM)
        self.tcp.SendPacket(p, self.peerAddr)
        self.tcp.CloseTCPConnection(self.peerAddr)
        return task.done
    
    def StartSendEnvironment(self):
        p = self.tcp.CreateNewPacket(Packet.PC_START_ENVIRONMENT_STREAM)
        self.blocks = self.environment.GetBlocks()
        self.numBlocksX = self.environment.GetNumBlocksX()
        self.numBlocksY = self.environment.GetNumBlocksY()
        self.numBlocksZ = self.environment.GetNumBlocksZ()
        p.AddUint16(int(((self.numBlocksX * self.numBlocksY * self.numBlocksZ) / 1024) + 1))
        p.AddUint8(self.numBlocksX)
        p.AddUint8(self.numBlocksY)
        p.AddUint8(self.numBlocksZ)
        #p.AddFixedString('asd')
        self.tcp.SendPacket(p, self.peerAddr)
        
        taskMgr.add(self.SendTask, 'SendTask')
        
#    @staticmethod
#    def ChunkNumToXYZ(chunkNum):
#        _x = 16 * 6
#        x = int(chunkNum / _x)
#        y = int((chunkNum - (_x * x)) / 6)
#        z = int(chunkNum - (_x * x) - 6 * y)
#        return (x, y, z)

#    @staticmethod
#    def SendPacket(packet, peerAddr, cWriter, conn):
#        cWriter.send(packet.GetDatagram(), conn, peerAddr)
         
#    @staticmethod   
#    def SendChunk(x, y, z, environment, peerAddr, cWriter, conn):
#        p = EnvironmentPacket(x * 16 * 6 + y * 6 + z)
#        
#        blocks = environment.GetBlocks()
#        
#        for x1 in xrange(ChunkOfBlocks.CHUNK_SIZE): 
#            for y1 in xrange(ChunkOfBlocks.CHUNK_SIZE):
#                for z1 in xrange(ChunkOfBlocks.CHUNK_SIZE):
#                    
#                    x2 = x * ChunkOfBlocks.CHUNK_SIZE + x1
#                    y2 = y * ChunkOfBlocks.CHUNK_SIZE + y1
#                    z2 = z * ChunkOfBlocks.CHUNK_SIZE + z1
#                    
#                    b = blocks[x2][y2][z2]
#                    
#                    p.AddUint8(b.GetId())
#        
#        EnvironmentSender.SendPacket(p, peerAddr, cWriter, conn)
    