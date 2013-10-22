
from item.Tool import Tool
from item.ItemId import ItemId

class Pickaxe(Tool):
    
    def __init__(self):
        Tool.__init__(self)
        self.itemId = ItemId.Pickaxe
        self.invWidth = 1
        self.invHeight = 1
        self.modelName = 'Pickaxe'
        self.model = None
        self.dequipTime = 0.5
        self.equipTime = 0.5
        
        self.LoadContent()
        