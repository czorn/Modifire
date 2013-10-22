
from item.Item import Item
from item.Firearm import Firearm
from item.ItemId import ItemId

class RifleBase(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.itemId = ItemId.RifleBase
        self.invWidth = 2
        self.invHeight = 1
        self.modelName = 'RifleBase'
        self.dequipTime = 0.5
        self.equipTime = 0.5
        
        self.LoadContent()
        
    def GetWeapon(self, fm):
        from item.RifleSemi import RifleSemi
        from item.RifleBurst import RifleBurst
        from item.RifleAuto import RifleAuto

        weapons = {Firearm.FM_BOLT : None,
                   Firearm.FM_SEMI : RifleSemi,
                   Firearm.FM_BURST : RifleBurst,
                   Firearm.FM_AUTO : RifleAuto}
        return weapons[fm]
    
    def GetPossibleItems(self):
        from item.RifleAuto import RifleAuto
        from item.RifleSemi import RifleSemi
        from item.RifleBurst import RifleBurst
        
        return [RifleSemi, RifleBurst, RifleAuto]
    
    def GetRecipe(self):
        from item.MidMetal import MidMetal
        
        return [MidMetal, MidMetal]