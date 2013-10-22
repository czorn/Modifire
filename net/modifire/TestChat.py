from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from gui.chat.ChatBox import ChatBox
from hud.DeathNotifications import DeathNotifications

  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        wp = WindowProperties()
        wp.setSize(850, 480)
        wp.setTitle("GAME")
        base.win.requestProperties(wp)
        
        c = DeathNotifications()
        
        self.accept('a', c.AddMessage, extraArgs=['Player1', 'mp5', 'Tedasdasd'])

app = MyApp() 
app.run()
