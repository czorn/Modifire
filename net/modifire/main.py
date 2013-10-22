import sys
 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec4, Vec3, WindowProperties, ConfigVariableString #@UnresolvedImport
from pandac.PandaModules import PStatClient
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "interpolate-frames 1")
loadPrcFileData('', 'sync-video 0')
loadPrcFileData('', 'audio-library-name p3fmod_audio')

# Client
"""
packp3d -S mycert.pem -r morepy -r audio -r fmod -r rocket -n mapc -o client.p3d -d C:\Users\Chris\Modifire\net\modifire\
"c:\Program Files (x86)\Panda3D\panda3d.exe" client.p3d

"""

"""
packp3d -o client.p3d -d C:\Users\Chris\Desktop\modifire\modifire
"c:\Program Files\Panda3D\panda3d.exe" client.p3d

"""

# Server
"""
packp3d -S mycert.pem -r morepy -r rocket -n mapc -o server.p3d -d C:\Users\Chris\Modifire\net\modifire\ -m mainServer.py
"c:\Program Files (x86)\Panda3D\panda3d.exe" server.p3d

"""

"""
packp3d -o server.p3d -d C:\Users\Chris\Desktop\modifire\modifire -m mainServer.py
"c:\Program Files\Panda3D\panda3d.exe" server.p3d

"""

from gui.menus.MainMenu import MainMenu
from Engine import Engine
from netcode.Client import Client
from event.ClientEvent import LoadEngineEvent, EngineLoadedEvent, ServerJoinResponseEvent, PeerTimeoutEvent
from LoadingScreen import LoadingScreen
from Preloader import Preloader
import Settings
import Globals
import GameTime
import SettingsController
  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        Globals.OFFLINE = False
        self.client = 0
        self.engine = 0
        
        #PStatClient.connect()
        
        wp = WindowProperties()
        wp.setSize(Settings.WIDTH, Settings.HEIGHT)
        wp.setTitle("Modifire")
        wp.setMouseMode(WindowProperties.MRelative)
        #wp.setCursorHidden(True) 
        base.win.requestProperties(wp)
        base.setBackgroundColor(0.133, 0.133, 0.133) 
        self.disableMouse()
        self.client = Client()
        self.mainMenu = MainMenu()
        self.SetupEventHandlers()
        self.pid = -1
        self.loadingScreen = None
        
        SettingsController.LoadClientSettings()
        
        version = OnscreenText(text = Globals.VERSION, pos = (0.3, -0.07), scale = 0.07, fg = (1, 1, 1, 1))
        version.reparentTo(base.a2dTopLeft)
        version.setBin('fixed', 200)
        
        Preloader.Preload()
        
        #self.mainMenu.Hide()
        #self.LoadEngine(None)
        #self.OnStartOffline()
        
    def SetupEventHandlers(self):
        #self.accept('escape', self.Exit)
        self.accept('mainMenuMulti', self.AttemptConnection)
        self.accept('mainMenuExit', self.Exit)
        self.accept('fileTransferComplete', self.OnFileTransferComplete)
        self.accept('goBackToMain', self.LeaveGameToMainmenu)
        self.accept('startOffline', self.OnStartOffline)
        self.accept(LoadEngineEvent.EventName, self.LoadEngine)
        self.accept(ServerJoinResponseEvent.EventName, self.OnServerJoinResponseEvent)
        self.accept(PeerTimeoutEvent.EventName, self.LeaveGameToMainmenu)
        
    def OnStartOffline(self):
        Globals.OFFLINE = True
        Globals.WORLD_SEED = Settings.LAST_WORLD
        self.OnServerJoinResponseEvent(ServerJoinResponseEvent(True, ''))
        self.LoadEngine(None)
        
    def LeaveGameToMainmenu(self, event = None):
        if(not Globals.OFFLINE):
            self.client.Disconnect()
        if(self.engine):
            self.engine.CleanUp()
            del self.engine
            self.engine = None
        self.client.engine = self.engine
        self.client.CleanUp()
        if(self.loadingScreen):
            self.loadingScreen.Destroy()
            del self.loadingScreen
        self.mainMenu.Show()
        
        if(event):
            self.mainMenu.CreateAlertPopup('Server Timeout', 'Lost connection with server.', self.mainMenu.OnAlertPopupClose, self.mainMenu.OnAlertPopupClose)
        
    def OnServerJoinResponseEvent(self, event):
        base.setBackgroundColor(0.133, 0.133, 0.133) 
        if(event.GetResponse()):
            self.mainMenu.Hide()
            self.loadingScreen = LoadingScreen() 
        
    def LoadEngine(self, event):
        print 'MY ID', Globals.MY_PID
        self.engine = Engine(Globals.MY_PID, Globals.WORLD_SEED)
        self.client.engine = self.engine
        self.engine.client = self.client
        if(not Globals.OFFLINE):
            self.client.fsm.request('PlayingGame')
        print 'engine loaded'
        EngineLoadedEvent().Fire()
        
        
    def OnFileTransferComplete(self, filename):
        if(filename):
            self.StartEngine(self.pid, filename)
            self.engine.CreateInitialPlayers(self.tempPlayerStates)
            del self.tempPlayerStates
            self.client.engine = self.engine
            self.engine.client = self.client
            print 'game loaded', GameTime.GetTime()
            self.engine.OnEngineLoaded()
            self.client.fsm.request('PlayingGame')
        
    def AttemptConnection(self):
        print 'connecting to ', Settings.SERVER
        self.client.ConnectToServer(Settings.SERVER)
        
    def Exit(self):
        self.settingsController.SaveSettings()
        
        if(self.client):
            self.client.Exit()
        if(self.engine):
            self.engine.Exit()
        sys.exit()
        
 
app = MyApp() 
app.run()
