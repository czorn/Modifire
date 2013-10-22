
from item.Item import Item
import GameTime

class Weapon(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.damage = 0     # How much damage the weapon causes to other players
        
    def GetDamage(self):
        return self.damage
    
    