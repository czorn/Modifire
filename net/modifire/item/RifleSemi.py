
from item.Firearm import Firearm
from item.RifleBase import RifleBase
from item.ItemId import ItemId

class RifleSemi(Firearm):
    
    def __init__(self):
        Firearm.__init__(self)
        self.itemId = ItemId.RifleSemi
        self.baseWeapon = RifleBase
        self.fireMode = Firearm.FM_SEMI
        self.invWidth = 2
        self.invHeight = 1
        self.dequipTime = 0.5
        self.equipTime = 0.5
        self.modelName = 'RifleSemi'
        self.damage = 30
        self.attackDelay = 0.3 
        self.maxAmmo = 60
        self.ammoLeft = 60
        self.reloadTime = 0.5
        self.recoil = 0.1
        self.bulletSpread = 0
        
    def GetRecipe(self):        
        return [RifleBase]