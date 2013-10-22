
from item.Item import Item
from item.ItemId import ItemId
from item.Firearm import Firearm


class SniperBase(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.itemId = ItemId.SniperBase
        self.invWidth = 3
        self.invHeight = 1
        self.modelName = 'SniperBase'
        self.dequipTime = 0.5
        self.equipTime = 0.5
        
        self.LoadContent()
        
    def GetWeapon(self, fm):
        from item.SniperBolt import SniperBolt
        from item.SniperSemi import SniperSemi
        
        weapons = {Firearm.FM_BOLT : SniperBolt,
                   Firearm.FM_SEMI : SniperSemi,
                   Firearm.FM_BURST : None,
                   Firearm.FM_AUTO : None}
        return weapons[fm]
    
    def GetPossibleItems(self):
        from item.SniperBolt import SniperBolt
        from item.SniperSemi import SniperSemi
        
        return [SniperBolt, SniperSemi]
    
    def GetRecipe(self):
        from item.MidMetal import MidMetal
        from item.LowMetal import LowMetal
        
        return [MidMetal, LowMetal]