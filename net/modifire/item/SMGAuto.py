
from panda3d.core import Vec3 #@UnresolvedImport

from item.ItemId import ItemId
from item.Firearm import Firearm
from item.SMGBase import SMGBase

import Settings
import Globals

class SMGAuto(Firearm):
    
    def __init__(self):
        Firearm.__init__(self)
        self.itemId = ItemId.SMGAuto 
        self.baseWeapon = SMGBase
        self.fireMode = Firearm.FM_AUTO
        self.invWidth = 2
        self.invHeight = 1
        self.dequipTime = 0.3
        self.equipTime = 0.3
        self.modelName = 'SMGAuto'
        self.damage = 10
        self.useDelay = 0.085
        self.maxAmmo = 90
        self.clipSize = 25
        self.ammoLeft = self.maxAmmo
        self.currentClip = self.clipSize
        self.reloadTime = 1.1
        self.recoil = 0.7
        self.hiddenPos = Vec3(0.3, 0.35, -0.7)
        self.equippedPos = Vec3(0.3, 0.35, -0.1)
        self.adsPos = Vec3(0, 0.05, 0)
        self.adsDelay = 0.2
        self.name = 'MP5'
        self.hasAnim = True
        
        if(not Settings.IS_SERVER):
            self.fireSound = Globals.AUDIO_3D.loadSfx('Assets/Sounds/mp5Fire.mp3')
            self.fireSound2 = Globals.AUDIO_3D.loadSfx('Assets/Sounds/mp5Fire.mp3')
            self.reloadSound = Globals.AUDIO_3D.loadSfx('Assets/Sounds/reloadMed.mp3')
            print 'Loaded Assets/Sounds/mp5Fire.mp3'
            print 'Loaded Assets/Sounds/reloadMed.mp3'
        
    def LoadContent(self):
        if(Firearm.LoadContent(self)):
            self.model.setScale(0.3)
            self.model.setLightOff()
            return True
        return False
    
    def GetRecipe(self):
        from item.SMGBase import SMGBase
        return [SMGBase]