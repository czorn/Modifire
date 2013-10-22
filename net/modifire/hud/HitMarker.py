from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib, Vec4, Vec3
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Func, LerpColorInterval, Wait

from gui.GUIOrder import GUIOrder
from event.PlayerEvent import PlayerHitEvent
from player.PlayerState import PlayerState

import Globals


class HitMarker(DirectObject):
    
    def __init__(self):
        self.node = aspect2d.attachNewNode('hitmarker')#GUIOrder.ORDER[GUIOrder.HUD])
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.indicator = OnscreenImage(image = 'Assets/Images/HUD/HitMarker.png', scale = 64.0 / 1024)
        self.indicator.setTransparency(TransparencyAttrib.MAlpha)
        self.indicator.reparentTo(self.node)
        
        self.alphaSeq = Sequence(Wait(0.2),
                                 LerpColorInterval(self.node, 0.2, Vec4(1, 1, 1, 0), Vec4(1, 1, 1, 1)),
                                 Func(self.Hide))
        
        self.node.hide()
        
        self.accept(PlayerHitEvent.EventName, self.OnPlayerHitEvent)
        
    def Hide(self):
        self.node.hide()
        
    def Show(self):
        self.node.show()
        self.node.setColor(Vec4(1, 1, 1, 1))
        
    def OnPlayerHitEvent(self, event):
        if(event.GetAttacker().GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            self.Show()
            self.alphaSeq.start(startT = 0)      
        
    def Destroy(self):
        self.alphaSeq.finish()
        self.ignoreAll()
        self.indicator.removeNode()
        self.node.removeNode()
        
        
        