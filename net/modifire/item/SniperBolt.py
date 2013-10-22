
from panda3d.core import Vec3 #@UnresolvedImport

from item.Firearm import Firearm
from item.SniperBase import SniperBase
from item.ItemId import ItemId
from event.HUDEvent import CrossHairEvent

import Settings
import Globals

class SniperBolt(Firearm):
    
    def __init__(self):        
        Firearm.__init__(self)
        self.itemId = ItemId.SniperBolt 
        self.baseWeapon = SniperBase
        self.fireMode = Firearm.FM_BOLT
        self.invWidth = 3
        self.invHeight = 1
        self.dequipTime = 0.6
        self.equipTime = 0.6
        self.modelName = 'SniperBolt'
        self.damage = 80
        self.useDelay = 2.0
        self.maxAmmo = 40
        self.clipSize = 6
        self.ammoLeft = self.maxAmmo
        self.currentClip = self.clipSize
        self.reloadTime = 2.5
        self.recoil = 4.0
        self.hiddenPos = Vec3(0.3, 0.35, -0.7)
        self.equippedPos = Vec3(0.3, 0.35, -0.1)
        self.adsPos = Vec3(0, 0.15, 0)
        self.adsDelay = 0.3
        self.name = 'L515'
        self.hasAnim = False
        self.adsFOV = 25
        self.adsMouseSpeedModifire = 0.25
        self.sniperCrossHairFilename = 'SniperBolt'
        
        if(not Settings.IS_SERVER):
            self.fireSound = Globals.AUDIO_3D.loadSfx('Assets/Sounds/SniperBoltFire.mp3')
            self.fireSound2 = Globals.AUDIO_3D.loadSfx('Assets/Sounds/SniperBoltFire.mp3')
            self.reloadSound = Globals.AUDIO_3D.loadSfx('Assets/Sounds/reloadLong.mp3')
            print 'Loaded Assets/Sounds/SniperBoltFire.mp3'
            print 'Loaded Assets/Sounds/reloadLong.mp3'
        
    def LoadContent(self):
        if(Firearm.LoadContent(self)):
            self.model.setScale(1.1)
#            self.model.setLightOff()
            return True
        return False
    
    def Use(self):
        Firearm.Use(self)
#        if(self.isADS):
#            self.ToggleADS(True)
    
    def OnIntoAdsSeqComplete(self):
        self.model.hide()
        CrossHairEvent(self.crossHairFilename, False).Fire()
        CrossHairEvent(self.sniperCrossHairFilename, True).Fire()
        
    def OnOutOfAdsSeqStart(self):
        self.model.show()
        CrossHairEvent(self.sniperCrossHairFilename, False).Fire()
        CrossHairEvent(self.crossHairFilename, True).Fire()
    
    def GetRecipe(self):
        from item.SniperBase import SniperBase
        return [SniperBase]