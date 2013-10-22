
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from direct.showbase.DirectObject import DirectObject

from gui.GUIOrder import GUIOrder
from event.HUDEvent import CrossHairEvent

class CrossHair(DirectObject):
    
    def __init__(self):
        self.node = aspect2d.attachNewNode('hud')#GUIOrder.ORDER[GUIOrder.HUD])
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        filename = 'cross2.png'
        
        self.normal = self.node.attachNewNode('NormalCrossHair')
        
        self.top = self.LoadImage(filename) 
        
        self.right = self.LoadImage(filename)
        self.right.setR(90)
        
        self.left = self.LoadImage(filename)
        self.left.setR(-90)
        
        self.bottom = self.LoadImage(filename)
        self.bottom.setR(180)
        
        self.crossHairs = {'Normal' : self.normal}
        
        self.accept(CrossHairEvent.EventName, self.OnCrossHairEvent)
        
    def LoadImage(self, filename):
        x = OnscreenImage(image = 'Assets/Images/Crosshairs/' + filename, scale = 128.0 / 1024)
        x.setTransparency(TransparencyAttrib.MAlpha)
        x.reparentTo(self.normal) 
        
        return x
    
    def LoadCrosshair(self, filename):
        parentNode = self.node.attachNewNode('CrossHair')
        
        if('Sniper' in filename):
            x = OnscreenImage(image = 'Assets/Images/Crosshairs/OuterBlack.png', scale = 2.2)
            x.setTransparency(TransparencyAttrib.MAlpha)
            x.reparentTo(parentNode)
        
        x = OnscreenImage(image = 'Assets/Images/Crosshairs/%s.png' % (filename), scale = 1)
        x.setTransparency(TransparencyAttrib.MAlpha)
        x.reparentTo(parentNode)
        
        parentNode.hide()
        return parentNode
    
    def OnCrossHairEvent(self, event):
        name = event.GetFilename()
        print event.GetFilename(), event.GetShow()
        if(name not in self.crossHairs.keys()):
            self.crossHairs[name] = self.LoadCrosshair(name)
            
        if(event.GetShow()):
            self.crossHairs[name].show()
        else:
            self.crossHairs[name].hide()
    
    def Show(self):
        self.node.show()
        
    def Hide(self):
        self.node.hide()