
from item.ItemId import ItemId
from item.Item import Item

class LowMetal(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.itemId = ItemId.LowMetal
        self.invWidth = 1
        self.invHeight = 1
        self.modelName = 'LowMetal'
        self.dequipTime = 0.5
        self.equipTime = 0.5
        
        self.LoadContent()
        
    def GetPossibleItems(self):
        from item.MidMetal import MidMetal
        
        return [MidMetal]
    
    def GetRecipe(self):        
        return []