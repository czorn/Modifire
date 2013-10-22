import sys
 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec4, WindowProperties #@UnresolvedImport
from pandac.PandaModules import PStatClient, TextNode
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'sync-video 0')

import Globals
from netcode.Server import Server
from gui.menus.ServerOptionsMenu import ServerOptionsMenu
from event.ServerEvent import ServerStartEvent
from LoadingScreen import LoadingScreen

import SettingsController
  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        version = OnscreenText(text = Globals.VERSION, pos = (0.3, -0.07), scale = 0.07, fg = (1, 1, 1, 1))
        version.reparentTo(base.a2dTopLeft)
        Globals.OFFLINE = False
        
        #PStatClient.connect()
        
        wp = WindowProperties()
        wp.setSize(850, 480)
        wp.setTitle("SERVER")
        base.win.requestProperties(wp)
        base.win.setClearColor(Vec4(0.133, 0.133, 0.133, 1)) 
        #self.disableMouse()
        
        SettingsController.LoadServerSettings()
        
        self.options = ServerOptionsMenu()
        self.accept('escape', self.Exit)
        self.accept(ServerStartEvent.EventName, self.Start)
        
        #self.Start()
        
    def Start(self, event):
        del self.options
        SettingsController.SaveServerSettings()
        taskMgr.doMethodLater(0.1, self.StartServer, 'StartServer')
        self.loadingScreen = LoadingScreen() 
        
    def StartServer(self, task = None):
        self.server = Server()
        
    def Exit(self):
        self.server.Exit()
        sys.exit()
        
 
app = MyApp() 
app.run()
