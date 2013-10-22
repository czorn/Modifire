

class ItemStack():
    
    def __init__(self, item = None, numItems = 1):
        self.item = item
        self.numItems = numItems
        self.maxItems = 64
        self.parentSlots = []
        
    def GetItem(self):
        return self.item
    
    def GetParentSlots(self):
        return self.parentSlots
    
    def AddParentSlot(self, parentSlot):
        self.parentSlots.append(parentSlot)
    
    def ClearParentSlots(self):
        self.parentSlots = []
        
    def Destroy(self):
        if(self.item):
            self.item.Destroy()