

from inventory.Inventory import Inventory 

class MainInventory(Inventory):
    
    def __init__(self):
        Inventory.__init__(self, 5, 4)