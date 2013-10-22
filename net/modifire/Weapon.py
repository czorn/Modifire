


class Weapon():
    
    def __init__(self):
        self.damage = 0         # How much damage it deals
        self.fireRate = 0       # How many bullets you can fire per second
        self.ammo = 0           # Total amount of ammo
        self.magSize = 0        # Max amount of ammo in clip
        self.activeAmmoCount    # Amount of ammo left in current clip
        self.recoil             # How many degress up does the gun recoil after firing
        self.fireMode           # e.g. Auto, Semi, Burst, Bolt
        
        # Sounds
        self.SfxReload = 0
        self.SfxFire = 0
        self.SfxOutOfAmmo == 0
        
        # Attachments
        self.AttachmentTop = 0
        self.AttachmentBot = 0
        self.AttachmentMag = 0
        self.AttachmentFront = 0