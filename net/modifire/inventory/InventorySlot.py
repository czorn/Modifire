

class InventorySlot():
    
    def __init__(self, x, y):
        self.itemStack = None
        self.x = x
        self.y = y
        self.inventorySlotButton = None
        
    def GetItemStack(self):
        return self.itemStack
    
    def SetItemStack(self, value):
        self.itemStack = value
        
    def RemoveItemStack(self, destroy = False):
        if(destroy):
            self.itemStack.Destroy()
        #del self.itemStack
        self.SetItemStack(None)
        
    def SetInventorySlotButton(self, value):
        self.inventorySlotButton = value
        
    def GetInventorySlotButton(self):
        return self.inventorySlotButton