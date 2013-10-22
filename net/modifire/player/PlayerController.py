from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import VBase3, Point3, Vec3
import random

from time import time
from collections import deque
from player.Player import Player
from player.PlayerState import PlayerState
from player.Input import Input
from player.CollisionDummy import CollisionDummy
from event.ClientEvent import TeamSelectEvent
from event.CameraEvent import ViewModeChangeEvent
from event.PlayerEvent import PlayerAttackEvent, PlayerDeathEvent, PlayerHealthEvent, PlayerRespawnEvent
from effect.BlockBulletMark import BlockBulletMark
from effect.BloodBulletMark import BloodBulletMark
from effect.BulletTracer import BulletTracer
from Camera import Camera
from game.Game import Game

from item.ItemId import ItemId
from item.Firearm import Firearm
from item.Builder import Builder

import GameTime
from panda3d.core import CollisionTraverser, CollisionHandlerPusher #@UnresolvedImport
import Settings
import Globals
#from PStats import pstat
from direct.interval.IntervalGlobal import LerpPosInterval
from event.InventoryEvent import SelectedItemChangeEvent

from item.ItemStack import ItemStack
from item.LowMetal import LowMetal

KEY_FWD = 0
KEY_RIGHT = 1
KEY_BACK = 2
KEY_LEFT = 4

myDebug = 0
DEBUG_PREDICTION = 1
START_POS = VBase3(10, 10, 16)

class PlayerController(DirectObject):
    
    #-----------------
    # Initialization
    #-----------------
    
    def __init__(self, engine, environment):
        self.engine = engine
        self.players = {}
        self.environment = environment
        self.inputQueue = deque()
        self.collisionDummy = CollisionDummy()
        self.inputPollWait = 0
        self.playerCollisionHandler = CollisionHandlerPusher()
        self.playerCollisionHandler.addCollider(self.collisionDummy.GetCollisionNode(), self.collisionDummy.GetNode())
        self.playerCollisionTraverser = CollisionTraverser('playerCollisionTraverser')
        self.playerCollisionTraverser.addCollider(self.collisionDummy.GetCollisionNode(), self.playerCollisionHandler)
        #self.playerCollisionTraverser.showCollisions(render)
        
        self.LoadServerPosDebug()
        self.LoadMyself()
        
        self.accept(ViewModeChangeEvent.EventName, self.OnViewModeChange)
        self.accept(SelectedItemChangeEvent.EventName, self.OnSelectedItemChangeEvent)
        self.accept(PlayerAttackEvent.EventName, self.OnPlayerAttackEvent)
        self.accept(PlayerRespawnEvent.EventName, self.OnPlayerRespawnEvent)
        self.accept(PlayerDeathEvent.EventName, self.OnPlayerDeathEvent)
        self.accept(TeamSelectEvent.EventName, self.OnTeamSelectEvent)
        
        if(not Settings.IS_SERVER):
            self.sounds = {}
            self.sounds['blockBreak'] = loader.loadSfx('Assets/Sounds/blockBreak.mp3')
            self.sounds['blockPlace'] = loader.loadSfx('Assets/Sounds/blockPlace.mp3')
        
    #-----------------------
    # Game Updates / Ticks
    #-----------------------
    
    def FixedUpdate(self):
        self.UpdatePlayer(self.GetMyself(), self.GetMyself().GetPlayerState(), self.engine.input, Globals.FIXED_UPDATE_DELTA_TIME)
        
    def Update(self):
        if(Settings.IS_SERVER):
            # Move all of the players that we have input for
            for elem in self.inputQueue:
                self.ProcessInput(elem[0], elem[1])
            self.inputQueue.clear()
            
            # Check to see if anyone fell off the environment
            self.CheckForFallingPlayers()
        else:
            self.GetMyself().UpdateLookingDirection(self.engine.camera.GetDirection())
            
            for player in self.players.values():
                player.GetPlayerOverheadName().Update()
            
            if(Globals.OFFLINE):
                self.CheckForFallingPlayers()
            
    def CheckForFallingPlayers(self):
        for player in self.players.values():
            if(player.GetPlayerState().GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
                if(player.GetPlayerState().GetValue(PlayerState.POSITION).getZ() < -10):
                    PlayerAttackEvent(player, player, 1000, False).Fire()
            
    #--------------------
    # Updating a player
    #--------------------
    
    def UpdatePlayer(self, player, playerState, playerInput, deltaTime):
        if(playerState.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING_DEAD):
            return
        
        playerState = self.MovePlayer(player, playerState, playerInput, deltaTime)
        player.SetPos(playerState.GetValue(PlayerState.POSITION))
        playerState.UpdateValue(PlayerState.KEYS_PRESSED, playerInput.GetKeys())
        self.HandleDeltaStates()
        player.Update(deltaTime)
        player.UpdateLookingRayDirection(playerInput.GetLookingDir())
        playerState.UpdateValue(PlayerState.LOOKING_DIRECTION, playerInput.GetLookingDir())
        if(playerState.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
            self.PlayerInteraction(player, playerInput.click1, playerInput.click3)
        
    def MovePlayer(self, player, playerState, playerInput, deltaTime):
                
        if(playerState.HasValue(PlayerState.TIME_ELAPSED)):
            timeElapsed = playerState.GetValue(PlayerState.TIME_ELAPSED)
        else:
            timeElapsed = 0
            
        if(playerState.HasValue(PlayerState.Z_VELOCITY)):
            zVelocity = playerState.GetValue(PlayerState.Z_VELOCITY)
        else:
            zVelocity = 0
        
        startPos = playerState.GetValue(PlayerState.POSITION)
        if(playerState.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
            newPos = self.ApplyInput(playerState, Vec3(startPos), playerInput, timeElapsed, zVelocity, deltaTime)
        elif(playerState.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_SPECTATE):
            newPos = self.ApplySpectatorInput(playerState, Vec3(startPos), playerInput, timeElapsed, zVelocity, deltaTime)
        
        playerState = self.EnvironmentCollisionCheck(self.environment, player, newPos, startPos, playerState)
        return playerState
    
    def ApplyInput(self, playerState, pos, playerInput, timeElapsed, zVelocity, deltaTime):
        fDir = Vec3(0, 0, 0)
        movementSpeed = 5
        
        facingDirection = Vec3(playerInput.GetLookingDir())
        facingDirection.setZ(0)
        facingDirection.normalize()
        keysPressed = playerInput.GetKeys()
        
        # Apply input commands
        for key in keysPressed:
            if(key == Globals.KEY_FWD):
                fDir += facingDirection
                
            elif(key == Globals.KEY_BACK):
                fDir -= facingDirection
                
            elif(key == Globals.KEY_RIGHT):
                strafePoint = facingDirection.cross(Globals.UP_VECTOR)
                strafePoint.normalize()
                fDir += strafePoint
                
            elif(key == Globals.KEY_LEFT):
                strafePoint = facingDirection.cross(Globals.UP_VECTOR)
                strafePoint.normalize()
                fDir -= strafePoint
                
            elif(key == Globals.KEY_JUMP):
                if(not playerState.HasValue(PlayerState.IS_GROUNDED)):
                    playerState.SetValue(PlayerState.IS_GROUNDED, True)
                if(playerState.GetValue(PlayerState.IS_GROUNDED)):
                    timeElapsed = 0
                    zVelocity = 6.55
                    playerState.UpdateValue(PlayerState.Z_VELOCITY, 5)
                    playerState.UpdateValue(PlayerState.IS_GROUNDED, False)           
                    
        # Calculate new position
        fDir.normalize()
        pos =  pos + (fDir * movementSpeed * deltaTime)
        
        #if(Settings.IS_SERVER or playerState.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
        # Update timeElapsed (for gravity)
        timeElapsed += deltaTime
        playerState.UpdateValue(PlayerState.TIME_ELAPSED, timeElapsed)
        
        # Figure out effect of gravity
        dz = (zVelocity * timeElapsed + 0.5 * Settings.GRAVITY * timeElapsed * timeElapsed) - (zVelocity * (timeElapsed - deltaTime) + 0.5 * Settings.GRAVITY * (timeElapsed - deltaTime) * (timeElapsed - deltaTime))
        pos.setZ(pos.getZ() + dz)
        
        return pos
    
    def ApplySpectatorInput(self, playerState, pos, playerInput, timeElapsed, zVelocity, deltaTime):
        fDir = Vec3(0, 0, 0)
        movementSpeed = 8
        
        facingDirection = Vec3(playerInput.GetLookingDir())
        facingDirection.normalize()
        keysPressed = playerInput.GetKeys()
        
        # Apply input commands
        for key in keysPressed:
            if(key == Globals.KEY_FWD):
                fDir += facingDirection
                
            elif(key == Globals.KEY_BACK):
                fDir -= facingDirection
                
            elif(key == Globals.KEY_RIGHT):
                strafePoint = facingDirection.cross(Globals.UP_VECTOR)
                strafePoint.normalize()
                fDir += strafePoint
                
            elif(key == Globals.KEY_LEFT):
                strafePoint = facingDirection.cross(Globals.UP_VECTOR)
                strafePoint.normalize()
                fDir -= strafePoint         
                    
        # Calculate new position
        fDir.normalize()
        pos =  pos + (fDir * movementSpeed * deltaTime)
        
        return pos
    
    # Draws bullet tracers and bullet impacts with environment
    def ShowShootingEffects(self, player):
        lookingDir = player.GetPlayerState().GetValue(PlayerState.LOOKING_DIRECTION)
        if(player.lookingRayCollisionEntry):
            loc = player.lookingRayCollisionEntry.getSurfacePoint(render)
            norm = player.lookingRayCollisionEntry.getSurfaceNormal(render)
            
            if(player.lookingRayCollisionEntry.getIntoNodePath().getPythonTag(Globals.TAG_COLLISION) == Globals.COLLISION_BLOCK):
                bid = player.lookingRayCollisionEntry.getIntoNodePath().getPythonTag(Globals.TAG_BLOCK).GetId()
                BlockBulletMark(loc, norm, bid)
            else:
                BloodBulletMark(loc, norm, 0)
        else:
            loc = Point3(player.camNode.getPos(render) + lookingDir * 1000)
        start = player.currentItem.GetPos(render) + Vec3(0, 0, -0.1) + lookingDir * 5
        if((loc - start).lengthSquared() > 16):
            BulletTracer(start, loc)  
    
    def OtherPlayerInteraction(self, player, click1, click3):
        if(isinstance(player.currentItem, Firearm)):
            player.currentItem.Use()
            player.PerfromLookingRayCollision(False)
            
            if(not Settings.IS_SERVER):
                self.ShowShootingEffects(player)
    
    def PlayerInteraction(self, player, click1, click3):
        traversed = False
        playerState = player.GetPlayerState()
        playerState.SetValue(PlayerState.USED_ITEM, False)
        
        currentItem = player.currentItem
        if(isinstance(currentItem, Firearm)):
            if(click1):
                if(currentItem.CanUse()):
                    currentItem.Use()
                    currentItem.Used()
                    playerState.UpdateValue(PlayerState.USED_ITEM, True)
                    player.camNode.setP(player.camNode.getP() + currentItem.recoil)
                    player.camNode.setH(player.camNode.getH() + (0.5 - random.random()) * 2 * currentItem.recoil)
                    
                    if(Settings.IS_SERVER):
                        self.MovePlayersToSnapshot(player, playerState.GetValue(PlayerState.CURRENT_SERVER_TIME) - playerState.GetValue(PlayerState.LAST_SERVER_TIME) + 2) # Add 2 to account for 100ms delay caused by lerping
                    player.PerfromLookingRayCollision()
                    if(Settings.IS_SERVER):
                        self.ReturnPlayersToCurrentPosition()
                    traversed = True
                    
                    # Check for collision with player, if so, do damage
                    if(Settings.IS_SERVER):
                        if(player.lookingRayCollisionEntry):
                            np = player.lookingRayCollisionEntry.getIntoNodePath()
                            collisionTag = np.getPythonTag(Globals.TAG_COLLISION)
                            if(collisionTag != Globals.COLLISION_BLOCK):
                                victim = np.getPythonTag(Globals.TAG_PLAYER)
                                damage = currentItem.GetDamage()
                                hs = False
                                if(collisionTag == Globals.COLLISION_HEAD):
                                    damage *= 1.25
                                    hs = True
                                elif(collisionTag == Globals.COLLISION_LEG):
                                    damage *= 0.75
                                    
                                # Either frindly fire is on, or the attacker and victim are on separate teams
                                if(Settings.FRIENDLY_FIRE or player.GetPlayerState().GetValue(PlayerState.TEAM) != victim.GetPlayerState().GetValue(PlayerState.TEAM)):
                                    PlayerAttackEvent(player, victim, damage, hs).Fire()
                    
                    if(not Settings.IS_SERVER):
                        self.ShowShootingEffects(player)
                
                # Auto reload on the client
                elif(not Settings.IS_SERVER and Settings.AUTO_RELOAD and currentItem.GetCurrentClipAmmo() == 0 and currentItem.GetTotalRemainingAmmo() > 0):
                    player.Reload()
                    
            if(click3):
                if(not Settings.IS_SERVER):
                    currentItem.ToggleADS()
                    
        if(not traversed):
            player.PerfromLookingRayCollision()
                    
        if(isinstance(currentItem, Builder)):
            
            if(click1):
                selectedBlock = player.GetSelectedBlock()
                if(selectedBlock and currentItem.CanUse()):
                    playerState.UpdateValue(PlayerState.USED_ITEM, True)
                    self.environment.DestroyBlock(int(selectedBlock.getX()), int(selectedBlock.getY()), int(selectedBlock.getZ()))
                    currentItem.Used()
                    
                    if(not Settings.IS_SERVER):
                        self.sounds['blockBreak'].play()
                
            if(click3):
                adjacentBlockPoint = player.GetAdjacentBlock()
                if(adjacentBlockPoint and currentItem.CanUse()):
                    self.environment.AddBlock(int(adjacentBlockPoint.getX()), int(adjacentBlockPoint.getY()), int(adjacentBlockPoint.getZ()), currentItem.GetBlockId())
                    currentItem.Used()
                    
                    if(not Settings.IS_SERVER):
                        self.sounds['blockPlace'].play()  
                    
    def MovePlayersToSnapshot(self, currentPlayer, numFramesBack):
        for player in self.players.values():
            player.currentPosition = player.pNode.getPos()
            if(player != currentPlayer and player.GetPlayerState().GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
                player.MovePosToPriorSnapshot(numFramesBack)
            
    def ReturnPlayersToCurrentPosition(self):
        for player in self.players.values():
            player.ReturnToCurrentPosition()
            
    def IsColliding(self, player, x, y, z):
        blocks = self.engine.GetEnvironment().GetBlocks()
        blockPoss = [[x, y, z], [x+1, y, z], [x, y+1, z], [x-1, y, z], [x, y-1, z],
                     [x, y, z+1], [x+1, y, z+1], [x, y+1, z+1], [x-1, y, z+1], [x, y-1, z+1],
                     [x, y, z+2], [x+1, y, z+2], [x, y+1, z+2], [x-1, y, z+2], [x, y-1, z+2],
                     [x+1, y+1, z], [x-1, y+1, z], [x+1, y-1, z], [x-1, y-1, z],
                     [x+1, y+1, z+1], [x-1, y+1, z+1], [x+1, y-1, z+1], [x-1, y-1, z+1],
                     [x+1, y+1, z+2], [x-1, y+1, z+2], [x+1, y-1, z+2], [x-1, y-1, z+2]]
        for (x1, y1, z1) in blockPoss:
            if(self.engine.GetEnvironment().AreValidIndices(x1, y1, z1)):
                if(blocks[x1][y1][z1].IsSolid() and player.boundingBox.IsCollidingWithBlock(x1, y1, z1)):
                    return True
        return False
    
    def EnvironmentCollisionCheck(self, environment, player, newPos, lastGoodPos, playerState):                
        
        x = int(lastGoodPos.getX())
        y = int(lastGoodPos.getY())
        z = int(lastGoodPos.getZ())
        
        # Check Z component
        z = int(newPos.getZ())
        player.pNode.setZ(newPos.getZ())
        if(self.IsColliding(player, x, y, z)):
            player.pNode.setZ(player.pNode.getZ() + player.boundingBox.lastAxisCollisions[2])
            z = int(player.pNode.getZ())
            
            playerState.UpdateValue(PlayerState.TIME_ELAPSED, 0)
            playerState.UpdateValue(PlayerState.Z_VELOCITY, 0)
            if(newPos.getZ() < lastGoodPos.getZ()):
                playerState.UpdateValue(PlayerState.IS_GROUNDED, True)
        else:
            playerState.UpdateValue(PlayerState.IS_GROUNDED, False)  
            
        # Check X component
        x = int(newPos.getX())
        player.pNode.setX(newPos.getX())
        if(self.IsColliding(player, x, y, z)):
            player.pNode.setX(player.pNode.getX() + player.boundingBox.lastAxisCollisions[0])
            x = int(player.pNode.getX())
            
        # Check Y component
        y = int(newPos.getY())
        player.pNode.setY(newPos.getY())
        if(self.IsColliding(player, x, y, z)):
            player.pNode.setY(player.pNode.getY() + player.boundingBox.lastAxisCollisions[1])
            y = int(player.pNode.getY())
            
        playerState.UpdateValue(PlayerState.POSITION, player.GetPos())
        return playerState
    
    #------------------------------
    # Player Deaths and Respawning
    #------------------------------
    
    def OnPlayerRespawnEvent(self, event):
        player = event.GetPlayer()
        pos = self.engine.game.FindRespawnPoint(None)
        playerState = player.GetPlayerState()
        if(playerState):
            playerState.UpdateValue(PlayerState.PLAYING_STATE, PlayerState.PS_PLAYING)
            playerState.UpdateValue(PlayerState.POSITION, pos)
            playerState.UpdateValue(PlayerState.HEALTH, 100)
            player.ChangeItem(player.currentItem)
            player.SetPos(pos)
            self.RefillAllAmmo(player)
            player.OnRespawn()
            if(Settings.IS_SERVER):
                self.engine.server.SendPlayerRespawn(playerState)
            print 'player respawned', playerState.GetValue(PlayerState.NAME), playerState.GetValue(PlayerState.CURRENT_ITEM)
            
            if(not Settings.IS_SERVER):
                self.engine.scoreboard.UpdateIsAlive(playerState.GetValue(PlayerState.PID), True)
            
        else:
            del player
            
    def OnPlayerDeathEvent(self, event):
        victim = event.GetVictim()
        attacker = event.GetAttacker()
        wasHS = event.WasHeadshot()
        
        playerState = victim.GetPlayerState()
        playerState.UpdateValue(PlayerState.PLAYING_STATE, PlayerState.PS_PLAYING_DEAD)
        print 'player Died', playerState.GetValue(PlayerState.NAME)
        victim.OnDeath()
        
        if(Settings.IS_SERVER or Globals.OFFLINE):
            taskMgr.doMethodLater(Game.RESPAWN_TIME, PlayerRespawnEvent(victim, None).Fire, 'RespawnPlayer_%s' % (playerState.GetValue(PlayerState.PID))) 
            
        if(not Settings.IS_SERVER and victim == self.GetMyself()):
            self.engine.respawnCountdown.Start()
            
        if(not Settings.IS_SERVER):
            self.engine.scoreboard.UpdateIsAlive(playerState.GetValue(PlayerState.PID), False)
    
    #------------------------
    # Client only functions
    #------------------------
    
    # This event only gets fired when our player selects a team
    def OnTeamSelectEvent(self, event):
        teamId = event.GetTeam()
        self.GetMyself().OnTeamChange(teamId)
        self.engine.scoreboard.UpdateTeam(Globals.MY_PID, Globals.MY_TEAM)
    
    def VerifyPrediction(self, serverState, snapshots):
        if(not serverState.HasValue(PlayerState.POSITION)):
            return
        
        if(Globals.DEBUG_CSP):
            print 'SERVER', serverState.GetValue(PlayerState.TIMESTAMP), serverState.GetValue(PlayerState.POSITION)
            print 'ME', snapshots[0].GetTimestamp(), snapshots[0].GetPosition()
            for x in snapshots:
                print 'SS', x.GetTimestamp(), x.GetPosition()
        
        diff = (serverState.GetValue(PlayerState.POSITION) - snapshots[0].GetPosition())
        
        if(diff.length() > 0.001):
            print 'DIFF', diff
            myself = self.GetMyself()
            myState = myself.GetPlayerState()
            for snapshot in snapshots:
                serverState.SetValue(PlayerState.PLAYING_STATE, PlayerState.PS_PLAYING)
                serverState = self.MovePlayer(myself, serverState, snapshot.GetInput(), Globals.FIXED_UPDATE_DELTA_TIME)
                snapshot.pos = serverState.GetValue(PlayerState.POSITION)
                myState.UpdateValue(PlayerState.POSITION, serverState.GetValue(PlayerState.POSITION))
                myself.SetPos(serverState.GetValue(PlayerState.POSITION))
                
        return snapshots
    
    def HandleDeltaStates(self):
        
        if(not Settings.IS_SERVER):
        
            for player in self.players.values():
                state = player.GetPlayerState()
                deltaState = state.GetDeltaVars()
                
                if(not Settings.IS_SERVER):
                    state.ClearDeltaVars()
                
                for dVar in deltaState:
                    # If isWalking changed
                    if(dVar == PlayerState.IS_WALKING):
                        if(state.GetValue(dVar)):           # If the player is now walking
                            player.RequestFSMTransition('IdleToWalk')
                        else:                               # If the player stopped moving
                            player.RequestFSMTransition('WalkToIdle')
                                                    
    # Given a dictionary of playerstate updates from the server,
    # apply them to the players in the game
    def HandleServerPlayerStates(self, playerStates):
        for pid, playerState in playerStates.iteritems():
            if(pid != self.GetMyId()):
                if(not pid in self.players.keys()):
                    continue
                    
                player = self.GetPlayer(pid)
                for pVar, value in playerState.vars.iteritems():
                    
                    if(pVar == PlayerState.POSITION):
                        self.GetPlayerPlayerState(player).UpdateValue(PlayerState.POSITION, value)
                        player.LerpTo(value)
                        
                    elif(pVar == PlayerState.LOOKING_DIRECTION):
                        self.GetPlayerPlayerState(player).UpdateValue(PlayerState.LOOKING_DIRECTION, value)
                        player.UpdateLookingDirection(value)
                        player.UpdateLookingRayDirection(value)
                            
                                
    def OtherPlayerWalkingChange(self, player, isWalking):
        if(isWalking):
            player.RequestFSMTransition('IdleToWalk')
        else:
            player.RequestFSMTransition('WalkToIdle')
            
    def HealthChange(self, player, health):
        player.GetPlayerState().UpdateValue(PlayerState.HEALTH, health)
        if(player == self.GetMyself()):
            PlayerHealthEvent(player, health).Fire()
    
    #------------------------
    # Server only functions
    #------------------------
    
    def IsFull(self):
        return len(self.players) > Globals.MAX_PLAYERS
    
    def QueueClientInput(self, player, keys, lookingDir, clicks, timestamp):
        
        newInput = Input(keys, lookingDir, clicks, timestamp)
        self.inputQueue.append([player, newInput])
        
        playerState = player.GetPlayerState()
        playerState.timestamp = timestamp
        
        return newInput
    
    def ProcessInput(self, player, newInput):
        if(player in self.players.values()):
            playerInputBuffer = player.GetInputBuffer()
            playerInputBuffer.UpdateInput(newInput)
            
            if(playerInputBuffer.GoodToGo()):
                newestInput = playerInputBuffer.GetNewestInput()
                bufferedInput = playerInputBuffer.GetBufferedInput()
                playerState = player.GetPlayerState()
                playerState.UpdateValue(PlayerState.KEYS_PRESSED, bufferedInput.GetKeys())
                
                if(playerState.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
                    
                    # Run a Fixed MovementUpdate as many times as necessary
                    while(newestInput.GetTimestamp() - playerState.GetValue(PlayerState.TIMESTAMP) > Globals.FIXED_UPDATE_DELTA_TIME):
                        self.UpdatePlayer(player, playerState, bufferedInput, Globals.FIXED_UPDATE_DELTA_TIME)
                        playerState.SetValue(PlayerState.TIMESTAMP, playerState.GetValue(PlayerState.TIMESTAMP) + Globals.FIXED_UPDATE_DELTA_TIME)
                        #print 'processing input for player ', playerState.GetValue(PlayerState.PID)
                else:
                    print 'spectator', playerState.GetValue(PlayerState.PID)
            else:
                player.GetPlayerState().SetValue(PlayerState.TIMESTAMP, newInput.GetTimestamp())
    
    #---------------------------------------
    # Adding and Removing Players from Game
    #---------------------------------------
        
    def AddNewPlayer(self, pid, name, teamId, playingState = PlayerState.PS_SPECTATE):
        print 'adding new player', pid
        if(pid not in self.players.keys()):
            player = Player()
            
            self.players[pid] = player
            playerState = player.GetPlayerState()
            playerState.SetValue(PlayerState.PID, pid)
            playerState.SetValue(PlayerState.NAME, name)
            playerState.SetValue(PlayerState.TEAM, teamId)
            playerState.SetValue(PlayerState.PLAYING_STATE, playingState)
            print 'added player', pid, name
            
            player.CreateNameTextNode(name)
            player.OnTeamChange(teamId)
            player.ShowPlayerModel()
            
            
            if(pid != Globals.MY_PID):
                player.RemoveSelectionGeom()
                
                if(teamId == Globals.MY_TEAM):
                    player.ShowNameAboveHead()
            else:
                player.HidePlayerModel()
                
            
                
        
    def RemovePlayer(self, pid):
        player = self.players[pid]
        player.Destroy()
        del self.players[pid]
        taskMgr.remove('RespawnPlayer_%s' %(pid))
        
    def HidePlayerModel(self, playerObject):
        playerObject.HidePlayerModel()
        
    def ShowPlayerModel(self, playerObject):
        playerObject.ShowPlayerModel()
        
    # THIS IS TEMPORARY
    def RefillAllAmmo(self, player):
        for item in player.itemModels.values():
            if(isinstance(item, Firearm)):
                item.RefillAmmo()
                
        if(not Settings.IS_SERVER and player.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            inv = player.GetPlayerState().GetValue(PlayerState.MAIN_INVENTORY)
            for itemStack in inv.GetItemStacks():
                if(isinstance(itemStack.GetItem(), Firearm)):
                    itemStack.GetItem().RefillAmmo()
        
    #--------------------
    # Event Handling
    #-----------------
    
    def OnSelectedItemChangeEvent(self, event):
        self.GetMyself().OnSelectedItemChangeEvent(event)
        
    # Figure out what item the player now has. If they've had
    # it before, use the already loaded model. Otherwise,
    # load the model
    def OtherPlayerItemChange(self, player, itemId, extraData = None):
        itemClass = ItemId.ToItem(itemId)
        #player.GetPlayerState().UpdateValue(PlayerState.CURRENT_ITEM, ItemId.NoItem)
        #player.GetPlayerState().UpdateValue(PlayerState.CURRENT_ITEM, itemId)
        if(itemId not in player.itemModels.keys()):            
            if(itemClass):
                item = itemClass()
                item.playerId = player.GetPlayerState().GetValue(PlayerState.PID)
            else:
                item = None
            player.itemModels[itemId] = item
            
        if(extraData):
            print 'changing with extra data'
            player.GetPlayerState().SetValue(PlayerState.CURRENT_ITEM, ItemId.Unknown)
            player.GetPlayerState().UpdateValue(PlayerState.CURRENT_ITEM, itemId)
            if(itemId == ItemId.Builder):
                player.itemModels[itemId].SetBlockId(extraData[0])
                if(not Settings.IS_SERVER):
                    player.itemModels[itemId].UpdateTexture()
                    
                    
        #player.GetPlayerState().UpdateValue(PlayerState.CURRENT_ITEM, itemId)
        
        player.ThirdPersonChangeItem(player.itemModels[itemId])
    
    def OnViewModeChange(self, event):        
        if(event.GetViewMode() == Camera.FirstPersonMode):
            self.GetMyself().HidePlayerModel() 
        else:
            self.GetMyself().ShowPlayerModel()
            
    def OnPlayerAttackEvent(self, event):
        victim = event.GetVictim()
        
        # Update the victim's health
        health = victim.GetPlayerState().GetValue(PlayerState.HEALTH)
        health = max(0, health - event.GetDamage())
        victim.GetPlayerState().UpdateValue(PlayerState.HEALTH, health)
        
        player = event.GetPlayer()
        player.GetPlayerState().UpdateValue(PlayerState.VICTIM, victim)
        
        if(event.WasHeadshot() and health == 0):
            player.GetPlayerState().UpdateValue(PlayerState.VICTIM_ATTACK_TYPE, PlayerState.VAT_BOTH)
        elif(event.WasHeadshot()):
            player.GetPlayerState().UpdateValue(PlayerState.VICTIM_ATTACK_TYPE, PlayerState.VAT_HEADSHOT)
        elif(health == 0):
            player.GetPlayerState().UpdateValue(PlayerState.VICTIM_ATTACK_TYPE, PlayerState.VAT_KILLSHOT)
        else:
            player.GetPlayerState().UpdateValue(PlayerState.VICTIM_ATTACK_TYPE, PlayerState.VAT_NONE)
            
        if(health == 0):
            PlayerDeathEvent(victim, player, event.WasHeadshot()).Fire()
            print 'PLAYER DIEEED'
            
    def ResetPlayerNames(self):
        for player in self.players.values():
            if(player != self.GetMyself()):
                if(player.GetPlayerState().GetValue(PlayerState.TEAM) != Globals.MY_TEAM):
                    # THIS IS REALLY BAD
                    player.nameText.reshowOnInView = False
                    player.nameText.Hide()
                else:
                    player.nameText.reshowOnInView = True
                    player.ShowNameAboveHead()
    
    #------------------------------------------------
    # Getting Information for All Players
    #------------------------------------------------
    
    def GetAllPlayers(self):
        return self.players.values()  
    
    def GetAllPlayerStates(self):
        ps = []
        for player in self.players.values():
            ps.append(player.GetPlayerState())
        return ps
    
    def GetAllPlayingPlayerStates(self):
        ps = []
        for player in self.players.values():
            ps1 = player.GetPlayerState()
            if(ps1.GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
                ps.append(ps1)
        return ps
    
    def GetAllPlayerNodes(self):
        nodes = []
        for p in self.GetPlayers():
            nodes.append(p.pNode)
        return nodes  
    
    #------------------------------------------------
    # Getting information for One Player
    #------------------------------------------------
    
    def GetPlayer(self, pid):
        if(pid in self.players.keys()):
            return self.players[pid]
        else:
            return None
    
    def GetPlayerPlayerState(self, player, pid = None):
        if(player is None):
            return self.GetPlayerPlayerState(self.GetPlayer(pid))
        else:
            return player.GetPlayerState()

    def GetPlayerPickerRay(self, player):
        return player.lookingRay
    
    def GetPlayerCollision(self, player):
        return player.collisionGeom 
    
    def GetPlayerEyePosition(self, player):
        return player.camNode.getPos(render)
    
    def GetPlayerLookingDirection(self, player):
        return player.lookingDirection
    
    #------------------------------------------------
    # Getting information for Myself
    #------------------------------------------------
    
    def GetMyself(self):
        return self.players[Globals.MY_PID]
    
    def GetMyId(self):
        return Globals.MY_PID
    
    def GetMyCamNode(self):
        return self.GetMyself().camNode
    
    def GetMyPlayerState(self):
        return self.GetPlayerPlayerState(self.GetMyself())
            
    def GetMyDeltaState(self):
        return self.GetMyself().GetPlayerState().GetDeltaVars()
    
    #--------------------------------------------------------
    # Helper Functions for Setup of PlayerController Object 
    #--------------------------------------------------------
        
    def LoadServerPosDebug(self):
        self.serverPlayer = loader.loadModel('Assets/Models/Players/ralph')
        self.serverPlayer.setScale(0.36)
        self.serverPlayer.reparentTo(render)
        if(not Globals.DEBUG_CSP):
            self.serverPlayer.hide()
        
    def LoadMyself(self):
        print 'loading self'
        if(not Settings.IS_SERVER):
            self.AddNewPlayer(pid = Globals.MY_PID, name = Settings.NAME, teamId = Game.SPECTATE, playingState = PlayerState.PS_SPECTATE)
            
    #-------------------------------------------------------------
    # Helper Functions for Destruction of PlayerController Object 
    #-------------------------------------------------------------
        
    def Destroy(self):
        self.ignoreAll()
        for player in self.players.values():
            player.Destroy()
        del self.players
        del self.environment
        del self.inputQueue
        del self.collisionDummy
        del self.inputPollWait
        del self.playerCollisionHandler
        del self.playerCollisionTraverser
        
    