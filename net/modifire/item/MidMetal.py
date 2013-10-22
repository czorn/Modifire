
from item.ItemId import ItemId
from item.Item import Item

class MidMetal(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.itemId = ItemId.MidMetal
        self.invWidth = 1
        self.invHeight = 1
        self.modelName = 'MidMetal'
        self.dequipTime = 0.5
        self.equipTime = 0.5
        
        self.LoadContent()
        
    def GetPossibleItems(self):
        from item.SMGBase import SMGBase
        from item.RifleBase import RifleBase
        from item.SniperBase import SniperBase
        
        return [RifleBase, SMGBase, SniperBase]
    
    def GetRecipe(self):
        from item.LowMetal import LowMetal
        
        return [LowMetal, LowMetal]
        