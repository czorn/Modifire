from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib, Vec4, Vec3
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Func, LerpColorInterval, Wait

from gui.GUIOrder import GUIOrder
from event.PlayerEvent import PlayerHitEvent
from player.PlayerState import PlayerState

import Globals


class EnemyFireIndicator(DirectObject):
    
    def __init__(self):
        self.node = aspect2d.attachNewNode('hudhealth')#GUIOrder.ORDER[GUIOrder.HUD])
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.lastAttacker = None
        
        self.indicator = OnscreenImage(image = 'Assets/Images/HUD/EnemyFireIndicator.png')
        self.indicator.setTransparency(TransparencyAttrib.MAlpha)
        self.indicator.reparentTo(self.node)
        
        self.alphaSeq = Sequence(Wait(0.75),
                                 LerpColorInterval(self.node, 0.75, Vec4(1, 1, 1, 0), Vec4(1, 1, 1, 1)),
                                 Func(self.Hide))
        
        self.node.hide()
        
        self.accept(PlayerHitEvent.EventName, self.OnPlayerHitEvent)
        
    def Hide(self):
        self.node.hide()
        self.lastAttacker = None
        
    def Show(self):
        self.node.show()
        self.node.setColor(Vec4(1, 1, 1, 1))
        
    def Update(self):
        if(self.lastAttacker):
            self.node.setR(self.GetTheta(self.me, self.lastAttacker))
            
    def GetTheta(self, victim, attacker):
        victimLookingDir = victim.GetPlayerState().GetValue(PlayerState.LOOKING_DIRECTION)
        victimLookingDir.setZ(0)
        victimLookingDir.normalize()
        victimLookingDir = Vec3(victimLookingDir)
        
        attackerToVictimVector = victim.GetPos() - attacker.GetPos()
        attackerToVictimVector.setZ(0)
        attackerToVictimVector.normalize()
        attackerToVictimVector = Vec3(attackerToVictimVector)
        
        return attackerToVictimVector.signedAngleDeg(victimLookingDir, Globals.UP_VECTOR)
        
    def OnPlayerHitEvent(self, event):
        victim = event.GetVictim()
        attacker = event.GetAttacker()
        
        if(victim and victim.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            self.me = victim
            self.lastAttacker = attacker
            
            theta = self.GetTheta(victim, attacker)
            
            self.node.setR(theta)
            self.Show()
            self.alphaSeq.start(startT = 0)
        
    def Destroy(self):
        self.alphaSeq.finish()
        self.ignoreAll()
        self.indicator.removeNode()
        self.node.removeNode()
        
        
        