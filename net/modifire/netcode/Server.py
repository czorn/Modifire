import sys
import random

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionReader, ConnectionWriter, NetDatagram, QueuedConnectionListener
from pandac.PandaModules import PointerToConnection, NetAddress, Vec4, Point3
from direct.task import Task
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
import Globals
from Log import Log
from netcode.ServerDataHandler import ServerDataHandler
from netcode.ReliablePacketController import ReliablePacketController
from netcode.UnreliablePacketController import UnreliablePacketController
from netcode.TCPPacketController import TCPPacketController
from netcode.Packet import Packet
from netcode.Heartbeat import Heartbeat
from player.PlayerState import PlayerState
from event.PlayerEvent import PlayerRespawnEvent
from item.ItemId import ItemId
import GameTime
from netcode.ServerFSM import ServerFSM
from gui.chat.ChatBox import ChatBox
from game.Game import Game

class ActiveClient():
    peerAddr = None
    pid = -1
    name = None
    timestamp = 0
    engineLoaded = False

class Server(DirectObject):
    
    #-----------------
    # Initialization
    #-----------------
    
    def __init__(self):
        self.log = Log()
        self.log.Open('server.txt')
        
        self.activeClients = {}
        self.nextAvailablePid = 0
        
        self.fsm = ServerFSM(self)
        self.fsm.request('LoadingEngine')
        
        self.heartbeat = Heartbeat()
        
        self.chat = ChatBox()
        
        taskMgr.doMethodLater(1, self.CheckForTimedOutClients, 'CheckForTimedOutClients')
        
    def CreateNetworkObjects(self):
        
        if(self.CreateUDPConnection() and self.CreateTCPConnection()):
            self.dataHandler = ServerDataHandler(self)
            self.reliablePacketController = ReliablePacketController(self.cWriter, self.conn, self.dataHandler, self.UDPPacketListenTask)
            self.unreliablePacketController = UnreliablePacketController(self.cWriter, self.conn, self.dataHandler)
            self.tcpPacketController = TCPPacketController(self.tcpWriter, self.tcpReader, self.cManager, self.dataHandler)
            self.dataHandler.SetPacketControllers(self.reliablePacketController, self.unreliablePacketController, self.tcpPacketController)
            
            self.ListenForIncomingTraffic()
            return True
        
        return False
    
    def CreateUDPConnection(self):   
        self.cManager = QueuedConnectionManager()
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager,0)
        self.conn = self.cManager.openUDPConnection(Globals.PORT_SERVER_LISTENER)
        
        if(self.conn):
            self.log.WriteLine('Connection on %s okay.' % (Globals.PORT_SERVER_LISTENER))
        else:
            self.log.WriteError('Connection on %s failed.' % (Globals.PORT_SERVER_LISTENER))
            sys.exit()
            return False
    
        self.cReader.addConnection(self.conn)
        
        return True
    
    def CreateTCPConnection(self):
        self.tcpSocket = self.cManager.openTCPServerRendezvous(Globals.PORT_SERVER_LISTENER, 1000)
        self.tcpWriter = ConnectionWriter(self.cManager,0)
        self.tcpListener = QueuedConnectionListener(self.cManager, 0)
        self.tcpListener.addConnection(self.tcpSocket)
        self.tcpReader = QueuedConnectionReader(self.cManager, 0)
        return True
    
    def ListenForIncomingTraffic(self):
        taskMgr.add(self.UDPPacketListenTask, "UDPPacketListenTask")
        taskMgr.add(self.TCPConnectionListenTask, "TCPConnectionListenTask", -39)
        taskMgr.add(self.TCPPacketListenTask, "TCPPacketListenTask", -40)
    
    def StartBroadcastGameState(self):
        print 'StartBroadcastGameState'
        taskMgr.doMethodLater(Globals.SERVER_SEND_DELAY, self.BroadcastGameState, "BroadcastGameState")
        taskMgr.doMethodLater(2.0, self.BroadcastScoreboard, 'BroadcastScoreboard')
        
    #----------------------
    # Listening for data
    #----------------------
        
    def UDPPacketListenTask(self, task = None):        
        while self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                data = PyDatagramIterator(datagram)
                ip = datagram.getAddress().getIpString()
                port = datagram.getAddress().getPort()
                peerAddr = NetAddress()
                peerAddr.setHost(ip, port)
                #print 'GOT UDP PACKET FROM', peerAddr.getIpString(), peerAddr.getPort()
                
                isReliable = data.getUint8()
                if(isReliable == Packet.PC_RELIABLE_PACKET):
                    self.reliablePacketController.OnPacketReceived(data, peerAddr)
                elif(isReliable == Packet.PC_UNRELIABLE_PACKET):
                    self.unreliablePacketController.OnPacketReceived(data, peerAddr)
                    
                if(self.ClientIsConnected(peerAddr)):
                    self.GetActiveClient(peerAddr).timestamp = GameTime.time
                    
        return task.cont
    
    def TCPPacketListenTask(self, task):
        if self.tcpReader.dataAvailable():
            datagram = NetDatagram()
            if self.tcpReader.getData(datagram):
                data = PyDatagramIterator(datagram)
                ip = datagram.getAddress().getIpString()
                port = datagram.getAddress().getPort()
                peerAddr = NetAddress()
                peerAddr.setHost(ip, port)
                
                packetType = data.getUint8()
                if(packetType == Packet.PC_TCP_PACKET):
                    self.tcpPacketController.OnPacketReceived(data, peerAddr)
                    
        return task.cont
    
    def TCPConnectionListenTask(self, task):
        if self.tcpListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
        
            if self.tcpListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.tcpReader.addConnection(newConnection)
                self.tcpPacketController.AddConnection(newConnection, netAddress)
        return task.cont
        
    def CheckForTimedOutClients(self, task):
        t = GameTime.GetTime()
        for ac in self.activeClients.values():
            if(t - ac.timestamp > 2):
                print 'player timed out', t, ac.timestamp
                self.OnClientDisconnect(ac.peerAddr)
                self.chat.AddMessage('[Server]: ', Vec4(0.9, 0.9, 0.9, 1), '%s timed out' % (ac.name))
                
        return task.again
        
    def IsFull(self):
        return len(self.activeClients) > Globals.MAX_PLAYERS    
    
    def BroadcastScoreboard(self, task = None):
        self.dataHandler.BroadcastScoreboard(self.GetAllPeerAddrs(), self.engine.GetPlayerController().GetAllPlayerStates()) 
        return Task.again
    
    def BroadcastGameState(self, task = None):
        peerAddrs = self.GetAllPeerAddrs()
        
        if(peerAddrs):
            self.dataHandler.BroadcastGameState(peerAddrs, self.engine.GetPlayerController().GetAllPlayerStates())
            #self.game.ClearAllDeltaStates()
        
        if(self.engine.environment.HasChanged()):
            self.dataHandler.BroadcastEnvironmentChange(self.GetAllPeerAddrs(), self.engine.environment.GetDestroyedBlocks(), self.engine.environment.GetAddedBlocks())
            self.engine.environment.ClearBlockNotifications()
        
        return Task.again
    
    def ClientIsConnected(self, peerAddr):
        return Packet.PeerAddrToIpPort(peerAddr) in self.activeClients.keys()
    
    def GetAllPeerAddrs(self):
        peerAddrs = []
        for ac in self.activeClients.values():
            if(ac.engineLoaded):
                peerAddrs.append(ac.peerAddr)
        return peerAddrs
    
    def SendPlayerDeath(self, playerState):
        peerAddrs = self.GetAllPeerAddrs()
        self.dataHandler.SendPlayerDeath(playerState, peerAddrs)
        
    def SendPlayerRespawn(self, playerState):
        peerAddrs = self.GetAllPeerAddrs()
        self.dataHandler.SendPlayerRespawn(playerState, peerAddrs)
    
    #-----------------------------
    # Handling data from clients 
    #----------------------------- 
    
    def OnEngineLoaded(self, peerAddr):
        if(self.ClientIsConnected(peerAddr)):
            ac = self.GetActiveClient(peerAddr)
            ac.timestamp = GameTime.GetTime()
            ac.engineLoaded = True
            
            self.dataHandler.SendListOfConnectedPlayers(peerAddr, self.engine.GetPlayerController().GetAllPlayerStates())
        
    def OnTeamSelect(self, peerAddr, team):
        if(self.ClientIsConnected(peerAddr)):
            ac = self.GetActiveClient(peerAddr)
            self.engine.game.AddPlayerToTeam(self.GetPlayer(ac.pid), team)
            PlayerRespawnEvent(self.engine.playerController.GetPlayer(ac.pid), Point3(random.randint(0, 8), random.randint(0, 8), 50)).Fire()
    
    def AddClient(self, peerAddr, name):
        a = ActiveClient()
        a.peerAddr = peerAddr
        a.pid = self.GetNextPid()
        a.name = name
        self.activeClients[Packet.PeerAddrToIpPort(peerAddr)] = a
        self.engine.GetPlayerController().AddNewPlayer(pid = a.pid, teamId = Game.SPECTATE, name = name)
        self.reliablePacketController.CreatePeerData(peerAddr)
        self.reliablePacketController.SetCurrentPeer(peerAddr)
#        self.reliablePacketController.AddRecvdSeqNum()
#        self.reliablePacketController.currentPeer.mostRecentSeqRecvd = 1
        Globals.CURRENT_PLAYERS = len(self.activeClients)
        
        return a.pid
    
    def OnClientChatMessage(self, messageType, message, peerAddr):
        peerAddrs = []
        for ac in self.activeClients.values():
            if(ac.engineLoaded):
                peerAddrs.append(ac.peerAddr)
        
        if(self.ClientIsConnected(peerAddr)):
            print 'message', message
            if(message.startswith('/')):
                if(message[1:] == 'save'):
                    self.engine.SaveEnvironment()
                    self.dataHandler.SendChatMessage(ChatBox.TYPE_CONSOLE, 255, 'Saving Environment...', peerAddrs)
                    return
                
            pid = self.activeClients[Packet.PeerAddrToIpPort(peerAddr)].pid
            self.dataHandler.SendChatMessage(messageType, pid, message, peerAddrs)
    
    def OnClientDisconnect(self, peerAddr):
        if(self.ClientIsConnected(peerAddr)):
            pid = self.activeClients[Packet.PeerAddrToIpPort(peerAddr)].pid
            self.engine.GetPlayerController().RemovePlayer(pid)
            self.RemovePeer(peerAddr)
            
            self.dataHandler.SendPlayerDisconnect(pid, self.GetAllPeerAddrs())
            self.engine.SaveEnvironment()
        Globals.CURRENT_PLAYERS = len(self.activeClients)
        
    def OnClientItemChange(self, peerAddr, itemId, extraData):
        pid = self.GetActiveClient(peerAddr).pid
        player = self.GetPlayer(pid)
        print 'server item change', player, itemId
        self.engine.GetPlayerController().OtherPlayerItemChange(player, itemId, extraData)
            
    def RemovePeer(self, peerAddr):
        self.reliablePacketController.RemovePeerData(peerAddr)
        self.unreliablePacketController.RemovePeerData(peerAddr)
        if(self.ClientIsConnected(peerAddr)):
            del self.activeClients[Packet.PeerAddrToIpPort(peerAddr)]
    
    def ProcessClientInput(self, peerAddr, keys, lookingDir, clicks, timestamp):
        if(self.ClientIsConnected(peerAddr)):
            pid = self.GetActiveClient(peerAddr).pid
            self.engine.GetPlayerController().QueueClientInput(self.GetPlayer(pid), keys, lookingDir, clicks, timestamp)
        
    def SetLastClientTimestamp(self, peerAddr, timestamp):
        if(self.ClientIsConnected(peerAddr)):
            self.GetActiveClient(peerAddr).timestamp = timestamp
        
    def GetEnvironment(self):
        return self.engine.environment
    
    def GetNextPid(self):
        self.nextAvailablePid += 1
        return self.nextAvailablePid
    
    def GetPlayer(self, pid):
        return self.engine.GetPlayerController().GetPlayer(pid)
    
    def GetName(self, peerAddr):
        if(self.ClientIsConnected(peerAddr)):
            return self.GetActiveClient(peerAddr).name
        else:
            return 'NOT A PLAYER'
    
    def GetActiveClient(self, peerAddr):
        return self.activeClients[Packet.PeerAddrToIpPort(peerAddr)]
    
    def Exit(self):
        self.log.Close()