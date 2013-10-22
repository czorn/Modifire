
import Globals

from item.SMGAuto import SMGAuto
from item.Builder import Builder
from item.ItemStack import ItemStack
from inventory.InventorySlot import InventorySlot
from event.InventoryEvent import InventoryChangeEvent

class Inventory():
    
    def __init__(self, width, height):
        self.width = width      # How many slots wide is the region
        self.height = height    # How many slots tall is the region
        self.dirty = True      # Whether this inventory has changed since last update
        
        # Initialize the slots
        self.invSlots = []
        for x in xrange(self.width):
            col = []
            for y in xrange(self.height):
                col.append(InventorySlot(x, y))
            self.invSlots.append(col)
            
    # Adds an itemStack to the next free slot if possible
    def AddItemStack(self, itemStack):
        for y in xrange(self.height):
            for x in xrange(self.width):
                if(self.PlaceItemStack(itemStack, x, y)):
                    return True
        return False 
    
    # Attempts to place the item in the inventory at the specified position
    # If the position is occupied, or the item
    # requires more space than is available, False
    # will be returned and the item will not be placed
    def PlaceItemStack(self, itemStack, x, y):
        item = itemStack.GetItem()
        if(self.invSlots[x][y].GetItemStack() is None):
            for i in xrange(item.GetItemWidth()):
                for j in xrange(item.GetItemHeight()):
                    if(x + i > self.width - 1 or y + j > self.height - 1):
                        return False
                    if(self.invSlots[x + i][y + j].GetItemStack()):
                        return False
            
            itemStack.ClearParentSlots()
            for i in xrange(item.GetItemWidth()):
                for j in xrange(item.GetItemHeight()):
                    self.invSlots[x + i][y + j].SetItemStack(itemStack)
                    itemStack.AddParentSlot(self.invSlots[x + i][y + j])
            
            self.SetDirty(True)
            InventoryChangeEvent(self).Fire()
            return True
        return False
    
    def RemoveItemStack(self, x, y, destroy = False):
        itemStack = self.GetItemStack(x, y)
        if(itemStack is not None):
            for inventorySlot in itemStack.GetParentSlots():
                inventorySlot.RemoveItemStack(destroy)
            itemStack.ClearParentSlots()
            self.SetDirty(True)
            InventoryChangeEvent(self).Fire()
    
    def GetItemStack(self, x, y):
        return self.invSlots[x][y].GetItemStack()
    
    def GetItemStacks(self):
        itemStacks = []
        for x in xrange(self.width):
            for y in xrange(self.height):
                itemStack = self.GetItemStack(x, y)
                if(itemStack and itemStack not in itemStacks):
                    itemStacks.append(itemStack)
        return itemStacks
    
    def Clear(self):
        for x in xrange(self.width):
            for y in xrange(self.height):
                print 'removing itemstack'
                self.RemoveItemStack(x, y, True) 
    
    def GetInventorySlots(self):
        return self.invSlots
    
    def GetIndices(self, itemStack):
        for x in xrange(self.width):
            for y in xrange(self.height):
                if(self.GetItemStack(x, y) == itemStack):
                    return [x, y]
        return None
    
    def IsEmpty(self):
        return len(self.GetItemStacks()) == 0
    
    def SetDirty(self, value):
        self.dirty = value
        
    def IsDirty(self):
        return self.dirty
    
    def Destroy(self):
        for itemStack in self.GetItemStacks():
            itemStack.Destroy()
        
    def AddCustomItem(self, item):
        item.playerId = Globals.MY_PID
        self.AddItemStack(ItemStack(item))
        
        