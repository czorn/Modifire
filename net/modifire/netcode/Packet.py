from direct.distributed.PyDatagram import PyDatagram

class Packet():
    
    (
    PC_REQUEST_ENVIRONMENT,
    PC_START_ENVIRONMENT_STREAM,
    PC_CONT_ENVIRONMENT_STREAM,
    PC_END_ENVIRONMENT_STREAM,
    PC_ACK_END_ENVIRONMENT_STREAM,
    PC_WORLD_SEED,
    PC_ENGINE_LOADED,
    PC_TEAM_SELECT,
    PC_PLAYER_DEATH,
    PC_PLAYER_RESPAWN,
    PC_REQUEST_INFO,
    PC_REQUEST_RESPONSE,
    PC_SERVER_INFO,
    PC_REQUEST_JOIN,
    PC_REQUEST_JOIN_RESPONSE,
    PC_PLAYER_JOINED,
    PC_CONNECTED_PLAYERS,
    PC_CLIENT_PLAYER_STATE,
    PC_SERVER_PLAYER_STATE,
    PC_CLIENT_READY,
    PC_CLIENT_CHANGE_ITEM,
    PC_CLIENT_RELOAD,
    PC_GAME_STATE,
    PC_RELIABLE_STATE,
    PC_CLIENT_DISCONNECT,
    PC_GO_AWAY,
    PC_PLAYER_DISCONNECT,
    PC_CLIENT_CHAT_MESSAGE,
    PC_SERVER_CHAT_MESSAGE,
    PC_SERVER_ENVIRONMENT_CHANGE,
    PC_SCOREBOARD,
    PC_UNRELIABLE_PACKET,
    PC_RELIABLE_PACKET,
    PC_TCP_PACKET,
    PC_EMPTY
    ) = range(35)
    
    def __init__(self):
        self.dg = PyDatagram()
        
    def AddBool(self, value):
        if(value):
            self.dg.addBool(True)
        else:
            self.dg.addBool(False)
        
    def AddUint8(self, value):
        self.dg.addUint8(value)
        
    def AddUint16(self, value):
        self.dg.addUint16(value)
        
    def AddUint32(self, value):
        self.dg.addUint32(value)
        
    def AddFloat32(self, value):
        self.dg.addFloat32(value)
        
    def GetDatagram(self):
        return self.dg
    
    def GetDatagramSize(self):
        return self.dg.getLength()
    
    def AddFixedString(self, text):
        n = len(text)
        self.dg.addUint8(n)
        self.dg.addFixedString(text, n)
        
    def AddString(self, text):
        self.dg.addFixedString(text, len(text))
        
    def GetLength(self):
        return self.dg.getLength()
        
    @staticmethod
    def GetFixedString(data):
        length = data.getUint8()
        return data.getFixedString(length)
    
    @staticmethod
    def GetRemainingAsString(data):
        length = data.getRemainingSize()
        return data.getFixedString(length)
    
    @staticmethod
    def PeerAddrToIpPort(peerAddr):
        return '%s:%s' % (peerAddr.getIpString(), peerAddr.getPort())
    
    @staticmethod
    def BitsToInt16(bits):
        return int(''.join(bits), 2)
    
    @staticmethod
    def BitsToInt32(bits):
        return int(''.join(bits), 2)
    
    @staticmethod
    # http://www.daniweb.com/software-development/python/code/216539
    def Int16ToBits(int16):
        return list(''.join([str((int16 >> y) & 1) for y in range(16-1, -1, -1)]))
    
    @staticmethod
    def Int32ToBits(int32):
        return list(''.join([str((int32 >> y) & 1) for y in range(32-1, -1, -1)]))

class UnreliablePacket(Packet):
    
    def __init__(self, seq, code):
        Packet.__init__(self)
        self.dg.addUint8(Packet.PC_UNRELIABLE_PACKET)
        self.dg.addUint8(seq)
        self.dg.addUint8(code)
        
class ReliablePacket(Packet):
    
    def __init__(self, mySeq, lastSeq, seqBits, code):
        Packet.__init__(self)
        self.dg.addUint8(Packet.PC_RELIABLE_PACKET)
        self.dg.addUint32(mySeq)
        self.dg.addUint32(lastSeq)
        self.dg.addUint32(seqBits)
        self.dg.addUint8(code)
        
class EnvironmentPacket(Packet):
    
    def __init__(self, chunkNumber):
        Packet.__init__(self)
        self.dg.addUint8(Packet.PC_ENVIRONMENT_PACKET)
        self.dg.addUint16(chunkNumber)
        
class TCPPacket(Packet):
    def __init__(self, code):
        Packet.__init__(self)
        self.dg.addUint8(Packet.PC_TCP_PACKET)
        self.dg.addUint8(code)
    
    