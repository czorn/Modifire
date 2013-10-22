from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from direct.showbase.DirectObject import DirectObject
from panda3d.core import VBase3 #@UnresolvedImport

import Globals
from hud.SelectionBox import SelectionBox
from gui.GUIOrder import GUIOrder
from event.InventoryEvent import InventoryChangeEvent, SelectedItemChangeEvent
from inventory.MainInventory import MainInventory

class HUDHotbar(DirectObject):
    
    def __init__(self, mainInventory):
        self.mainInventory = mainInventory
        self.hbNode = aspect2d.attachNewNode('hudhotbar')
        self.hbNode.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD])
        print self.hbNode
        self.currentItems = []
        self.selectedIndex = 0
        self.lastItem = None
        self.LoadContent()
        self.selectionBox = SelectionBox(self.hbNode)
        self.UpdateSelectionBox()
        self.accept(InventoryChangeEvent.EventName, self.OnInventoryChange)
        
        invHotbarCoords = Globals.ConvertFromImageAbsoluteToAspect2D(263, 741, 1024)
        coords = Globals.ConvertFromImageAbsoluteToAspect2D(374, 977, 1024)
        self.dVec = VBase3(coords[0] - invHotbarCoords[0], 0, coords[1] - invHotbarCoords[1])
        
        
        
    def EnableKeyboardListening(self):
        self.accept('wheel_down', self.SelectionIncrease)
        self.accept('wheel_up', self.SelectionDecrease)
        self.accept('1', self.SelectSlot, [1])
        self.accept('2', self.SelectSlot, [2])
        self.accept('3', self.SelectSlot, [3])
        self.accept('4', self.SelectSlot, [4])
        self.accept('5', self.SelectSlot, [5])
        
    def DisableKeyboardListening(self):
        self.ignore('wheel_down')
        self.ignore('wheel_up')
        self.ignore('1')
        self.ignore('2')
        self.ignore('3')
        self.ignore('4')
        self.ignore('5')
         
    def LoadContent(self):
        self.inventoryBackground = OnscreenImage(image = 'Assets/Images/HUD/HUDHotbar.png')
        self.inventoryBackground.setTransparency(TransparencyAttrib.MAlpha)
        self.inventoryBackground.reparentTo(self.hbNode)
        print self.hbNode
        
    def UpdateSelectionBox(self):
        itemStack = self.mainInventory.GetItemStack(self.selectedIndex, 0)
        if(itemStack):
            self.selectedIndex = min([slot.x for slot in itemStack.GetParentSlots()])
        if(itemStack != self.lastItem):
                SelectedItemChangeEvent(self.mainInventory, itemStack).Fire()
        self.lastItem = itemStack
        self.selectionBox.Update(itemStack, self.selectedIndex)
            
    def UpdateIcons(self, inventory):
        print 'updating icons'
        def IsHotbarItemStack(itemStack):
            return itemStack.GetParentSlots()[0].y == 0
        
        for item in self.currentItems:
            item.DestroyHotbarIcon()
        self.currentItems = []
        
        hotbarItemStacks = filter(IsHotbarItemStack, inventory.GetItemStacks())
        
        for itemStack in hotbarItemStacks:
            item = itemStack.GetItem()
            print 'loadicon', item, self.hbNode
            item.LoadHotbarIcon(self.hbNode)
            itemIcon = item.GetItemHotbarIcon()
            parentSlots = itemStack.GetParentSlots()
            
            pos = VBase3(0, 0, 0)
            numSlots = 0
            for parentSlot in parentSlots:
                numSlots += 1
                pos += parentSlot.GetInventorySlotButton().GetPos()
            pos /= 1.0 * numSlots
            pos += self.dVec
            
            itemIcon.SetPos(pos)
            self.currentItems.append(item)
        
        self.UpdateSelectionBox()
            
    def SelectionIncrease(self):
        self.selectedIndex = (self.selectedIndex + 1) % 5
        itemStack = self.mainInventory.GetItemStack(self.selectedIndex, 0)
        if(itemStack and itemStack == self.lastItem):
            self.SelectionIncrease()
        else:
            if(itemStack != self.lastItem):
                SelectedItemChangeEvent(self.mainInventory, itemStack).Fire()
            self.lastItem = itemStack
            self.UpdateSelectionBox()
        
    def SelectionDecrease(self):
        self.selectedIndex = (self.selectedIndex + 4) % 5
        itemStack = self.mainInventory.GetItemStack(self.selectedIndex, 0)
        if(itemStack and itemStack == self.lastItem):
            self.SelectionDecrease()
        else:
            i = self.selectedIndex
            while 1:
                i = (i + 4) % 5
                newItemStack = self.mainInventory.GetItemStack(i, 0)
                if(not (newItemStack and newItemStack == itemStack)):
                    break
            if(itemStack != self.lastItem):
                SelectedItemChangeEvent(self.mainInventory, itemStack).Fire()
            self.lastItem = itemStack
            self.selectedIndex = (i + 1) % 5
            self.UpdateSelectionBox()
            
    def SelectSlot(self, index):
        print 'selectslot', index
        items = []
        indexes = []
        for i in xrange(5):
            item = self.mainInventory.GetItemStack(i, 0)
            if(item not in items):
                items.append(item)
                indexes.append(i)
        
        if(len(items) >= index):
            index -= 1
            if(items[index] != self.lastItem):
                self.selectedIndex = indexes[index]
                self.lastItem = items[index]
                SelectedItemChangeEvent(self.mainInventory, self.lastItem).Fire()
                self.UpdateSelectionBox()            
            
    def OnInventoryChange(self, event):
        inventory = event.GetInventory()
        if(isinstance(inventory, MainInventory)):
            self.UpdateIcons(inventory)
        
    def Destroy(self):
        print 'destroy hudhotbar'
        for item in self.currentItems:
            item.DestroyHotbarIcon()
        self.selectionBox.Destroy()
        del self.selectionBox
        self.inventoryBackground.destroy()
        self.hbNode.removeNode()
        del self.hbNode
        self.ignoreAll()
        