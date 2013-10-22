
from direct.showbase.DirectObject import DirectObject

from gui.GUIOrder import GUIOrder

class Menu(DirectObject):
    
    def __init__(self):
        self.node = aspect2d.attachNewNode('Menu')
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.MENU])
        self.node.hide()
        
    def Update(self):
        pass
    
    def Hide(self):
        self.node.hide()   
        
    def Show(self):
        self.node.show()     
        
    def Destroy(self):
        self.node.removeNode()