
from direct.actor.Actor import Actor
from pandac.PandaModules import AudioSound
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Func, Wait
from panda3d.core import Vec3

import Settings
import Globals
import GameTime
from item.Weapon import Weapon
from event.InventoryEvent import AmmoChangeEvent
from event.CameraEvent import ADSEvent
from event.HUDEvent import CrossHairEvent

class Firearm(Weapon):
    
    (FM_BOLT,
     FM_SEMI,
     FM_BURST,
     FM_AUTO) = range(4)
    
    def __init__(self):
        Weapon.__init__(self)
        self.baseWeapon = None  # The base weapon required to make this weapon
        self.fireMode = None    # The firing mode of the weapon
        self.ammoLeft = 0       # int - The total number of bullets left to use
        self.currentClip = 0    # int - The number of bullets in the current magazine
        self.maxAmmo = 0        # int - The maximum number of bullets
        self.clipSize = 0       # int - The maximum number of bullets in the magazine
        self.reloadTime = 0     # float - Half of how long it takes to reload
        self.recoil = 0         # float - The amount (in degrees) the player view moves vertical after firing
        self.bulletSpread = 0   # float - The radius of the circle at the end of the cone that represent where bullets can be fired
        self.reloadSeq = Sequence()
        self.fireSound = None
        self.fireSound2 = None
        self.fireSound3 = None
        self.reloadSound = None
        self.adsPos = Vec3(0, 0, 0)
        self.isADS = 0
        self.adsDelay = 0.3
        self.lastADSTime = 0
        self.adsFOV = 65
        self.isReloading = False
        self.hasAnim = False
        self.crossHairFilename = 'Normal'
        self.adsMouseSpeedModifire = 0.55
        self.reloadInterrupted = False
        
    def LoadContent(self):
        if(self.model is None):
            print 'LOADED THAT MODEL FIREARM THING', self.modelName
            self.model = Actor('Assets/Models/Items/%s' % (self.modelName),
                                {'fire': 'Assets/Models/Items/%s-fire' % (self.modelName)
                                 #'reload': '../ext/models/weapons/mp5-reload',
                                 #'idle': '../ext/models/weapons/mp5-idle'
                                 })
            self.model.setPos(self.hiddenPos)
            return True
        return False
    
    def ToggleADS(self, force = False):
        if(force or (GameTime.time - self.lastADSTime > self.adsDelay and self.isReady and not self.isReloading)):
            self.lastADSTime = GameTime.time
            self.isADS = (self.isADS + 1) % 2
            if(self.model is not None):
                if(self.isADS):
                    Sequence(LerpPosInterval(self.model, self.adsDelay, self.adsPos),
                             Func(self.OnIntoAdsSeqComplete)).start()
                    # THIS IS A BAD PLACE FOR THIS
                else:
                    Sequence(Func(self.OnOutOfAdsSeqStart),
                             LerpPosInterval(self.model, self.adsDelay, self.equippedPos)).start()
                    # THIS IS A BAD PLACE FOR THIS
                
                # Fire event for ADS change. Camera listens for this and zooms in / out
                # and sets sensitivity of mouse
                ADSEvent(self.isADS, self.adsDelay, self.adsFOV, self.adsMouseSpeedModifire).Fire()
                
    def OnIntoAdsSeqComplete(self):
        CrossHairEvent(self.crossHairFilename, False).Fire()
    
    def OnOutOfAdsSeqStart(self):
        CrossHairEvent(self.crossHairFilename, True).Fire()
        
    def CanUse(self):
        return Weapon.CanUse(self) and self.currentClip > 0
        
    def GetFireMode(self):
        return self.fireMode
    
    def GetBaseWeapon(self):
        return self.baseWeapon
    
    def RefillAmmo(self):
        self.currentClip = self.clipSize
        self.ammoLeft = self.maxAmmo
    
    def Use(self):
        Weapon.Use(self)
        self.currentClip -= 1
        
        if(not Settings.IS_SERVER):
            if(self.model and self.hasAnim):
                self.model.play('fire')
                
            if(self.fireSound.status() != AudioSound.PLAYING):
                print '1'
                self.fireSound.play()
            elif(self.fireSound2.status() != AudioSound.PLAYING or not self.fireSound3):
                print '2'
                self.fireSound2.play()
            elif(self.fireSound3):
                print '3'
                self.fireSound3.play()
            
            if(self.playerId == Globals.MY_PID):
                AmmoChangeEvent(None, self).Fire()            
            
    def Reload(self):
        if(self.reloadSeq.isPlaying() or self.equipSeq.isPlaying() or self.dequipSeq.isPlaying()):
            return
        
        print 'PLAYER RELOAD'
        
        diff = self.clipSize - self.currentClip
        if(diff > 0 and self.ammoLeft > 0):
            if(not Settings.IS_SERVER):
                self.reloadSeq = Sequence(Func(self.SetIsReady, False),
                                        LerpPosInterval(self.model, self.dequipTime, self.hiddenPos, self.equippedPos),
                                        Func(self.PlayReloadSound),
                                        Wait(self.reloadTime),
                                        LerpPosInterval(self.model, self.equipTime, self.equippedPos, self.hiddenPos),
                                        Func(self.SetIsReady, True),
                                        Func(self.FinishReloading, diff))
            else:
                self.reloadSeq = Sequence(Func(self.SetIsReady, False),
                                         Wait(self.dequipTime),
                                         Wait(self.reloadTime),
                                         Wait(self.equipTime),
                                         Func(self.SetIsReady, True),
                                         Func(self.FinishReloading, diff))
            self.reloadSeq.start()
            self.isReloading = True
            if(self.isADS):
                self.ToggleADS(True)
                
    def IsADS(self):
        return self.isADS
                
    def Dequip(self):
        Weapon.Dequip(self)
        if(self.isADS):
                self.ToggleADS(True)
        if(self.isReloading):
            self.reloadInterrupted = True
            self.isReloading = False
            self.reloadSeq.finish()
#            
    def PlayReloadSound(self):
        self.reloadSound.play()
            
    def FinishReloading(self, diff):
        if(self.reloadInterrupted):
            self.reloadInterrupted = False
            return
        
        if(self.ammoLeft >= diff):
                    self.currentClip += diff
                    self.ammoLeft -= diff
        else:
            self.currentClip += self.ammoLeft
            self.ammoLeft = 0
            
        self.isReloading = False
        
        if(not Settings.IS_SERVER):
            AmmoChangeEvent(None, self).Fire()
            
    def GetCurrentClipAmmo(self):
        return self.currentClip
    
    def GetTotalRemainingAmmo(self):
        return self.ammoLeft
          
    def ReparentTo(self, node):
        Weapon.ReparentTo(self, node)
        if(not Settings.IS_SERVER):
            Globals.AUDIO_3D.attachSoundToObject(self.fireSound, node)
            Globals.AUDIO_3D.attachSoundToObject(self.fireSound2, node)
            Globals.AUDIO_3D.attachSoundToObject(self.reloadSound, node)
    
          
            
            
        