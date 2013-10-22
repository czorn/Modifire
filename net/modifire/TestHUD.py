from direct.showbase.ShowBase import ShowBase

import Globals
from hud.HUD import HUD

  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        Globals.FONT_SAF = loader.loadFont('Assets/Fonts/SAF.otf')
        Globals.FONT_SAF.setPixelsPerUnit(60)
        
        self.hud = HUD(None)

app = MyApp() 
app.run()








    
    
run()