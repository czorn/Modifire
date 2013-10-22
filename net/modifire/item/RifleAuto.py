
from panda3d.core import Vec3 #@UnresolvedImport

import Settings
import Globals

from item.Firearm import Firearm
from item.RifleBase import RifleBase
from item.ItemId import ItemId

class RifleAuto(Firearm):
    
    def __init__(self):
        Firearm.__init__(self)
        self.itemId = ItemId.RifleAuto
        self.baseWeapon = RifleBase
        self.fireMode = Firearm.FM_AUTO
        self.invWidth = 2
        self.invHeight = 1
        self.dequipTime = 0.5
        self.equipTime = 0.5
        self.modelName = 'RifleAuto'
        self.damage = 20
        self.useDelay = 0.1
        self.maxAmmo = 120
        self.clipSize = 30
        self.ammoLeft = self.maxAmmo
        self.currentClip = self.clipSize
        self.reloadTime = 2.0
        self.recoil = 0.4
        self.hiddenPos = Vec3(0.3, 0.35, -0.7)
        self.equippedPos = Vec3(0.3, 0.4, -0.1)
        self.adsPos = Vec3(0, 0.1, 0)
        self.adsDelay = 0.25
        self.name = 'M4A1'
        
        
        if(not Settings.IS_SERVER):
            self.fireSound = Globals.AUDIO_3D.loadSfx('Assets/Sounds/RifleAutoFire.mp3')
            self.fireSound2 = Globals.AUDIO_3D.loadSfx('Assets/Sounds/RifleAutoFire.mp3')
            self.fireSound3 = Globals.AUDIO_3D.loadSfx('Assets/Sounds/RifleAutoFire.mp3')
            self.reloadSound = Globals.AUDIO_3D.loadSfx('Assets/Sounds/reloadMed.mp3')
            print 'Loaded Assets/Sounds/RifleAutoFire.mp3'
            print 'Loaded Assets/Sounds/reloadMed.mp3'
        
    def LoadContent(self):
        if(Firearm.LoadContent(self)):
            self.model.setScale(0.035)
            self.model.setH(180)
            self.model.setLightOff()
            return True
        return False
        
    def GetRecipe(self):        
        return [RifleBase]