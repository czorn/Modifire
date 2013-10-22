
from panda3d.core import Vec3, Point2 #@UnresolvedImport
from pandac.PandaModules import TextureStage, CardMaker

from item.Tool import Tool
from item.ItemId import ItemId
from item.ItemStack import ItemStack
from environment.BlockGeometryGenerator import BlockGeometryGenerator
from event.InventoryEvent import SelectedItemAttributeChangeEvent

class Builder(Tool):
    
    def __init__(self):
        Tool.__init__(self)
        self.itemId = ItemId.Builder
        self.invWidth = 1
        self.invHeight = 1
        self.modelName = 'Builder'
        self.model = None
        self.useDelay = 0.2
        self.dequipTime = 0.3
        self.equipTime = 0.3
        self.hiddenPos = Vec3(0.17, 0.5, -0.7)   # The location of the item when it's unequipped
        self.equippedPos = Vec3(0.17, 0.5, -0.2) # The location of the item when it's equipped
        
        self.currentBlockIdToPlace = 0
        self.maxBlocks = 18
        self.blockTexture = None
        
    def LoadContent(self):
        if(Tool.LoadContent(self)):
            self.model.setScale(0.09)
            self.model.setLightOff()
            self.blockTexture = loader.loadTexture('Assets/Images/Textures/blocks.png')
            print 'Loaded Assets/Images/Textures/blocks.png'
            self.UpdateTexture()
            return True
        return False
    
    def UpdateTexture(self):
        if(not self.model):
            self.LoadContent()
            
        (u, v) = BlockGeometryGenerator.BlockIdToUV(self.currentBlockIdToPlace + 1) # Add 1 to offset from Air Id = 0
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MReplace)
        self.model.clearTexture()
        self.model.setTexture(ts, self.blockTexture)
        self.model.setTexOffset(ts, u[0], v[0])
        self.model.setTexScale(ts, 0.0625, 0.0625)
    
    def OnBlockChange(self):
        self.UpdateTexture()
        
        print 'sent block change'
        SelectedItemAttributeChangeEvent(None, ItemStack(self)).Fire()
        
    def IncreaseBlock(self):
        self.currentBlockIdToPlace = ((self.currentBlockIdToPlace  + 1) % self.maxBlocks)
        self.OnBlockChange()
        
    def DecreaseBlock(self):
        self.currentBlockIdToPlace = ((self.currentBlockIdToPlace  + self.maxBlocks - 1) % self.maxBlocks)
        self.OnBlockChange()
        
    def GetBlockId(self):
        return self.currentBlockIdToPlace + 1 # Add 1 to offset from Air Id = 0
    
    def SetBlockId(self, value):
        self.currentBlockIdToPlace = value - 1
        
    def GetItemData(self):
        return [self.GetBlockId()]
        
        