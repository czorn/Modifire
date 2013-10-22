from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode
from direct.interval.IntervalGlobal import LerpColorInterval, LerpColorScaleInterval, Sequence

import Globals
from gui.GUIOrder import GUIOrder
from event.PlayerEvent import PlayerHealthEvent

class HUDBottomLeft(DirectObject):
    
    def __init__(self):
        self.node = base.a2dBottomLeft.attachNewNode('hudhealth')#GUIOrder.ORDER[GUIOrder.HUD])
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.health = OnscreenImage(image = 'Assets/Images/HUD/HUDBottomLeft.png', scale = 512.0 / 1024, pos = (0.5, 0, 0.5))
        self.health.setTransparency(TransparencyAttrib.MAlpha)
        self.health.reparentTo(self.node)
        
        self.healthText = OnscreenText(text = '100', pos = (0.2, 0.07), scale = 0.12, fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1), mayChange = True, font = Globals.FONT_SAF, align=TextNode.ALeft)
        self.healthText.reparentTo(self.node)
        self.healthText.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.healthColorSeq = Sequence(LerpColorScaleInterval(self.node, 0.25, Globals.COLOR_RED),
                                       LerpColorScaleInterval(self.node, 0.25, Globals.COLOR_WHITE))
        
        self.dieingColorSeq = Sequence(LerpColorScaleInterval(self.node, 1, Globals.COLOR_RED),
                                       LerpColorScaleInterval(self.node, 1, Globals.COLOR_WHITE))
        
        self.accept(PlayerHealthEvent.EventName, self.OnPlayerHealthEvent)
        
    def OnPlayerHealthEvent(self, event):
        health = event.GetHealth()
        self.healthText.setText(str(health))
        if(health < 16):
            #self.node.setColor(Globals.COLOR_RED)
            self.dieingColorSeq.loop()
        elif(health == 100):
            self.dieingColorSeq.finish()
        else:
            self.healthColorSeq.start()        
        
    def Destroy(self):
        self.ignoreAll()
        self.health.removeNode()
        self.healthText.removeNode()
        self.node.removeNode()