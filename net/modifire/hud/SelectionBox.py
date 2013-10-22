from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from direct.showbase.DirectObject import DirectObject

import Settings
import Globals

class SelectionBox():
    
    def __init__(self, parent):
        self.currentSelectionBox = 0
        self.LoadContent(parent)
        
    def LoadContent(self, parent):        
        self.selectionBoxSmall = self.LoadImage('SelectionBoxSmall.png', parent)
        self.selectionBoxMed = self.LoadImage('SelectionBoxMed.png', parent)
        self.selectionBoxLarge = self.LoadImage('SelectionBoxLarge.png', parent)
        
    def LoadImage(self, filename, parent):
        myImage = OnscreenImage(image = 'Assets/Images/HUD/%s' % (filename))
        myImage.setTransparency(TransparencyAttrib.MAlpha)
        myImage.reparentTo(parent)
        myImage.setScale((myImage.getTexture().getOrigFileXSize() / 1024.0, 1, myImage.getTexture().getOrigFileYSize() / 1024.0))
        myImage.hide()
        return myImage
        
    def Update(self, itemStack, index):        
        if(self.currentSelectionBox):
            self.currentSelectionBox.hide()
            
        if(itemStack):
            item = itemStack.GetItem()
            itemWidth = item.GetItemWidth()
            if(itemWidth == 2):
                self.currentSelectionBox = self.selectionBoxMed
            elif(itemWidth == 3):
                self.currentSelectionBox = self.selectionBoxLarge
            else:
                self.currentSelectionBox = self.selectionBoxSmall
                
            coords = Globals.ConvertFromImageAbsoluteToAspect2D(374 + 69 * index + (itemWidth-1) * 69.0/2, 977, 1024)
        else:
            self.currentSelectionBox = self.selectionBoxSmall
            coords = Globals.ConvertFromImageAbsoluteToAspect2D(374 + 69 * index, 977, 1024)
            
        self.currentSelectionBox.show()
        
        
        self.currentSelectionBox.setPos(coords[0], 0, coords[1])
        
    def Destroy(self):
        self.selectionBoxSmall.destroy()
        self.selectionBoxMed.destroy()
        self.selectionBoxLarge.destroy()
        