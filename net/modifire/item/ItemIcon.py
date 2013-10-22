
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib


class ItemIcon():
    
    def __init__(self, itemName, parentNode):
        print 'itemicon', itemName, parentNode
        self.parentNode = parentNode    # The node of its parent (e.g. the inventory)
        self.itemName = itemName        # The filename of the icon
        self.image = None               # The actual icon
        #self.iconNode = aspect2d.attachNewNode('iconnode')
        
        self.LoadContent()
        
    def LoadContent(self):
        self.itemImage = OnscreenImage(image = "Assets/Images/Items/%s.png" % (self.itemName))
        self.itemImage.setScale((self.itemImage.getTexture().getOrigFileXSize() / 1024.0, 1, self.itemImage.getTexture().getOrigFileYSize() / 1024.0))
        self.itemImage.setTransparency(TransparencyAttrib.MAlpha)
        self.itemImage.reparentTo(self.parentNode)
        
    def setBin(self, binType, value):
        print 'set bin', binType, value
        self.itemImage.setBin(binType, value)
        
    def SetPos(self, pos):
        self.itemImage.setPos(pos)
        
    def Destroy(self):
        self.itemImage.destroy()