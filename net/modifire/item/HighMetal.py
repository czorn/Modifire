
from item.ItemId import ItemId
from item.Item import Item

class HighMetal(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.itemId = ItemId.HighMetal
        self.invWidth = 1
        self.invHeight = 1
        self.modelName = 'HighMetal'
        self.dequipTime = 0.5
        self.equipTime = 0.5
        
        self.LoadContent()
        
    def GetPossibleItems(self):        
        return []
    
    def GetRecipe(self):
        from item.MidMetal import MidMetal
        
        return [MidMetal, MidMetal]