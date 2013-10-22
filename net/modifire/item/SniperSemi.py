
from item.Firearm import Firearm
from item.SniperBase import SniperBase
from item.ItemId import ItemId

class SniperSemi(Firearm):
    
    def __init__(self):
        Firearm.__init__(self)
        self.itemId = ItemId.SniperSemi
        self.baseWeapon = SniperBase
        self.fireMode = Firearm.FM_SEMI
        self.invWidth = 3
        self.invHeight = 1
        self.dequipTime = 0.5
        self.equipTime = 0.5
        self.modelName = 'SniperSemi'
        self.damage = 35
        self.attackDelay = 0.5
        self.maxAmmo = 60
        self.ammoLeft = 60
        self.reloadTime = 0.5
        self.recoil = 0.1
        self.bulletSpread = 0