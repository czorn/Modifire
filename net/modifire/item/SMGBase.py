
from item.Item import Item
from item.Firearm import Firearm
from item.ItemId import ItemId

class SMGBase(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.itemId = ItemId.SMGBase
        self.invWidth = 2
        self.invHeight = 1
        self.modelName = 'SMGBase'
        self.dequipTime = 0.5
        self.equipTime = 0.5
        self.componentOf = []   # A list of the items this item can create
        self.recipe = []        # A list of the components required to make this item
        
        self.LoadContent()
        
    def GetWeapon(self, fm):
        from item.SMGAuto import SMGAuto
        
        weapons = {Firearm.FM_BOLT : None,
                   Firearm.FM_SEMI : None,
                   Firearm.FM_BURST : None,
                   Firearm.FM_AUTO : SMGAuto}
        return weapons[fm]
    
    def GetPossibleItems(self):
        from item.SMGAuto import SMGAuto
        
        return [SMGAuto]
    
    def GetRecipe(self):
        from item.MidMetal import MidMetal
        
        return [MidMetal]
        