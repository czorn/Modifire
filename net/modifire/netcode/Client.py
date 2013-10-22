from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionReader, ConnectionWriter, NetAddress, NetDatagram
from direct.task import Task
from direct.distributed.PyDatagramIterator import PyDatagramIterator
import Globals
from Log import Log
import Settings
from ClientFSM import ClientFSM
from event.ClientEvent import LoadEngineEvent, ServerJoinResponseEvent
from netcode.ClientSnapshotHandler import ClientSnapshotHandler
from netcode.Snapshot import Snapshot
from netcode.ClientDataHandler import ClientDataHandler
from netcode.ReliablePacketController import ReliablePacketController
from netcode.UnreliablePacketController import UnreliablePacketController
from netcode.TCPPacketController import TCPPacketController
from netcode.Packet import Packet
from event.ClientEvent import EngineLoadedEvent
from player.PlayerState import PlayerState
import copy

class Client(DirectObject):
    
    #-----------------
    # Initialization
    #-----------------

    def __init__(self):
        self.log = Log()
        self.log.Open('client.txt')

        self.clientSnapshotHandler = ClientSnapshotHandler()
        
        self.accept(EngineLoadedEvent.EventName, self.OnEngineLoadedEvent)

        self.fsm = ClientFSM(self)
        self.fsm.request('CreateNetworkObjects')
        
        self.lastServerPacketTimestamp = 0
        

    def CreateNetworkObjects(self):
        if(self.CreateUDPConnection() and self.CreateTCPConnection()):
            self.dataHandler = ClientDataHandler(self)
            self.reliablePacketController = ReliablePacketController(self.cWriter, self.conn, self.dataHandler)
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
        self.conn = self.cManager.openUDPConnection(Globals.PORT_CLIENT_LISTENER)

        if(self.conn):
            self.log.WriteLine('Connection on %s okay.' % (Globals.PORT_CLIENT_LISTENER))
        else:
            self.log.WriteError('Connection on %s failed.' % (Globals.PORT_CLIENT_LISTENER))
            Globals.PORT_CLIENT_LISTENER += 1
            self.log.WriteError('Retrying on %s .' % (Globals.PORT_CLIENT_LISTENER))
            self.conn = self.cManager.openUDPConnection(Globals.PORT_CLIENT_LISTENER)
            if(self.conn):
                self.log.WriteLine('Connection on %s okay.' % (Globals.PORT_CLIENT_LISTENER))
            else:
                self.log.WriteError('Connection on %s failed.' % (Globals.PORT_CLIENT_LISTENER))
                self.log.WriteError('Connection unsuccessful, exiting Client')
                return False

        self.cReader.addConnection(self.conn)

        return True
    
    def CreateTCPConnection(self):
        self.tcpWriter = ConnectionWriter(self.cManager,0)
        self.tcpReader = QueuedConnectionReader(self.cManager, 0)
        return True
    
    #---------------------
    # Listening for data
    #---------------------

    def ListenForIncomingTraffic(self):
        taskMgr.add(self.UDPPacketListenTask, "UDPPacketListenTask")
        taskMgr.add(self.TCPPacketListenTask, "TCPPacketListenTask", -40)

    def UDPPacketListenTask(self, task):
        while self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                #print 'PACKET', datagram
                data = PyDatagramIterator(datagram)
                ip = datagram.getAddress().getIpString()
                port = datagram.getAddress().getPort()
                peerAddr = NetAddress()
                peerAddr.setHost(ip, port)
                
                packetType = data.getUint8()
                if(packetType == Packet.PC_RELIABLE_PACKET):
                    self.reliablePacketController.OnPacketReceived(data, peerAddr)
                elif(packetType == Packet.PC_UNRELIABLE_PACKET):
                    self.unreliablePacketController.OnPacketReceived(data, peerAddr)
                elif(packetType == Packet.PC_ENVIRONMENT_PACKET):
                    self.dataHandler.OnDataReceived(data, peerAddr, Packet.PC_ENVIRONMENT_PACKET)

        return Task.cont
    
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
    
    #---------------
    # Sending Data
    #---------------
    
    def ConnectToServer(self, serverAddress):
        self.fsm.request('WaitingForJoinResponse')
        self.log.WriteLine('Requesting to join server (%s)' % serverAddress)
        serverAddr = NetAddress()
        serverAddr.setHost(serverAddress, Globals.PORT_SERVER_LISTENER)
        self.dataHandler.SetServerAddress(serverAddr)
        self.dataHandler.SendRequestToJoinServer()
        self.acceptOnce(ServerJoinResponseEvent.EventName, self.OnServerJoinResponseEvent)
        taskMgr.doMethodLater(1.8, self.OnRequestJoinTimeout, 'serverJoinTimeout', extraArgs = [False])

#    def SendChatMessage(self, messageType, message):
#        self.dataHandler.SendChatMessage(messageType, message)
        
#    def OnServerChatMessage(self, messageType, pid, message):
#        self.engine.OnServerChatMessage(messageType, pid, message)
    
    def SendInput(self, currentTime, myInput, myState):
        self.dataHandler.SendInputCommands(currentTime, myInput, myState)
        #self.game.ClearMyClicking()
        
#    def SendSelectedTeam(self, team):
#        self.dataHandler.SendSelectedTeam(team)

    def StoreSnapshot(self, t, myInput, myState):
        #myInput.SetTimestamp(t)
        
        snapshot = Snapshot(myInput,
                            myState.GetValue(PlayerState.POSITION),
                            t)
        
        self.clientSnapshotHandler.AddSnapshot(snapshot)
    
    def HandleEnvironmentChange(self, destroyed, added):
        self.engine.HandleEnvironmentChange(destroyed, added)

    def HandleServerPlayerStates(self, playerStates):
        if(self.engine is not None):
            self.engine.GetPlayerController().HandleServerPlayerStates(playerStates)

#    def UpdatePlayerState(self, playerId, key, value):
#        self.engine.UpdatePlayerState(playerId, key, value)
        
#    def OnPlayerDisconnect(self, pid):
#        self.engine.RemovePlayer(pid)
        
#    def OnConnectedPlayers(self, players):
#        for player in players:
#            self.engine.AddNewPlayer(player[0], player[1])

    def CompareSnapshots(self, playerStates):
            if(self.engine is not None):
                if(Globals.MY_PID in playerStates.keys()):
                    myState = playerStates[Globals.MY_PID]
                    oldStates = self.clientSnapshotHandler.GetOldStates(myState.GetValue(PlayerState.TIMESTAMP))
                    self.engine.GetPlayerController().VerifyPrediction(copy.deepcopy(myState), oldStates)

    def OnRequestJoinTimeout(self, task):
        taskMgr.remove('serverJoinTimeout')
        self.reliablePacketController.RemovePeerData(self.dataHandler.serverAddr)
        self.unreliablePacketController.RemovePeerData(self.dataHandler.serverAddr)
        ServerJoinResponseEvent(False, 'Server could not be reached.').Fire()
        
    def OnServerJoinResponseEvent(self, event):
        #self.fsm.request('WaitingForEnvironment')
        print 'removed timeout message'
        taskMgr.remove('serverJoinTimeout')
        
    def LoadEngine(self):
        LoadEngineEvent().Fire()
    
    def OnEngineLoadedEvent(self, event):
        self.dataHandler.SendEngineLoaded()
        
    def GetPlayer(self, pid):
        return self.engine.GetPlayerController().GetPlayer(pid)

    def Disconnect(self):
        self.fsm.request('Idle', 'Left Server')
        
    def CleanUp(self):
        self.reliablePacketController.CleanUp()
        self.unreliablePacketController.CleanUp()

    def Exit(self):
        self.log.Close()

