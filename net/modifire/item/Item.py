
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Func, Wait
from direct.actor.Actor import Actor
from panda3d.core import Vec3 #@UnresolvedImport

import Settings
import Globals
from item.ItemIcon import ItemIcon
from item.ItemId import ItemId
from gui.GUIOrder import GUIOrder

class Item():
    
    def __init__(self):
        self.itemId = ItemId.NoItem
        self.itemIcon = None    # The icon of the item for the main inventory
        self.hotbarItemIcon = None    # The icon of the item for the main inventory
        self.invWidth = 0       # Width the item takes up in the inventory
        self.invHeight = 0      # Height the item taske up in the inventory
        self.modelName = ''     # The filename of the model
        self.model = None       # The visible model of the item
        self.dequipTime = 0     # How long it takes to 'put away' the item into the inventory
        self.equipTime = 0      # How long it takes to 'get' the item from the inventory
        self.hiddenPos = Vec3(0.3, 0.3, -0.3)   # The location of the item when it's unequipped
        self.equippedPos = Vec3(0.3, 0.3, -0.1) # The location of the item when it's equipped
        self.equipSeq = Sequence()
        self.dequipSeq = Sequence()
        self.equipDequipSeq = Sequence()
        self.timeSinceLastUse = 0
        self.useDelay = 1
        self.isReady = False
        self.name = '???'
        self.playerId = Globals.MY_PID
        
    def LoadContent(self):
        if(self.model is None):
            self.model = loader.loadModel('Assets/Models/Items/%s' % (self.modelName))
            self.model.setPos(self.hiddenPos)
            print 'Loaded Assets/Models/Items/%s' % (self.modelName)
            return True
        return False
        
    def LoadIcon(self, parentNode):
        if(self.itemIcon is None):
            self.itemIcon = ItemIcon(self.modelName, parentNode)
            self.itemIcon.setBin('fixed', GUIOrder.ORDER[GUIOrder.INV_LOW])
            
    def LoadHotbarIcon(self, parentNode):
        if(self.hotbarItemIcon is None):
            self.hotbarItemIcon = ItemIcon(self.modelName, parentNode)
            self.hotbarItemIcon.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD_ITEM])
        
    def IncreaseTimeSinceLastUse(self, dt):
        self.timeSinceLastUse += dt
        
    def CanUse(self):
        return (self.timeSinceLastUse > self.useDelay) and self.isReady
    
    def Used(self):
        self.timeSinceLastUse = 0
        
    def Use(self):
        pass
    
    def AlternateUse(self):
        pass
    
    def SetIsReady(self, value):
        self.isReady = value
    
    def Equip(self):
        print 'equipping', self
        if(self.dequipSeq.isPlaying()):
            self.dequipSeq.finish()
            
        if(Settings.IS_SERVER):
            self.equipSeq = Sequence(Wait(self.equipTime),
                                     Func(self.SetIsReady, True))
        else:
            self.equipSeq = Sequence(Func(self.Show),
                                     LerpPosInterval(self.model, self.equipTime, self.equippedPos),
                                     Func(self.SetIsReady, True))
        self.equipSeq.start()
        
    def EquipDequip(self, otherItem):
        self.equipDequipSeq = Sequence(Func(otherItem.Dequip),
                                         Wait(otherItem.equipTime),
                                         Func(self.Equip))
        self.equipDequipSeq.start()
#        if(Settings.IS_SERVER):
#            Sequence(Func(otherItem.SetIsReady, False),
#                     Wait(otherItem.equipTime),
#                     Wait(self.equipTime),
#                     Func(self.SetIsReady, True)).start()
#        else:
#            Sequence(Func(otherItem.SetIsReady, False),
#                     LerpPosInterval(otherItem.model, otherItem.equipTime, otherItem.hiddenPos, otherItem.equippedPos),
#                     Func(otherItem.Hide),
#                     Func(self.Show),
#                     LerpPosInterval(self.model, self.equipTime, self.equippedPos, self.hiddenPos),
#                     Func(self.SetIsReady, True)).start()
    
    def Dequip(self):
        print 'dequipping', self
        if(self.equipSeq.isPlaying()):
            self.equipSeq.finish()
        
        if(self.equipDequipSeq.isPlaying()):
            self.equipDequipSeq.finish()
            
        if(Settings.IS_SERVER):
            self.dequipSeq = Sequence(Func(self.SetIsReady, False),
                                      Wait(self.equipTime))
        else:
            self.dequipSeq = Sequence(Func(self.SetIsReady, False),
                                      LerpPosInterval(self.model, self.equipTime, self.hiddenPos),
                                      Func(self.Hide))
        self.dequipSeq.start()
        
    def Show(self):
        self.model.show()
        
    def Hide(self):
        self.model.hide()
        
    def ReparentTo(self, node):
        self.model.reparentTo(node)
    
    def GetItemWidth(self):
        return self.invWidth
    
    def GetItemHeight(self):
        return self.invHeight
    
    def GetItemIcon(self):
        return self.itemIcon
    
    def GetItemHotbarIcon(self):
        return self.hotbarItemIcon
    
    def GetItemId(self):
        return self.itemId
    
    def GetFireMode(self):
        return None
    
    def GetPossibleItems(self):
        return []
    
    def GetRecipe(self):
        return []
    
    def GetBaseWeapon(self):
        return None
    
    def GetWeapon(self, fm):
        return None
    
    def GetName(self):
        return self.name
    
    def GetCurrentClipAmmo(self):
        return ''
    
    def GetTotalRemainingAmmo(self):
        return ''
    
    def GetItemData(self):
        return []
    
    def DestroyHotbarIcon(self):
        if(self.hotbarItemIcon):
            self.hotbarItemIcon.Destroy()
            self.hotbarItemIcon = None
            
    def DestroyIcon(self):
        if(self.itemIcon):
            self.itemIcon.Destroy()
            self.itemIcon = None
    
    def Destroy(self):
        print 'Destroying', self
        if(self.model):
            if(isinstance(self.model, Actor)):
                self.model.cleanup()
            self.model.removeNode()
        self.DestroyIcon()
        self.DestroyHotbarIcon()
        if(self.dequipSeq.isPlaying()):
            self.dequipSeq.finish()
        if(self.equipSeq.isPlaying()):
            self.equipSeq.finish()
            
    def GetPos(self, coordSpace = None):
        if(coordSpace):
            return self.model.getPos(coordSpace)
        else:
            return self.model.getPos()