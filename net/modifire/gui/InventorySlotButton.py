from direct.gui.DirectGui import DirectButton

import Globals

#egg-texture-cards -o inventorySlot.egg -p 64,64 inventorySlot-up.png inventorySlot-over.png

class InventorySlotButton():
    
    def __init__(self, slotIndexX, slotIndexY, xCoord, yCoord, padding, x, y, inventorySlot, parentInventory, onClickFunction):
        self.xIndex = slotIndexX                    # The x index of the button in the inventory
        self.yIndex = slotIndexY                    # The y index of the button in the inventory
        self.button = None                          # The DirectButton
        self.inventorySlot = inventorySlot          # The slot this button represents
        self.parentInventory = parentInventory      # The region this slot belongs to
        
        self.LoadContent(x, y, xCoord, yCoord, padding, onClickFunction)
        
    def LoadContent(self, x, y, xCoord, yCoord, padding, onClickFunction):
        egg = 'inventorySlot'
        up = ''.join([egg, '-up'])
        over = ''.join([egg, '-over'])
        maps = loader.loadModel("Assets/Images/Inventory/%s" % ('inventorySlot'))
        self.button = DirectButton(geom = (maps.find('**/%s' % (up)),
                         maps.find('**/%s' % (over)),
                         maps.find('**/%s' % (over)),
                         maps.find('**/%s' % (up))),
                         command = onClickFunction,
                         extraArgs = [self],
                         pressEffect = 0,
                         relief = None,
                         rolloverSound = None, 
                         clickSound = None,
                         scale = (128.0/1024.0, 1, 128.0/1024.0))
        
        pos = Globals.ConvertFromImageAbsoluteToAspect2D(xCoord + x * padding, yCoord + y * padding, 1024)
        self.button.setPos(pos[0], 0, pos[1])
        
    def ReparentTo(self, node):
        self.button.reparentTo(node)
        
    def GetPos(self):
        return self.button.getPos()
    
    def GetParentInventory(self):
        return self.parentInventory
    
    def GetInventorySlot(self):
        return self.inventorySlot
    
    def GetSlotIndices(self):
        return [self.xIndex, self.yIndex]
    