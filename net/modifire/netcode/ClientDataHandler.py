
from pandac.PandaModules import Vec3
from direct.showbase.DirectObject import DirectObject

import Globals
import Settings
import GameTime

from game.Game import Game
from player.PlayerState import PlayerState
from netcode.Packet import Packet
from netcode.EnvironmentReceiver import EnvironmentReceiver
from environment.MapInfo import MapInfo
from event.PlayerEvent import PlayerDeathEvent, PlayerRespawnEvent, PlayerJoinEvent, PlayerDisconnectEvent, PlayerHitEvent, PlayerReloadEvent
from event.ChatEvent import ChatReceivedEvent, ChatEnteredEvent, ChatDeathEvent
from event.ClientEvent import ServerJoinResponseEvent, TeamSelectEvent, LoadProgressEvent, ListOfConnectedPlayersReceivedEvent
from event.EnvironmentEvent import EnvironmentChangeEvent
from event.InventoryEvent import SelectedItemChangeEvent, SelectedItemAttributeChangeEvent
from event.DebugEvent import BandwidthInfoEvent
from item.ItemId import ItemId
from item.Builder import Builder


class ClientDataHandler(DirectObject):
    
    #-----------------
    # Initialization
    #-----------------
    
    def __init__(self, client):
        self.client = client 
        self.log = client.log
        self.peerStr = None
        self.serverAddr = None
        self.lastProgressHeartBeatTime = 0
        self.progressHeartBeatDelay = 0.3
        self.environmentReceiver = None
        self.lastServerTime = 0
        self.incomingPacketsInLastSecond = 0
        self.incomingBytesInLastSecond = 0
        
        self.packetActions = {
                              Packet.PC_REQUEST_JOIN_RESPONSE : self.OnRequestJoinResponse,
                              Packet.PC_START_ENVIRONMENT_STREAM : self.OnStartEnvironmentStream,
                              Packet.PC_CONT_ENVIRONMENT_STREAM : self.OnContinuteEnvironmentStream,
                              Packet.PC_END_ENVIRONMENT_STREAM : self.OnEndEnvironmentStream,
                              Packet.PC_WORLD_SEED : self.OnWorldSeed,
                              Packet.PC_PLAYER_DEATH : self.OnPlayerDeath,
                              Packet.PC_PLAYER_RESPAWN : self.OnPlayerRespawn,
                              Packet.PC_CONNECTED_PLAYERS : self.OnListOfConnectedPlayers,
                              Packet.PC_PLAYER_JOINED : self.OnPlayerJoined,
                              Packet.PC_SERVER_PLAYER_STATE : self.OnServerPlayerStates,
                              Packet.PC_RELIABLE_STATE : self.OnReliableGameState,
                              Packet.PC_PLAYER_DISCONNECT : self.OnPlayerDisconnect,
                              Packet.PC_SERVER_CHAT_MESSAGE : self.OnServerChatMessage,
                              Packet.PC_SERVER_ENVIRONMENT_CHANGE : self.OnServerEnvironmentChange,
                              Packet.PC_SCOREBOARD : self.OnScoreboardUpdate,
                              Packet.PC_TEAM_SELECT : self.OnPlayerTeamChange,
                              Packet.PC_GO_AWAY : self.OnGoAway, 
                              Packet.PC_EMPTY : self.OnEmptyPacket
                              }
        
        self.accept(TeamSelectEvent.EventName, self.SendSelectedTeam)
        self.accept(ChatEnteredEvent.EventName, self.SendChatMessage)
        self.accept(LoadProgressEvent.EventName, self.OnLoadProgressEvent)
        self.accept(SelectedItemChangeEvent.EventName, self.SendCurrentItemChange)
        self.accept(SelectedItemAttributeChangeEvent.EventName, self.SendCurrentItemChange)
        
        # This is bad - find a better way to notify of reload
        self.accept(PlayerReloadEvent.EventName, self.SendReload)
        
        taskMgr.doMethodLater(1, self.UpdateBandwidthWatcher, 'UpdateBandwidthWatcher')
    
    def SetPacketControllers(self, reliable, unreliable, tcp):
        self.rUDP = reliable
        self.uUDP = unreliable
        self.tcp = tcp
        
    def SetServerAddress(self, serverAddr):
        self.serverAddr = serverAddr
        self.peerStr = Packet.PeerAddrToIpPort(serverAddr)
        
    def UpdateBandwidthWatcher(self, task):
        outgoingBytes = self.rUDP.outgoingBytesInLastSecond + self.uUDP.outgoingBytesInLastSecond
        outgoingPackets = self.rUDP.outgoingPacketsInLastSecond + self.uUDP.outgoingPacketsInLastSecond
        BandwidthInfoEvent('%skB/s %s p' % (self.incomingBytesInLastSecond / 1000.0, self.incomingPacketsInLastSecond),
                           '%skB/s %s p' % (outgoingBytes / 1000.0, outgoingPackets)).Fire()
#        print 'Incoming: %skB/s %s packets' % (self.incomingBytesInLastSecond / 1000.0, self.incomingPacketsInLastSecond)
#        print 'Outgoing: %skB/s %s packets' % (outgoingBytes / 1000.0, outgoingPackets)
        self.incomingBytesInLastSecond = 0
        self.incomingPacketsInLastSecond = 0
        self.rUDP.ClearBandwidthInfo()
        self.uUDP.ClearBandwidthInfo()
        return task.again
        
    #----------------
    # Sending Data
    #----------------
    
    def SendRequestToJoinServer(self):
        """ Send a request to the server to join the game.
        Packet contains desired name.
        """
            
        self.log.WriteLine('Requesting to join server (%s)' % (self.peerStr))
        #p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_REQUEST_JOIN)
        p = self.uUDP.CreateNewPacket(Packet.PC_REQUEST_JOIN)
        p.AddFixedString(Settings.NAME)
        p.AddFixedString(Globals.VERSION)
        self.uUDP.SendPacket(p, self.serverAddr)
        self.rUDP.CreatePeerData(self.serverAddr)
        self.rUDP.SetCurrentPeer(self.serverAddr)
        #self.rUDP.SendPacket(p, self.serverAddr)
        
    def SendRequestForEnvironment(self):
        self.tcp.OpenTCPConnection(self.serverAddr)
        p = self.tcp.CreateNewPacket(Packet.PC_REQUEST_ENVIRONMENT)
        self.tcp.SendPacket(p, self.serverAddr)
    
    def SendEngineLoaded(self):
        """ Let the server know we loaded the engine
        so that it can start to send us data.
        """
        if(not Globals.OFFLINE):
            self.log.WriteLine('Sending Engine Loaded (%s)' % (self.peerStr))
            p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_ENGINE_LOADED)
            self.rUDP.SendPacket(p, self.serverAddr)
    
    def SendSelectedTeam(self, event):
        team = event.GetTeam()
        
        if(not Globals.OFFLINE):
            self.log.WriteLine('Sending Desired Team (%s)' % (self.peerStr))
            p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_TEAM_SELECT)
            p.AddUint8(team)
            self.rUDP.SendPacket(p, self.serverAddr)
    
    def SendInputCommands(self, currentTime, myInput, myState):
        p = self.uUDP.CreateNewPacket(Packet.PC_CLIENT_PLAYER_STATE)
        p.AddUint32(self.lastServerTime)
        p.AddUint32(GameTime.ToMilliseconds(currentTime))
        
        p.AddUint8(PlayerState.KEYS_PRESSED)
        value = myInput.GetKeys()
        length = len(value)
        p.AddUint8(length)
        for key in value:
            p.AddUint8(key)
            
        p.AddUint8(PlayerState.LOOKING_DIRECTION)
        value = myInput.GetLookingDir()
        p.AddFloat32(value.getX())
        p.AddFloat32(value.getY())
        p.AddFloat32(value.getZ())
        
        p.AddUint8(PlayerState.CLICK_1)
        p.AddBool(myInput.click1)
        
        p.AddUint8(PlayerState.CLICK_3)
        p.AddBool(myInput.click3)
        
#        p.AddUint8(PlayerState.CURRENT_ITEM)
#        p.AddUint8(myState.GetValue(PlayerState.CURRENT_ITEM))
        
        #taskMgr.doMethodLater(0.6, self.uUDP.SendPacket, 'asd', extraArgs=[p, self.serverAddr])
        self.uUDP.SendPacket(p, self.serverAddr)
        
    def SendReload(self, event):
        if(not Globals.OFFLINE):
            p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_CLIENT_RELOAD)
            self.rUDP.SendPacket(p, self.serverAddr)
        
    def SendChatMessage(self, event):
        messageType = event.GetMessageType()
        message = event.GetMessage()
        if(self.serverAddr):
            p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_CLIENT_CHAT_MESSAGE)
            p.AddUint8(messageType)
            p.AddFixedString(message)
            self.rUDP.SendPacket(p, self.serverAddr)
    
    def SendClientDisconnect(self):
        self.log.WriteLine('Voluntarily disconnecting from server (%s)' % (self.peerStr))
        p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_CLIENT_DISCONNECT)
        self.rUDP.SendPacket(p, self.serverAddr)
        self.RemoveServer()
        
    def SendCurrentItemChange(self, event):
        if(self.serverAddr and self.rUDP.HasPeerData(self.serverAddr)):
            args = []
            
            if(event.GetItemStack()):
                item = event.GetItemStack().GetItem()
                args = item.GetItemData()
            else:
                item = None
                
            p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_CLIENT_CHANGE_ITEM)
            if(item):
                p.AddUint8(item.GetItemId())
            else:
                p.AddUint8(ItemId.NoItem)
            
            p.AddUint8(len(args))
            for arg in args:
                p.AddUint8(arg)
                
            print 'sending change item', item
            self.rUDP.SendPacket(p, self.serverAddr)  
    
    def RemoveServer(self):
        self.rUDP.RemovePeerData(self.serverAddr)
        self.uUDP.RemovePeerData(self.serverAddr)
        self.serverAddr = None
    
    #------------------
    # Receiving Data
    #------------------
        
    def OnDataReceived(self, data, peerAddr, code):
        self.incomingPacketsInLastSecond += 1
        self.incomingBytesInLastSecond += data.getRemainingSize()
        
        self.packetActions[code](data)
        
    def OnEnvironmentPacket(self, data):
        if(self.environmentReceiver):
            self.environmentReceiver.OnPacketReceived(data)
        
    def OnStartEnvironmentStream(self, data):
        totalPackets = data.getUint16()
        xmax = data.getUint8()
        ymax = data.getUint8()
        zmax = data.getUint8()
        Globals.MAP_INFO = MapInfo('', [xmax, ymax, zmax], None, None)
        self.environmentReceiver = EnvironmentReceiver(totalPackets, xmax, ymax, zmax)
        #self.environmentReceiver.OnPacketReceived(data)
    
    def OnContinuteEnvironmentStream(self, data):
        #print 'cont stream'
        self.environmentReceiver.OnPacketReceived(data)
        
    def OnEndEnvironmentStream(self, data):
        if(self.environmentReceiver):
            Globals.BLOCKS = self.environmentReceiver.GetBlocks()
            del self.environmentReceiver
            self.tcp.CloseTCPConnection(self.serverAddr)
            p = self.rUDP.CreateNewPacket(self.serverAddr, Packet.PC_ACK_END_ENVIRONMENT_STREAM)
            self.rUDP.SendPacket(p, self.serverAddr)
            self.client.LoadEngine()
    
    def OnWorldSeed(self, data):
        print self.client.fsm.state
        if(self.client.fsm.state == 'WaitingForEnvironment'):
            print 'Got World Seed'
            Globals.WORLD_SEED = Packet.GetFixedString(data)
            self.client.LoadEngine()
        else:
            self.rUDP.SendEmptyPacket()
        
    def OnPlayerDeath(self, data):
        pid = data.getUint8()
        #PlayerDeathEvent(self.client.GetPlayer(pid)).Fire()
        
    def OnPlayerRespawn(self, data):
        pid = data.getUint8()
        x = data.getUint32()
        y = data.getFloat32()
        z = data.getFloat32()
        player = self.client.GetPlayer(pid)
        if(player):
            PlayerRespawnEvent(player, Vec3(x, y, z)).Fire()
        #self.client.engine.OnPlayerRespawn(pid, Vec3(x, y, z))
        
    def OnPlayerJoined(self, data):
        pid = data.getUint8()
        name = Packet.GetFixedString(data)
        PlayerJoinEvent(None, pid, name, PlayerState.PS_SPECTATE, Game.SPECTATE, ItemId.NoItem, []).Fire()
        print 'Got Player Joined', pid, name
        
    def OnListOfConnectedPlayers(self, data):
        numPlayers = data.getUint8()
        for i in xrange(numPlayers):
            pid = data.getUint8()
            name = Packet.GetFixedString(data)
            playingState = data.getUint8()
            teamId = data.getUint8()
            currentItem = data.getUint8()
            numRemainingBytes = data.getUint8()
            extraData = []
            for i in xrange(numRemainingBytes):
                extraData.append(data.getUint8())
            
            if(pid != Globals.MY_PID):
                PlayerJoinEvent(None, pid, name, playingState, teamId, currentItem, extraData).Fire()
                
            ListOfConnectedPlayersReceivedEvent(self.client.engine.GetPlayerController().GetAllPlayerStates()).Fire()
        
    def OnServerChatMessage(self, data):
        messageType = data.getUint8()
        pid = data.getUint8()
        message = Packet.GetFixedString(data)
        print 'got message', message
        ChatReceivedEvent(messageType, self.client.GetPlayer(pid), message).Fire()
        #self.client.OnServerChatMessage(messageType, pid, message)
        
    def OnPlayerDisconnect(self, data):
        pid = data.getUint8()
        PlayerDisconnectEvent(self.client.GetPlayer(pid)).Fire()
        #self.client.OnPlayerDisconnect(pid)

    def OnRequestJoinResponse(self, data):
        """ When the server responds letting us know if we
        can join. Packet contains True or False.
        """
        
        reason = ''
        response = data.getBool()
        if(response):
            Globals.MY_PID = data.getUint8()
            print 'Can join server', Globals.MY_PID
            self.SendRequestForEnvironment()
        else:
            reason = Packet.GetFixedString(data)
            self.rUDP.RemovePeerData(self.serverAddr)
        ServerJoinResponseEvent(response, reason).Fire()
        
    def OnReliableGameState(self, data):
        playerController = self.GetPlayerController()
        myself = playerController.GetMyself()
        
        numPlayers = data.getUint8()
        for i in xrange(numPlayers):
            pid = data.getUint8()
            change = data.getUint16()
            player = self.GetPlayer(pid)
            
            if(change & 2**PlayerState.USED_ITEM):
                if(player != myself):
                    playerController.OtherPlayerInteraction(player, True, False)
            
            if(change & 2**PlayerState.VICTIM):
                victimPid = data.getUint8()
                typeThing = data.getUint8()
                victim = self.GetPlayer(victimPid)
                print victim, typeThing
                
                if(typeThing == PlayerState.VAT_KILLSHOT):
                    PlayerDeathEvent(victim, player, False).Fire()
                elif(typeThing == PlayerState.VAT_BOTH):
                    PlayerDeathEvent(victim, player, True).Fire()
                PlayerHitEvent(player, victim, False).Fire()
                
                if(player != myself):
                    playerController.OtherPlayerInteraction(player, True, False)
                    
            if(change & 2**PlayerState.HEALTH):
                health = data.getUint8()
                playerController.HealthChange(player, health)
            
            if(change & 2**PlayerState.CURRENT_ITEM):
                itemId = data.getUint8()
                numRemainingBytes = data.getUint8()
                extraData = []
                for i in xrange(numRemainingBytes):
                    extraData.append(data.getUint8())
                print 'got args', extraData
                if(player != myself):
                    playerController.OtherPlayerItemChange(player, itemId, extraData)
                
            if(change & 2**PlayerState.IS_WALKING):
                isWalking = data.getBool()
                if(player != myself):
                    playerController.OtherPlayerWalkingChange(player, isWalking)
                    
            #print pid, changes
            
#            for playerStateVariableCode, wasChanged in enumerate(changeArray):
#                psvc = 15 - playerStateVariableCode 
#                if(wasChanged == '1'):
#                    
#                    if(psvc == PlayerState.USED_ITEM):
#                        print 'used item'
#                        if(player != myself):
#                            playerController.OtherPlayerInteraction(player, True, False)
#                    
#                    elif(psvc == PlayerState.CURRENT_ITEM):
#                        itemId = data.getUint8()
#                        print 'new item', itemId
#                        if(player != myself):
#                            playerController.OtherPlayerItemChange(player, itemId)
#                    
#                    elif(psvc == PlayerState.IS_WALKING):
#                        isWalking = data.getBool()
#                        print 'iswalking', isWalking
#                        if(player != myself):
#                            playerController.OtherPlayerWalkingChange(player, isWalking)
#                    
#                    elif(psvc == PlayerState.HEALTH):
#                        health = data.getUint8()
#                        print 'health', health
#                        pass
#                    
#                    elif(psvc == PlayerState.VICTIM):
#                        victimPid = data.getUint8()
#                        typeThing = data.getUint8()
#                        print 'victim', victimPid, typeThing
#                        PlayerDeathEvent(self.GetPlayer(victimPid), player, False).Fire()
#                        if(typeThing == PlayerState.VAT_KILLSHOT):
#                            PlayerDeathEvent(self.GetPlayer(victimPid), player, False).Fire()
#                        elif(typeThing == PlayerState.VAT_BOTH):
#                            PlayerDeathEvent(self.GetPlayer(victimPid), player, True).Fire()

    def OnServerPlayerStates(self, data):
        currentPlayerId = -1
        playerStates = {}
        
        self.lastServerTime = data.getUint32()

        while data.getRemainingSize() > 0:
            playerStateVariableCode = data.getUint8()

            if(playerStateVariableCode == PlayerState.START):
                currentPlayerId = data.getUint8()
                lastClientTime = GameTime.FromMilliseconds(data.getUint32())
                playerStates[currentPlayerId] = PlayerState(None, True)
                playerStates[currentPlayerId].SetValue(PlayerState.TIMESTAMP, lastClientTime)

            if(playerStateVariableCode == PlayerState.POSITION):
                x = data.getFloat32()
                y = data.getFloat32()
                z = data.getFloat32()
                playerStates[currentPlayerId].SetValue(PlayerState.POSITION, Vec3(x, y, z))

            if(playerStateVariableCode == PlayerState.LOOKING_DIRECTION):
                x = data.getFloat32()
                y = data.getFloat32()
                z = data.getFloat32()
                playerStates[currentPlayerId].SetValue(PlayerState.LOOKING_DIRECTION, Vec3(x, y, z))

        self.client.CompareSnapshots(playerStates)

        self.client.HandleServerPlayerStates(playerStates)
        
    def OnScoreboardUpdate(self, data):
        numPlayers = data.getUint8()
        
        for i in xrange(numPlayers):
            pid = data.getUint8()
            kills = data.getUint8()
            deaths = data.getUint8()
            assists = data.getUint8()
            score = data.getUint16()
            ping = data.getUint8() * 2
            
            self.client.engine.scoreboard.UpdateRow(pid = pid, kills = kills, deaths = deaths, assists = assists, score = score, ping = ping)
            
    def OnPlayerTeamChange(self, data):
        pid = data.getUint8()
        teamId = data.getUint8()
        self.client.GetPlayer(pid).OnTeamChange(teamId)
        if(pid == Globals.MY_PID):
            self.GetPlayerController().ResetPlayerNames()
        
        # This is bad
        self.client.engine.scoreboard.UpdateTeam(pid, teamId)
        print 'TEAM CHANGE', pid, teamId

    def OnServerEnvironmentChange(self, data):
        numDestroyed = data.getUint8()
        
        destroyedBlocks = []
        for i in xrange(numDestroyed):
            x = data.getUint8()
            y = data.getUint8()
            z = data.getUint8()
            bid = data.getUint8()
            destroyedBlocks.append((x, y, z, bid))
            
        numAdded = data.getUint8()
        
        addedBlocks = []
        for i in xrange(numAdded):
            x = data.getUint8()
            y = data.getUint8()
            z = data.getUint8()
            bid = data.getUint8()
            addedBlocks.append((x, y, z, bid))
            
        EnvironmentChangeEvent(destroyedBlocks, addedBlocks).Fire()
        
    def OnGoAway(self, data):
        messenger.send('goBackToMain')
        
    def OnLoadProgressEvent(self, event):
        if(GameTime.GetTime() - self.lastProgressHeartBeatTime > self.progressHeartBeatDelay):
            self.lastProgressHeartBeatTime = GameTime.GetTime()
            self.rUDP.SendHeartBeats()
            
      
        
    def OnEmptyPacket(self, data):
        pass
    
    def GetPlayerController(self):
        return self.client.engine.GetPlayerController()
    
    def GetPlayer(self, pid):
        return self.GetPlayerController().GetPlayer(pid)