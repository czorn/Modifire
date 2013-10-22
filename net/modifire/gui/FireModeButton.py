import Settings

from direct.gui.DirectGui import DirectButton
#457, 412
class FireModeButton():
    
    (FM_AUTO, FM_BURST, FM_SEMI) = range(3)
    
    #egg-texture-cards -o FM_Auto.egg -p 100,50 FM_Auto.png FM_Auto_Over.png
    #egg-texture-cards -o FM_Burst.egg -p 100,50 FM_Burst.png FM_Burst_Over.png
    #egg-texture-cards -o FM_Semi.egg -p 100,50 FM_Semi.png FM_Semi_Over.png
    
    def __init__(self, invNode):        
        x = 450
        y = 409
        self.autoImage = self.MakeButton('FM_Auto', 'FM_Auto', 'FM_Auto_Over', x, y, self.CycleModes, invNode)
        self.semiImage = self.MakeButton('FM_Semi', 'FM_Semi', 'FM_Semi_Over', x, y, self.CycleModes, invNode)
        self.burstImage = self.MakeButton('FM_Burst', 'FM_Burst', 'FM_Burst_Over', x, y, self.CycleModes, invNode)
        self.boltImage = self.MakeButton('FM_Burst', 'FM_Burst', 'FM_Burst_Over', x, y, self.CycleModes, invNode)
        
        self.states = [self.boltImage, self.semiImage, self.burstImage, self.autoImage]
        self.index = 0
        
        self.states[0].show()
        
    def MakeButton(self, egg, up, over, x, y, cmd, parent):
        maps = loader.loadModel("Assets/Images/Inventory/%s" % (egg))
        b = DirectButton(geom = (maps.find('**/%s' % (up)),
                         maps.find('**/%s' % (over)),
                         maps.find('**/%s' % (over)),
                         maps.find('**/%s' % (up))),
                         command = cmd,
                         pressEffect = 0,
                         relief = None,
                         rolloverSound = None, 
                         clickSound = None,
                         scale = (150./1024.0, 1, 75.0/1024.0))
        b.reparentTo(parent)
        b.hide()
        
        diff = Settings.WIDTH - Settings.HEIGHT
        xOff = 0
        yOff = 0
        if(diff > 0):
            xOff = diff / 2
        else:
            yOff = diff / 2
        
        x = Settings.Transpose(x + 50, 1024) + xOff
        y = Settings.Transpose(y + 25, 1024) + yOff
            
        centerX = Settings.WIDTH / 2
        centerY = Settings.HEIGHT / 2
        
        newX = 1.0 * (x - centerX) / (centerX - xOff)
        newY = 1.0 * (centerY - y) / (centerY - yOff)
        
        b.setX(newX)
        b.setZ(newY)
        
        return b
        
    def CycleModes(self):
        self.states[self.index].hide()
        self.index = (self.index + 1) % 4
        self.states[self.index].show()
        
    def SetMode(self, mode):
        self.states[self.index].hide()
        self.index = mode
        self.states[self.index].show()
        
    def GetMode(self):
        return self.index
    
    
    
    
    