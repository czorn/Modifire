
from item.Item import Item

class Tool(Item):
    
    def __init__(self):
        Item.__init__(self)
        
    def LoadContent(self):
        return Item.LoadContent(self)