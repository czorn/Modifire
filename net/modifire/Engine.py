import sys
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import WindowProperties, Vec4

from player.PlayerController import PlayerController
from environment.Environment import Environment
from environment.EnvironmentLoader import EnvironmentLoader
from hud.HUD import HUD
from hud.FPSCounter import FPSCounter

from gui.menus.MenuController import MenuController
from Camera import Camera
from player.PlayerState import PlayerState
from player.Input import Input
from gui.menus.InventoryGUI import InventoryGUI
from gui.chat.ChatBox import ChatBox
from gui.Scoreboard import Scoreboard
from hud.DeathNotifications import DeathNotifications
from hud.RespawnCountdown import RespawnCountdown
from event.ChatEvent import ChatOpenEvent, ChatCloseEvent, ChatReceivedEvent, ChatEnteredEvent
from event.MenuEvent import MenuOpenEvent, MenuCloseEvent
from event.ClientEvent import EngineLoadedEvent
from event.EnvironmentEvent import EnvironmentChangeEvent
from event.PlayerEvent import PlayerJoinEvent, PlayerDisconnectEvent, PlayerDeathEvent, PlayerRespawnEvent
from event.WindowEvent import WindowFocusEvent
from InputFSM import InputFSM
from game.Game import Game
import Settings
import Globals
import GameTime
import InputKeys
#from PStats import pstat

KEY_FWD = 0
KEY_RIGHT = 1
KEY_BACK = 2
KEY_LEFT = 4



class Engine(DirectObject):
    
    #-----------------
    # Initialization
    #-----------------
     
    def __init__(self, pid, mapname, server = False):
        Globals.WORLD_SEED = mapname
        Settings.IS_SERVER = server
        self.addrToPlayer = {}
        self.input = Input()
        self.lastInputPollTime = 0
        self.lastFixedUpdateTimestamp = 0
        self.client = None
        self.server = None
        
        self.fpsCounter = FPSCounter()
        self.envLoader = EnvironmentLoader()
        
        if(Globals.BLOCKS):
            self.environment = self.envLoader.LoadEnvironmentFromServer(Globals.BLOCKS, Globals.MAP_INFO)
        else:
            self.environment = self.envLoader.LoadEnvironment(Settings.LAST_WORLD)
            
        self.playerController = PlayerController(self, self.environment)
        self.game = Game(self, self.playerController)   
        
        self.SetupKeyBinds()
        self.SetupEventHandlers() 
        
        self.hud = None
        self.menuController = None
        self.camera = None
        self.selectionGeom = None
        self.scoreboard = None
            
        if(Settings.IS_SERVER):
            render.hide()
            
        else:
            self.menuController = MenuController(self, InventoryGUI(self.playerController.GetMyPlayerState().GetValue(PlayerState.MAIN_INVENTORY)))
            print 'loaded menuController'
            self.camera = Camera(self.playerController.GetMyCamNode())
            self.hud = HUD(self)
            print 'loaded hud'
            self.chat = ChatBox()
            self.deathNotifications = DeathNotifications()
            self.inputFSM = InputFSM(self, self.chat, self.menuController)
            self.scoreboard = Scoreboard()
            self.scoreboard.NewRow(Globals.MY_PID, Settings.NAME)
            self.menuController.OpenTeamSelectMenu()
            self.respawnCountdown = RespawnCountdown()
            
            from item.SMGAuto import SMGAuto
            from item.Builder import Builder
            from item.RifleAuto import RifleAuto
            from item.SniperBolt import SniperBolt
            self.playerController.GetMyPlayerState().GetValue(PlayerState.MAIN_INVENTORY).AddCustomItem(SMGAuto())
            self.playerController.GetMyPlayerState().GetValue(PlayerState.MAIN_INVENTORY).AddCustomItem(Builder())
            self.playerController.GetMyPlayerState().GetValue(PlayerState.MAIN_INVENTORY).AddCustomItem(RifleAuto())
            self.playerController.GetMyPlayerState().GetValue(PlayerState.MAIN_INVENTORY).AddCustomItem(SniperBolt())
        
        
        # Register Update task to occur every frame
        taskMgr.add(self.Tick,"GameEngineTick")
        print 'added tick'
        
        GameTime.fixedTime = GameTime.GetTime()
        
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def SetupKeyBinds(self):
        self.keyMap = {"KEY_FWD":0, "KEY_BACK":0, "KEY_LEFT":0, "KEY_RIGHT":0,
                       "KEY_JUMP":0, "LEFT_MOUSE":0, "RIGHT_MOUSE":0, "WHEEL_UP":0,
                       "WHEEL_DOWN":0, "INVENTORY":0, "TOSS_ITEM":0, "RELOAD":0}
        
        self.accept("mouse1", self.setKey, ['LEFT_MOUSE', 1])
        self.accept("mouse1-up", self.setKey, ['LEFT_MOUSE', 0])
        self.accept("mouse3", self.setKey, ['RIGHT_MOUSE', 1])
        self.accept("mouse3-up", self.setKey, ['RIGHT_MOUSE', 0])
        
        self.accept("shift-mouse1", self.setKey, ['LEFT_MOUSE', 1])
        self.accept("shift-mouse1-up", self.setKey, ['LEFT_MOUSE', 0])
        self.accept("shift-mouse3", self.setKey, ['RIGHT_MOUSE', 1])
        self.accept("shift-mouse3-up", self.setKey, ['RIGHT_MOUSE', 0])
        
        self.accept("control-mouse1", self.setKey, ['LEFT_MOUSE', 1])
        self.accept("control-mouse1-up", self.setKey, ['LEFT_MOUSE', 0])
        self.accept("control-mouse3", self.setKey, ['RIGHT_MOUSE', 1])
        self.accept("control-mouse3-up", self.setKey, ['RIGHT_MOUSE', 0])
        
        self.accept('f11', self.ToggleFullScreen)
        
    def SetupEventHandlers(self):
        self.accept(ChatOpenEvent.EventName, self.OnChatOpenEvent)
        self.accept(ChatCloseEvent.EventName, self.OnChatCloseEvent)
        self.accept(ChatReceivedEvent.EventName, self.OnChatReceivedEvent)
        self.accept(EngineLoadedEvent.EventName, self.OnEngineLoadedEvent)
        self.accept(MenuOpenEvent.EventName, self.OnMenuOpenEvent)
        self.accept(MenuCloseEvent.EventName, self.OnMenuCloseEvent)
        self.accept(EnvironmentChangeEvent.EventName, self.OnEnvironmentChangeEvent)
        self.accept(PlayerJoinEvent.EventName, self.OnPlayerJoinEvent)
        self.accept(PlayerDisconnectEvent.EventName, self.OnPlayerDisconnectEvent)
        self.accept(PlayerDeathEvent.EventName, self.OnPlayerDeathEvent)
        self.accept(PlayerRespawnEvent.EventName, self.OnPlayerRespawnEvent)
        #self.accept('itemPickUp', self.OnItemPickup)
        self.accept('window-event', self.OnPandaWindowEvent)
        #self.accept('loadMapFail', self.OnLoadMapFail)
        
        if(Globals.OFFLINE):
            self.accept(ChatEnteredEvent.EventName, self.OnChatEnteredEvent)
        
    #-----------------------
    # Game Ticks / Updates
    #-----------------------
    
    def Tick(self, task):
        currentTime = GameTime.GetTime()
        GameTime.UpdateTime(currentTime)
        if(GameTime.deltaTime > 0.1):
            print 'GAME HANG', GameTime.deltaTime
        
        self.Update()
         
        while(GameTime.time - GameTime.fixedTime > Globals.FIXED_UPDATE_DELTA_TIME):
            GameTime.UpdateFixedTime(GameTime.fixedTime + Globals.FIXED_UPDATE_DELTA_TIME)
            self.FixedUpdate()           
            
        return task.cont
        
    #@pstat
    def FixedUpdate(self):
        
        if(Settings.IS_SERVER):
            pass
        else:
            if(GameTime.fixedTime - self.lastInputPollTime >= Globals.CLIENT_SEND_DELAY):
                self.lastInputPollTime = GameTime.fixedTime
                self.input = self.PollInput()
                self.input.SetTimestamp(GameTime.fixedTime)

                if(self.client is not None and self.client.fsm.state == 'PlayingGame'):
                    if(self.playerController.GetMyPlayerState().GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
                        self.client.SendInput(GameTime.fixedTime, self.input, self.playerController.GetMyPlayerState())
                        self.client.StoreSnapshot(GameTime.fixedTime, self.input, self.playerController.GetMyPlayerState())
#                    else:
#                        print 'not playing'
                
            self.playerController.FixedUpdate()
        
    #@pstat
    def Update(self):
        if(Settings.IS_SERVER):
            self.game.Update()
        else:
            self.UpdateCamera()
            self.menuController.Update()
            self.hud.Update()
        
        self.playerController.Update()   
        self.environment.Update()
        self.fpsCounter.Update()
                      
    #-----------------
    # Updating Input
    #----------------- 
    
    def PollInput(self):
        clicks = self.UpdateMyMouseClicks()
        keys = self.UpdateMyKeysPressed()
        return Input(keys, self.camera.GetDirection(), clicks)         
  
    def UpdateMyKeysPressed(self):
        keys = []
        
        if (self.keyMap['KEY_FWD']):
            keys.append(Globals.KEY_FWD)
            
        elif (self.keyMap['KEY_BACK']):
            keys.append(Globals.KEY_BACK)
            
        if (self.keyMap['KEY_RIGHT']):
            keys.append(Globals.KEY_RIGHT)
            
        elif (self.keyMap['KEY_LEFT']):
            keys.append(Globals.KEY_LEFT)
            
        if (self.keyMap['KEY_JUMP']):
            keys.append(Globals.KEY_JUMP)
            
        return keys   
    
    def UpdateMyMouseClicks(self):
        clicks = []
            
        if(not Settings.IS_SERVER and not self.menuController.IsMenuOpen()):
            if(self.keyMap['LEFT_MOUSE']):
                clicks.append(PlayerState.CLICK_1)
            if(self.keyMap['RIGHT_MOUSE']):
                clicks.append(PlayerState.CLICK_3)
                    
        return clicks
  
    def UpdateCamera(self):
        if(not self.menuController.IsMenuOpen()):
            self.camera.Update()
    
    #--------------------------------------------
    # Client - Handling information from server
    #--------------------------------------------
    
      
            
#    def HandleServerPlayerStates(self, playerStates):
#        self.playerController.HandleServerPlayerStates(playerStates)
        
#    def OnServerChatMessage(self, messageType, pid, message):
#        player = self.playerController.GetPlayer(pid)
#        playerState = self.playerController.GetPlayerPlayerState(player)
#        self.chat.AddMessage('%s:' % (playerState.GetValue(PlayerState.NAME)), Vec4(1, 0, 1, 1), message)
        
#    def VerifyPrediction(self, s1, s2):
#        return self.playerController.VerifyPrediction(s1, s2)
            
#    def SetMyId(self, pid):
#        self.playerController.SetMyId(pid)
#        
#    def GetMyId(self):
#        return self.playerController.GetMyId()
      
    #---------------------------------------------
    # Server - Handling information from clients
    #---------------------------------------------
    
#    def QueueClientInput(self, pid, keys, lookingDir, clicks, timestamp):
#        player = self.playerController.GetPlayer(pid)
#        if(player):
#            self.playerController.QueueClientInput(player, keys, lookingDir, clicks, timestamp)
            
    #---------------
    # Out of place
    #---------------
        
    
#    def SaveEnvironment(self):
#        self.environment.Save()
            
    
        
#    def AddNewPlayer(self, pid, name):
#        self.playerController.AddNewPlayer(pid, name)
#        if(not Settings.IS_SERVER):
#            self.chat.AddMessage('', Vec4(0, 0, 0, 0), '%s joined.' % (name))
#        
#    def RemovePlayer(self, pid):
#        playerState = self.playerController.GetPlayerPlayerState(None, pid)
#        name = playerState.GetValue(PlayerState.NAME)
#        self.playerController.RemovePlayer(pid)
#        if(not Settings.IS_SERVER):
#            self.chat.AddMessage('', Vec4(0, 0, 0, 0), '%s disconnected.' % (name))
#            
#    def CreateInitialPlayers(self, playerStates):
#        for ps in playerStates:
#            myid = ps['id']
#            self.playerController.AddNewPlayer(myid)
     
          
#    def UpdatePlayerState(self, playerId, key, value):
#        self.playerController.UpdatePlayerState(playerId, key, value)
#            
#    def GetAllPlayerStates(self):
#        return self.playerController.GetAllPlayerStates()
#    
#    def GetAllPlayingPlayerStates(self):
#        return self.playerController.GetAllPlayingPlayerStates()
#            
#    def GetMyPlayerState(self):
#        return self.playerController.GetMyPlayerState()
#    
#    def GetMyDeltaState(self):
#        return self.playerController.GetMyDeltaState()
#    
#    def ClearMyDeltaState(self):
#        self.playerController.ClearMyDeltaState()
#        
#    def ClearMyClicking(self):
#        self.playerController.ClearMyClicking()
#        
#    def ClearAllDeltaStates(self):
#        self.playerController.ClearAllDeltaStates()
            
    
            
        
    
        
    def EnableKeyboardListening(self):
        self.accept(Settings.KEY_BINDINGS[InputKeys.MOVE_FORWARD], self.setKey, ['KEY_FWD', 1])
        self.accept(Settings.KEY_BINDINGS[InputKeys.MOVE_BACKWARD], self.setKey, ['KEY_BACK', 1])
        self.accept(Settings.KEY_BINDINGS[InputKeys.STRAFE_LEFT], self.setKey, ['KEY_LEFT', 1])
        self.accept(Settings.KEY_BINDINGS[InputKeys.STRAFE_RIGHT], self.setKey, ['KEY_RIGHT', 1])
        
        self.accept('%s-up' % Settings.KEY_BINDINGS[InputKeys.MOVE_FORWARD], self.setKey, ['KEY_FWD', 0])
        self.accept('%s-up' % Settings.KEY_BINDINGS[InputKeys.MOVE_BACKWARD], self.setKey, ['KEY_BACK', 0])
        self.accept('%s-up' % Settings.KEY_BINDINGS[InputKeys.STRAFE_LEFT], self.setKey, ['KEY_LEFT', 0])
        self.accept('%s-up' % Settings.KEY_BINDINGS[InputKeys.STRAFE_RIGHT], self.setKey, ['KEY_RIGHT', 0])
        
        self.accept('%s' % Settings.KEY_BINDINGS[InputKeys.JUMP], self.setKey, ['KEY_JUMP', 1])
        self.accept('%s-up' % Settings.KEY_BINDINGS[InputKeys.JUMP], self.setKey, ['KEY_JUMP', 0])
        
        self.accept('arrow_left', self.playerController.GetMyself().ChangeBlockToPlace, [-1])
        self.accept('arrow_right', self.playerController.GetMyself().ChangeBlockToPlace, [1])
        
        self.accept(Settings.KEY_BINDINGS[InputKeys.RELOAD], self.playerController.GetMyself().Reload)
        
        self.accept('tab', self.scoreboard.Show)
        self.accept('tab-up', self.scoreboard.Hide)
        
        self.acceptOnce('t', self.chat.Show, [ChatBox.TYPE_GLOBAL])
        self.acceptOnce('y', self.chat.Show, [ChatBox.TYPE_TEAM])
        
        self.acceptOnce('escape', self.menuController.OpenInGameMenu)
        self.acceptOnce(Settings.KEY_BINDINGS[InputKeys.INVENTORY], self.menuController.OpenInventory)
        self.acceptOnce(',', self.menuController.OpenTeamSelectMenu)
        self.accept('f5', self.ToggleViewMode)     
        
        # The HUD Hotbar listens for keys 1-5 for swapping items
        self.hud.EnableKeyboardListening()   
        
    def DisableKeyboardListening(self):
        self.ignore('w')
        self.ignore('s')
        self.ignore('a')
        self.ignore('d')
        self.ignore('w-up')
        self.ignore('s-up')
        self.ignore('a-up')
        self.ignore('d-up')
        
        self.ignore('space')
        self.ignore('space-up')
        self.ignore('q')
        
        self.ignore('arrow_left')
        self.ignore('arrow_right')
        
        self.ignore('t')
        self.ignore('y')
        
        self.ignore('tab')
        #self.ignore('tab-up')
        self.ignore('r')
        
        self.ignore('escape')
        self.ignore('e')
        self.ignore(',')
        self.ignore('f5')
        
        self.hud.DisableKeyboardListening()
        
#    def ToggleViewMode(self):
#        self.camera.ToggleViewMode()
        
    #----------------------
    # Game Event Handling
    #----------------------
    
    def OnMenuOpenEvent(self, event):
        self.inputFSM.request('Menu')
        
    def OnMenuCloseEvent(self, event):
        self.inputFSM.request('Game')
        
    def OnChatOpenEvent(self, event):
        self.inputFSM.request('Chat')
        
    def OnChatCloseEvent(self, event):
        self.inputFSM.request('Game')
        
    def OnChatReceivedEvent(self, event):
        player = event.GetPlayer()
        message = event.GetMessage()
        messageType = event.GetMessageType()
        if(messageType == ChatBox.TYPE_CONSOLE):
            self.chat.AddMessage('[Console]:', Globals.COLOR_BLACK, message)
        else:
            if(player):
                self.chat.AddMessage('%s: ' % (player.GetPlayerState().GetValue(PlayerState.NAME)), Globals.TEAM_COLORS[player.GetPlayerState().GetValue(PlayerState.TEAM)], message)
            else:
                self.chat.AddMessage('[Unknown Player]:', Globals.COLOR_GREY, message)
        
    def OnChatEnteredEvent(self, event):
        msg = event.GetMessage()
        print msg[1:], 'saving'
        if(msg[0] != '/'):
            return
        
        if(msg[1:] == 'save'):
            self.SaveEnvironment()
            
        elif(msg[1:] == 'whereami'):
            self.chat.AddMessage('[INFO]: ', Globals.COLOR_BLACK, str(self.playerController.GetMyself().GetPos()))
            
    def SaveEnvironment(self):
        self.envLoader.SaveEnvironment(self.environment)
        
    # Called by Client when another player joins the game
    def OnPlayerJoinEvent(self, event):
        pid = event.GetPid()
        name = event.GetName()
        pState = event.GetPlayingState()
        teamId = event.GetTeamId()
        self.playerController.AddNewPlayer(pid = pid, name = name, teamId = teamId, playingState = pState)
        self.playerController.OtherPlayerItemChange(self.playerController.GetPlayer(pid), event.GetItemId(), event.GetItemData())
        self.chat.AddMessage('', Vec4(0, 0, 0, 0), '%s joined.' % (name))
        self.scoreboard.NewRow(pid, name)
        
    def OnPlayerDisconnectEvent(self, event):
        player = event.GetPlayer()
        playerState = self.playerController.GetPlayerPlayerState(player)
        name = playerState.GetValue(PlayerState.NAME)
        pid = playerState.GetValue(PlayerState.PID)
        self.playerController.RemovePlayer(pid)
        self.chat.AddMessage('', Vec4(0, 0, 0, 0), '%s disconnected.' % (name))
        self.scoreboard.RemoveRow(pid)
        
    def OnPlayerDeathEvent(self, event):
        victim = event.GetPlayer()
        if(not Settings.IS_SERVER):
            if(victim.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
                self.camera.SetViewMode(Camera.ThirdPersonMode)
                
    def OnPlayerRespawnEvent(self, event):
        player = event.GetPlayer()
        if(not Settings.IS_SERVER):
            if(player.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
                self.camera.SetViewMode(Camera.FirstPersonMode)
    
#    def OnViewModeChange(self, viewMode):
#        if(Settings.DEBUG_EVENT): 
#            print '[Event] ViewModeToggled'
#        
#        if(viewMode == Camera.FirstPersonMode):
#            self.playerController.GetMyself().HidePlayerModel() 
#        else:
#            self.playerController.GetMyself().ShowPlayerModel() 
        
#    def OnItemPickup(self, item):
#        if(Settings.DEBUG_EVENT):  
#            print '[Event] ItemPickup'
#        if(self.menuController.OnItemPickup(item)):
#            self.hud.UpdateHotbar()
        
    def OnEngineLoadedEvent(self, event):
        currentTime = GameTime.GetTime()
        GameTime.UpdateTime(currentTime)
        GameTime.UpdateFixedTime(currentTime)
        self.lastFixedUpdateTimestamp = currentTime
        print 'OnEngineLoaded'
        
    def OnEnvironmentChangeEvent(self, event):
        destroyed = event.GetDestroyedBlocks()
        added = event.GetAddedBlocks()
        for myTuple in destroyed:
            self.environment.DestroyBlock(myTuple[0], myTuple[1], myTuple[2], False)
            self.environment.Verified(myTuple)
            
        for myTuple in added:
            self.environment.AddBlock(myTuple[0], myTuple[1], myTuple[2],  myTuple[3], False)
            self.environment.Verified(myTuple) 
        
#    def OnTeamSelected(self, team):
#        self.client.SendSelectedTeam(team)
#        
#    def OnPlayerDeath(self, pid):
#        player = self.playerController.GetPlayer(pid)
#        playerState = self.playerController.GetPlayerPlayerState(player)
#        playerState.UpdateValue(PlayerState.PLAYING_STATE, PlayerState.PS_SPECTATE)
#        self.chat.AddMessage('Console:', Vec4(1, 1, 1, 1), '%s died.' % (playerState.GetValue(PlayerState.NAME)))
#        
#    def OnPlayerRespawn(self, pid, pos):
#        player = self.playerController.GetPlayer(pid)
#        playerState = self.playerController.GetPlayerPlayerState(player)
#        playerState.UpdateValue(PlayerState.POSITION, pos)
#        playerState.UpdateValue(PlayerState.PLAYING_STATE, PlayerState.PS_PLAYING)
     
#    def SaveSnapshot(self, playerState):
#        self.playerController.SaveSnapshot(playerState)
        
    
    
    #-------------------------
    # Screen / Window Sizing
    #-------------------------
    
    def OnPandaWindowEvent(self, event):
        Settings.WIDTH = base.win.getProperties().getXSize()
        Settings.HEIGHT = base.win.getProperties().getYSize()
        print 'window', Settings.WIDTH, Settings.HEIGHT
        windowFocused = base.win.getProperties().getForeground()
        WindowFocusEvent(windowFocused).Fire()
        if(not Settings.IS_SERVER):
            self.camera.OnWindowResized()
            
    def ToggleViewMode(self):
        if(self.playerController.GetMyself().GetPlayerState().GetValue(PlayerState.PLAYING_STATE) == PlayerState.PS_PLAYING):
            self.camera.ToggleViewMode()
        
    def ToggleFullScreen(self):
        fullscreen = not base.win.isFullscreen()
        props = WindowProperties( base.win.getProperties() )
        
        if(not fullscreen):
            props.setFullscreen(False)
            props.setSize(850, 480)
        
        else:
            props.setFullscreen(True)
            w = base.pipe.getDisplayWidth()
            h = base.pipe.getDisplayHeight()
            if w and h:
                props.setSize(w,h)
            else:
                props.setSize(850, 480)
        
        base.win.requestProperties(props)
                
        messenger.send('window-event',[base.win])
        
#    def IsFull(self):
#        return self.playerController.IsFull()
        
        
    #------------------------------
    # Accessing Important Objects
    #------------------------------
    
    def GetPlayerController(self):
        return self.playerController
    
    def GetEnvironment(self):
        return self.environment
    
    def GetCamera(self):
        return self.camera
        
    #------------------------------------------
    # Cleanup (on destruction of Game object)
    #------------------------------------------
        
    def CleanUp(self):
        taskMgr.remove('GameEngineTick')
#        self.loadingScreen.Destroy()
#        del self.loadingScreen
        self.camera.Destroy()
        del self.camera
        self.playerController.Destroy()
        del self.playerController  
        self.game.Destroy()
        del self.game
        self.environment.Destroy()
        del self.environment  
        self.hud.Destroy() 
        del self.hud
        self.menuController.Destroy()
        del self.menuController
        self.chat.Destroy()
        del self.chat
        self.fpsCounter.Destroy()
        del self.fpsCounter
        #self.itemInWorldController.Destroy()
        for c in render.getChildren():
            c.removeNode()
        self.ignoreAll()
       
    def Exit(self):
        sys.exit() 
        
        