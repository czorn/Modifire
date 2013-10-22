from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TransparencyAttrib
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectEntry

"""
egg-texture-cards -o Button_Okay.egg -p 200,60 okay.png okay_over.png
egg-texture-cards -o Button_Cancel.egg -p 200,60 cancel.png cancel_over.png

"""

class AlertPopup(DirectObject):
    
    def __init__(self, title, message, okayFunction, cancelFunction):
        self.okayFunction = okayFunction
        self.cancelFunction = cancelFunction
        self.node = aspect2d.attachNewNode('alertPopup')
        self.frame = DirectFrame()
        self.LoadContent(title, message)
        self.frame.reparentTo(self.node)
        
    def LoadContent(self, title, message):
        bg = OnscreenImage(image = 'Assets/Images/Inventory/BlackScreen.png', scale = (2, 1, 1))
        bg.setTransparency(TransparencyAttrib.MAlpha)
        bg.reparentTo(self.node)
        
        popup = OnscreenImage(image = 'Assets/Images/Menus/Popups/popup.png')
        popup.setTransparency(TransparencyAttrib.MAlpha)
        popup.reparentTo(self.node)
        
        titleText = OnscreenText(text = title, pos = (-0.29, 0.51), scale = 0.07, fg = (1, 1, 1, 1))
        titleText.reparentTo(self.node)
        
        self.LoadButton('Button_Okay', 'okay', 'okay_over', -0.27, -0.13, self.OnButtonClicked, ['okay'])
        self.LoadButton('Button_Cancel', 'cancel', 'cancel_over', 0.27, -0.13, self.OnButtonClicked, ['cancel'])
        
        messageText = OnscreenText(text = message, pos = (0, 0.2), scale = 0.07, fg = (1, 1, 1, 1))
        messageText.reparentTo(self.node)
        
    def LoadButton(self, egg, up, over, x, y, cmd, args):
        maps = loader.loadModel("Assets/Images/Menus/Popups/%s" % (egg))
        b = DirectButton(geom = (maps.find('**/%s' % (up)),
                         maps.find('**/%s' % (over)),
                         maps.find('**/%s' % (over)),
                         maps.find('**/%s' % (up))),
                         command = cmd,
                         extraArgs = args,
                         pressEffect = 0,
                         relief = None,
                         rolloverSound = None, 
                         clickSound = None,
                         pos = (x, 1, y),
                         scale = (0.5, 1, 60.0/400.0))
        b.reparentTo(self.frame)
        
    def Destroy(self):
        self.frame.destroy()
        self.node.removeNode()
        
    def OnButtonClicked(self, buttonText):
        if(buttonText == 'okay'):
            self.okayFunction(self)
        elif(buttonText == 'cancel'):
            self.cancelFunction(self)
            
            