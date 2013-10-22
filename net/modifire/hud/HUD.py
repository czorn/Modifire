from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject

import Globals

from gui.GUIOrder import GUIOrder
from hud.HUDHotbar import HUDHotbar
from hud.HUDBottomLeft import HUDBottomLeft
from hud.HUDBottomRight import HUDBottomRight
from hud.EnemyFireIndicator import EnemyFireIndicator
from hud.HitMarker import HitMarker
from hud.CrossHair import CrossHair
from player.PlayerState import PlayerState
from event.PlayerEvent import PlayerSelectedEvent, PlayerDeathEvent
from event.CameraEvent import ADSEvent

class HUD(DirectObject):
    
    def __init__(self, engine):
        print 'new hud'
        self.engine = engine
        self.node = aspect2d.attachNewNode('hud')#GUIOrder.ORDER[GUIOrder.HUD])
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        self.crossHair = CrossHair()
#        self.crossHair = OnscreenImage(image = 'Assets/Images/Crosshairs/cross.png', scale = 256.0 / 1024)
#        self.crossHair.setTransparency(TransparencyAttrib.MAlpha)
#        self.crossHair.reparentTo(self.node)
        
        if(engine):
            self.hudHotbar = HUDHotbar(engine.menuController.invGUI.mainInventory)
        
        self.selectedPlayerName =  OnscreenText(text = '', pos = (0, -0.7), scale = 0.06, fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1), mayChange = True)
        self.selectedPlayerName.reparentTo(self.node)
        self.selectedPlayerName.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.personalDeathMessage =  OnscreenText(text = '', pos = (0, -0.6), scale = 0.06, fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1), mayChange = True)
        self.personalDeathMessage.reparentTo(self.node)
        self.personalDeathMessage.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.HUDBL = HUDBottomLeft()
        self.HUDBR = HUDBottomRight()
        self.enemyFireIndicator = EnemyFireIndicator()
        self.hitMarker = HitMarker()
        
        self.accept(PlayerSelectedEvent.EventName, self.OnPlayerSelectedEvent)
        self.accept(PlayerDeathEvent.EventName, self.OnPlayerDeathEvent)
        self.accept(ADSEvent.EventName, self.OnADSEvent)
        
    def Update(self):
        self.enemyFireIndicator.Update()
        
    def SelectionIncrease(self):
        self.hudHotbar.SelectionIncrease()
        
    def SelectionDecrease(self):
        self.hudHotbar.SelectionDecrease()
        
    def GetCurrentItem(self):
        return self.hudHotbar.GetCurrentItem()
    
    def GetSelectedIndex(self):
        return self.hudHotbar.selectedIndex
    
    # If we hover over an enemy, show their name
    # After a short delay, hide it
    def OnPlayerSelectedEvent(self, event):
        player = event.GetPlayer()
        if(not player):
            return
        
        taskMgr.remove('ClearSelectedPlayerName_%s' % player.GetPlayerState().GetValue(PlayerState.PID))
        if(player.GetPlayerState().GetValue(PlayerState.TEAM) != Globals.MY_TEAM):
            player.ShowNameAboveHead()
            taskMgr.doMethodLater(0.05, player.FadeOutNameAboveHead, 'ClearSelectedPlayerName_%s' % player.GetPlayerState().GetValue(PlayerState.PID))
            
#    def OnPlayerSelectedEvent(self, event):
#        player = event.GetPlayer()
#        taskMgr.remove('ClearSelectedPlayerName')
#        if(player):
#            self.selectedPlayerName.setText(player.GetPlayerState().GetValue(PlayerState.NAME))
#        else:
#            taskMgr.doMethodLater(3, self.ClearSelectedPlayerName, 'ClearSelectedPlayerName')
        
    def OnPlayerDeathEvent(self, event):
        victim = event.GetVictim()
        attacker = event.GetAttacker()
        taskMgr.remove('ClearPersonalDeathMessage')
        
        if(victim.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            self.personalDeathMessage.setText("You were killed by %s" % (attacker.GetPlayerState().GetValue(PlayerState.NAME)))
            taskMgr.doMethodLater(3, self.ClearPersonalDeathMessage, 'ClearPersonalDeathMessage')
            self.ClearSelectedPlayerName()
                                            
        elif(attacker.GetPlayerState().GetValue(PlayerState.PID) == Globals.MY_PID):
            self.personalDeathMessage.setText("You killed %s" % (victim.GetPlayerState().GetValue(PlayerState.NAME)))
            taskMgr.doMethodLater(4, self.ClearPersonalDeathMessage, 'ClearPersonalDeathMessage')
            self.ClearSelectedPlayerName()
        
    def ClearSelectedPlayerName(self, task = None):
        self.selectedPlayerName.setText('')
        
    def ClearPersonalDeathMessage(self, task = None):
        self.personalDeathMessage.setText('')
        
    def OnADSEvent(self, event):
        pass
#        if(event.GetIsADS()):
#            self.HideCrosshairs()
#        else:
#            self.ShowCrosshairs()
        
    def ShowCrosshairs(self):
        self.crossHair.Show()
        
    def HideCrosshairs(self):
        self.crossHair.Hide()
        
    def EnableKeyboardListening(self):
        self.hudHotbar.EnableKeyboardListening()
        
    def DisableKeyboardListening(self):
        self.hudHotbar.DisableKeyboardListening()
        
    def Destroy(self):
        self.ignoreAll()
        self.node.removeNode()
        self.hudHotbar.Destroy()
        self.HUDBL.Destroy()
        self.HUDBR.Destroy()
        self.enemyFireIndicator.Destroy()
        self.hitMarker.Destroy()
        del self.hudHotbar