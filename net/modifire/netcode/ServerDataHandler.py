from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3, Vec4 #@UnresolvedImport
from pandac.PandaModules import NetAddress
from netcode.Packet import Packet
from netcode.FileHandler import FileHandler
from netcode.PacketController import PacketController
from netcode.EnvironmentSender import EnvironmentSender
from player.PlayerState import PlayerState
from event.ServerEvent import FinishedSendingEnvironmentEvent
from event.DebugEvent import BandwidthInfoEvent
from environment.Environment import Environment
from item.ItemId import ItemId
from game.Game import Game
from time import time, sleep
import Globals
import GameTime


class ServerDataHandler(DirectObject):
    
    #-----------------
    # Initialization
    #-----------------

    def __init__(self, server):
        self.server = server
        self.log = server.log
        self.peerStr = None
        self.environmentSenders = {}
        self.gameStateNum = 0
        self.incomingPacketsInLastSecond = 0
        self.incomingBytesInLastSecond = 0
        
        self.packetActions = {
                              Packet.PC_REQUEST_JOIN : self.OnRequestJoin,
                              Packet.PC_REQUEST_ENVIRONMENT : self.OnRequestEnvironment,
                              Packet.PC_ACK_END_ENVIRONMENT_STREAM : self.OnAckEndEnvironmentStream,
                              Packet.PC_ENGINE_LOADED : self.OnEngineLoaded,
                              Packet.PC_TEAM_SELECT : self.OnTeamSelect,
                              Packet.PC_CLIENT_PLAYER_STATE : self.OnClientPlayerState,
                              Packet.PC_CLIENT_DISCONNECT : self.OnClientDisconnect,
                              Packet.PC_CLIENT_CHAT_MESSAGE : self.OnClientChatMessage,
                              Packet.PC_CLIENT_CHANGE_ITEM : self.OnClientItemChange,
                              Packet.PC_CLIENT_RELOAD : self.OnClientReload,
                              Packet.PC_EMPTY : self.OnEmptyPacket,
                              }
        
        self.accept(FinishedSendingEnvironmentEvent.EventName, self.OnFinishedSendingEnvironmentEvent)
        
        taskMgr.doMethodLater(1, self.UpdateBandwidthWatcher, 'UpdateBandwidthWatcher')
        
    def SetPacketControllers(self, reliable, unreliable, tcp):
        self.rUDP = reliable
        self.uUDP = unreliable
        self.tcp = tcp
        
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
    
    def SendEnvironment(self, peerAddr):
        self.log.WriteLine('Sending Environment to (%s)' % (self.peerStr))
        EnvironmentSender(peerAddr, self.tcp, self.server.GetEnvironment()).StartSendEnvironment()
        
    def BroadcastGameState(self, peerAddrs, playerStates):
        if(not playerStates):
            return
        
        self.gameStateNum += 1
        
        p = self.uUDP.CreateNewPacket(Packet.PC_SERVER_PLAYER_STATE)
        p.AddUint32(self.gameStateNum)

        for i, playerState in enumerate(playerStates):
            if(playerState.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
                p.AddUint8(PlayerState.START)
                p.AddUint8(playerState.GetValue(PlayerState.PID))
                p.AddUint32(GameTime.ToMilliseconds(playerState.GetValue(PlayerState.TIMESTAMP)))
                #deltaState = playerState.GetDeltaVars()
                deltaState = [PlayerState.POSITION, PlayerState.LOOKING_DIRECTION, PlayerState.IS_WALKING]
    
                for dVar in deltaState:
                    value = playerState.GetValue(dVar)
    
                    if(dVar == PlayerState.LOOKING_DIRECTION or dVar == PlayerState.POSITION):
                        p.AddUint8(dVar)
                        p.AddFloat32(value.getX())
                        p.AddFloat32(value.getY())
                        p.AddFloat32(value.getZ())
                
                playerState.GetValue(PlayerState.POSITION_HISTORY).AddPosition(playerState.GetValue(PlayerState.POSITION))
                playerState.UpdateValue(PlayerState.CURRENT_SERVER_TIME, self.gameStateNum)
        
        self.BroadcastPacket(p, peerAddrs)
        
        changes = []
        for playerState in playerStates:
            changes.append(playerState.GetReliableChanges())
            playerState.ClearDeltaVars()
        
        # Broadcast ReliablePacket
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_RELIABLE_STATE)
            p.AddUint8(len(playerStates))
            
            for i, playerState in enumerate(playerStates):
                change = changes[i]
                p.AddUint8(playerState.GetValue(PlayerState.PID))
                p.AddUint16(change)                
                
                if(change & 2**PlayerState.VICTIM):
                    player = playerState.GetValue(PlayerState.VICTIM)
                    p.AddUint8(player.GetPlayerState().GetValue(PlayerState.PID))
                    p.AddUint8(playerState.GetValue(PlayerState.VICTIM_ATTACK_TYPE))
                    
                if(change & 2**PlayerState.HEALTH):
                    p.AddUint8(playerState.GetValue(PlayerState.HEALTH))
                
                if(change & 2**PlayerState.CURRENT_ITEM):
                    p.AddUint8(playerState.GetValue(PlayerState.CURRENT_ITEM))
                    
                    item = playerState.GetPlayer().GetCurrentItem()
                    args = []
                    if(item):
                        args = item.GetItemData()
                    
                    print 'sent args', args
                    p.AddUint8(len(args))
                    for arg in args:
                        p.AddUint8(arg)
                    
                if(change & 2**PlayerState.IS_WALKING):
                    p.AddBool(playerState.GetValue(PlayerState.IS_WALKING))
                    
            self.rUDP.SendPacket(p, peerAddr)
            
        for playerState in playerStates:
            playerState.SetValue(PlayerState.VICTIM, None)
            
    def BroadcastTeamChange(self, peerAddrs, pid, teamId):
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_TEAM_SELECT)
            p.AddUint8(pid)
            p.AddUint8(teamId)
            self.rUDP.SendPacket(p, peerAddr)        
            
    # Send the scoreboard info to all players
    def BroadcastScoreboard(self, peerAddrs, playerStates):
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_SCOREBOARD)
            p.AddUint8(len(playerStates))
            
            for pState in playerStates:
                pid = pState.GetValue(PlayerState.PID)
                kills = pState.GetValue(PlayerState.KILLS)
                deaths = pState.GetValue(PlayerState.DEATHS)
                assists = pState.GetValue(PlayerState.ASSISTS)
                score = pState.GetValue(PlayerState.SCORE) / 10
                ping = int(pState.GetValue(PlayerState.PING) / 2)
                
                p.AddUint8(pid)
                p.AddUint8(kills)
                p.AddUint8(deaths)
                p.AddUint8(assists)
                p.AddUint16(score)
                p.AddUint8(ping)
                
            self.rUDP.SendPacket(p, peerAddr)
        
    def BroadcastPacket(self, packet, peerAddrs):
        for peerAddr in peerAddrs:
            self.uUDP.SendPacket(packet, peerAddr)
            
    def SendPlayerDeath(self, playerState, peerAddrs):
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_PLAYER_DEATH)
            p.AddUint8(playerState.GetValue(PlayerState.PID))
            self.rUDP.SendPacket(p, peerAddr)
            
        self.server.chat.AddMessage('[Server]: ', Vec4(0.9, 0.9, 0.9, 1), '%s died' % (self.server.GetName(peerAddr)))
            
    def SendPlayerRespawn(self, playerState, peerAddrs):
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_PLAYER_RESPAWN)
            p.AddUint8(playerState.GetValue(PlayerState.PID))
            pos = playerState.GetValue(PlayerState.POSITION)
            p.AddFloat32(pos.getX())
            p.AddFloat32(pos.getY())
            p.AddFloat32(pos.getZ())
            self.rUDP.SendPacket(p, peerAddr)
            
    def SendChatMessage(self, messageType, pid, message, peerAddrs):
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_SERVER_CHAT_MESSAGE)
            p.AddUint8(messageType)
            p.AddUint8(pid)
            p.AddFixedString(message)
            self.rUDP.SendPacket(p, peerAddr)
            
    def BroadcastEnvironmentChange(self, peerAddrs, destroyedBlocks, addedBlocks):
        print 'sent change'
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_SERVER_ENVIRONMENT_CHANGE)
        
            p.AddUint8(len(destroyedBlocks))
            for myTuple in destroyedBlocks:
                p.AddUint8(myTuple[0])
                p.AddUint8(myTuple[1])
                p.AddUint8(myTuple[2])
                p.AddUint8(myTuple[3])
            
            p.AddUint8(len(addedBlocks))
            for myTuple in addedBlocks:
                p.AddUint8(myTuple[0])
                p.AddUint8(myTuple[1])
                p.AddUint8(myTuple[2])
                p.AddUint8(myTuple[3])
                
            self.rUDP.SendPacket(p, peerAddr)
    
    def SendPlayerDisconnect(self, pid, peerAddrs):
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_PLAYER_DISCONNECT)
            p.AddUint8(pid)
            self.rUDP.SendPacket(p, peerAddr)
            
    def SendFinishedEnvironment(self, peerAddr):
        p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_END_ENVIRONMENT_STREAM)
        self.rUDP.SendPacket(p, peerAddr)
            
    def SendGoAway(self, peerAddr):
        p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_GO_AWAY)
        self.rUDP.SendPacket(p, peerAddr)
        self.server.RemovePeer(peerAddr)
            
    def SendListOfConnectedPlayers(self, peerAddr, playerStates):
        p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_CONNECTED_PLAYERS)
        p.AddUint8(len(playerStates))
        for ps in playerStates:
            p.AddUint8(ps.GetValue(PlayerState.PID))
            p.AddFixedString(ps.GetValue(PlayerState.NAME))
            p.AddUint8(ps.GetValue(PlayerState.PLAYING_STATE))
            p.AddUint8(ps.GetValue(PlayerState.TEAM))
            p.AddUint8(ps.GetValue(PlayerState.CURRENT_ITEM))
            if(ps.GetValue(PlayerState.CURRENT_ITEM) != ItemId.NoItem):
                player = ps.GetPlayer()
                args = player.currentItem.GetItemData()
                p.AddUint8(len(args))
                for arg in args:
                    p.AddUint8(arg)
            else:
                p.AddUint8(0)
        self.rUDP.SendPacket(p, peerAddr)
        
    def SendPlayerJoined(self, peerAddrs, name, pid):
        for peerAddr in peerAddrs:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_PLAYER_JOINED)
            p.AddUint8(pid)
            p.AddFixedString(name)
            self.rUDP.SendPacket(p, peerAddr)
    
    #------------------
    # Receiving Data
    #------------------    
        
    def OnDataReceived(self, data, peerAddr, code):
        self.incomingPacketsInLastSecond += 1
        self.incomingBytesInLastSecond += data.getRemainingSize()
        self.peerStr = Packet.PeerAddrToIpPort(peerAddr)
        self.packetActions[code](data, peerAddr)
        
    #-----------------------------
    # Players joining the server
    #-----------------------------
        
    def OnRequestJoin(self, data, peerAddr):        
        accepted = False
        reason = ''
        name = Packet.GetFixedString(data)
        version = Packet.GetFixedString(data)
        print 'Request to join from', name
          
        # If the server is full or the client has already joined
        if(self.server.IsFull()):
            self.log.WriteLine('Join Request Denied, Server Full (%s)' % (self.peerStr))
            reason = 'Server Full'
        elif(Packet.PeerAddrToIpPort(peerAddr) in self.server.activeClients.keys()):
            self.log.WriteLine('Request Denied, Player Already Playing (%s)' % (self.peerStr))
            reason = 'Already Playing'
        elif(version != Globals.VERSION):
            reason = 'Wrong Version'
        else:
            self.log.WriteLine('Join Request Accepted (%s)' % (self.peerStr))
            accepted = True
        
        if(accepted):
            pid = self.server.AddClient(peerAddr, name)
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_REQUEST_JOIN_RESPONSE)  
            p.AddBool(accepted)
            p.AddUint8(pid)
            self.rUDP.SendPacket(p, peerAddr)
            sleep(0.005)
            
            #self.SendEnvironment(peerAddr)
            self.SendPlayerJoined(self.server.GetAllPeerAddrs(), name, pid)
            self.server.chat.AddMessage('[Server]: ', Vec4(0.9, 0.9, 0.9, 1), '%s connected' % (name))
        else:
            p = self.rUDP.CreateNewPacket(peerAddr, Packet.PC_REQUEST_JOIN_RESPONSE)  
            p.AddBool(accepted)
            p.AddFixedString(reason)
            self.rUDP.SendPacket(p, peerAddr)
            self.server.RemovePeer(peerAddr)
            
    def OnRequestEnvironment(self, data, peerAddr):
        self.SendEnvironment(peerAddr)
        
    def OnAckEndEnvironmentStream(self, data, peerAddr):
        pass
        
            
    def OnEngineLoaded(self, data, peerAddr):
        print 'client loaded engine'
        self.log.WriteLine('Client Loaded Engine (%s)' % (self.peerStr))
        self.server.OnEngineLoaded(peerAddr)
        
    def OnTeamSelect(self, data, peerAddr):
        if(self.server.ClientIsConnected(peerAddr)):
            team = data.getUint8()
            self.server.OnTeamSelect(peerAddr, team)
            self.server.chat.AddMessage('[Server]: ', Vec4(0.9, 0.9, 0.9, 1), '%s joined team %s' % (self.server.GetName(peerAddr), team))
            self.BroadcastTeamChange(self.server.GetAllPeerAddrs(), self.server.GetActiveClient(peerAddr).pid, team)
        else:
            self.SendGoAway()
        
    def OnClientChatMessage(self, data, peerAddr):
        if(self.server.ClientIsConnected(peerAddr)):
            messageType = data.getUint8()
            message = Packet.GetFixedString(data)
            self.server.OnClientChatMessage(messageType, message, peerAddr)
            self.server.chat.AddMessage('%s: ' %  (self.server.GetName(peerAddr)), Vec4(0.9, 0, 0, 1), message)
    
    def OnClientDisconnect(self, data, peerAddr):
        if(self.server.ClientIsConnected(peerAddr)):
            print 'player left', self.server.GetName(peerAddr), ' ', time()
            self.log.WriteLine('Client disconnected (%s)' % (peerAddr))
            self.server.chat.AddMessage('[Server]: ', Vec4(0.9, 0.9, 0.9, 1), '%s disconnected' % (self.server.GetName(peerAddr)))
            self.server.OnClientDisconnect(peerAddr)
        
    def OnFinishedSendingEnvironmentEvent(self, event):
        taskMgr.doMethodLater(0.3, self.SendFinishedEnvironment, 'SendFinishedEnvironment', extraArgs = [event.GetPeerAddr()])

    def OnClientPlayerState(self, data, peerAddr):
        if(not self.server.ClientIsConnected(peerAddr)):
            return
        
        lastServerTime = data.getUint32()
        
        # Update Ping and last time
        pState = self.server.GetPlayer(self.server.GetActiveClient(peerAddr).pid).GetPlayerState()
        pState.UpdateValue(PlayerState.LAST_SERVER_TIME, lastServerTime)
        
        oldPing = pState.GetValue(PlayerState.PING)
        newPing = (self.gameStateNum -  lastServerTime) * 50
        
        pState.UpdateValue(PlayerState.PING, (newPing - oldPing) * 0.05 + oldPing)
        #print 'player ping ', lastServerTime, ' ', self.gameStateNum
        
        clientTime = GameTime.FromMilliseconds(data.getUint32())
        self.server.SetLastClientTimestamp(peerAddr, clientTime)
        keys = None
        lookingDir = None
        clicks = []
        
        while data.getRemainingSize() > 0:
            playerStateVariableCode = data.getUint8()

            if(playerStateVariableCode == PlayerState.KEYS_PRESSED):
                numKeys = data.getUint8()

                keys = []
                for i in xrange(numKeys):
                    keys.append(data.getUint8())

            if(playerStateVariableCode == PlayerState.LOOKING_DIRECTION):
                x = data.getFloat32()
                y = data.getFloat32()
                z = data.getFloat32()
                lookingDir = Vec3(x, y, z)
                
            if(playerStateVariableCode == PlayerState.CLICK_1):
                value = data.getBool()
                if(value):
                    clicks.append(PlayerState.CLICK_1)
                
            if(playerStateVariableCode == PlayerState.CLICK_3):
                value = data.getBool()
                if(value):
                    clicks.append(PlayerState.CLICK_3)
                    
#            if(playerStateVariableCode == PlayerState.CURRENT_ITEM):
#                value = data.getUint8()
#                self.server.OnClientItemChange(peerAddr, value)
        self.server.ProcessClientInput(peerAddr, keys, lookingDir, clicks, clientTime)
        
    def OnClientItemChange(self, data, peerAddr):
        newItemId = data.getUint8()
        numRemainingBytes = data.getUint8()
        extraData = []
        for i in xrange(numRemainingBytes):
            extraData.append(data.getUint8())
        self.server.OnClientItemChange(peerAddr, newItemId, extraData)   
        
    def OnClientReload(self, data, peerAddr):
        player = self.server.GetPlayer( self.server.GetActiveClient(peerAddr).pid )
        player.Reload()
        
    def OnEmptyPacket(self, data, peerAddr):
        pass

