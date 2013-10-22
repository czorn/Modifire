from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode

from gui.GUIOrder import GUIOrder
from event.InventoryEvent import AmmoChangeEvent, SelectedItemChangeEvent
import Globals

class HUDBottomRight(DirectObject):
    
    def __init__(self):
        self.node = base.a2dBottomRight.attachNewNode('hudBottomRight')#GUIOrder.ORDER[GUIOrder.HUD])
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.ammoIcon = OnscreenImage(image = 'Assets/Images/HUD/HUDBottomRight.png', scale = 512.0 / 1024, pos = (-0.5, 0, 0.5))
        self.ammoIcon.setTransparency(TransparencyAttrib.MAlpha)
        self.ammoIcon.reparentTo(self.node)
        
        self.ammoTextClip = OnscreenText(text = '30', pos = (-0.35, 0.09), scale = 0.12, fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1), mayChange = True, align=TextNode.ARight, font = Globals.FONT_SAF)
        self.ammoTextClip.reparentTo(self.node)
        self.ammoTextClip.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.ammoTextLeft = OnscreenText(text = '90', pos = (-0.23, 0.05), scale = 0.07, fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1), mayChange = True, align=TextNode.ARight, font = Globals.FONT_SAF)
        self.ammoTextLeft.reparentTo(self.node)
        self.ammoTextLeft.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        
        self.accept(AmmoChangeEvent.EventName, self.OnAmmoChangeEvent)
        self.accept(SelectedItemChangeEvent.EventName, self.OnSelectedItemChangeEvent)
        
    def OnAmmoChangeEvent(self, event):
        item = event.GetItem()
        if(item and item.GetCurrentClipAmmo() == ''):
            self.ChangeAmmoText('', '')
        else:
            self.ChangeAmmoText(str(item.GetCurrentClipAmmo()), str(item.GetTotalRemainingAmmo()))
            
    def ChangeAmmoText(self, clip, total):
        self.ammoTextClip.setText(clip)
        self.ammoTextLeft.setText(total)
        
    def OnSelectedItemChangeEvent(self, event):
        if(event.GetItemStack() and event.GetItemStack().GetItem()):
            self.OnAmmoChangeEvent(AmmoChangeEvent(None, event.GetItemStack().GetItem()))
        else:
            self.ChangeAmmoText('', '')
        
    def Destroy(self):
        self.ignoreAll()
        self.ammoIcon.removeNode()
        self.ammoTextClip.removeNode()
        self.ammoTextLeft.removeNode()
        self.node.removeNode()