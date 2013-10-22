from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TransparencyAttrib, TextNode
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectEntry

"""
egg-texture-cards -o Button_Okay.egg -p 200,60 okay.png okay_over.png
egg-texture-cards -o Button_Cancel.egg -p 200,60 cancel.png cancel_over.png

"""

class Popup(DirectObject):
    
    def __init__(self, title, fields, initialValues, okayFunction, cancelFunction):
        self.okayFunction = okayFunction
        self.cancelFunction = cancelFunction
        self.node = aspect2d.attachNewNode('popup')
        self.frame = DirectFrame()
        self.fields = {}
        self.LoadContent(title, fields, initialValues)
        self.frame.reparentTo(self.node)
        
    def LoadContent(self, title, fields, initialValues):
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
        
        y = 0
        for i in xrange(len(fields)):
            self.fields[fields[i]] = self.CreateField(fields[i], initialValues[i], y, y)
            y += 1
        
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
        
    def CreateField(self, fieldLabel, initText, yIndex, focus):
        label = OnscreenText(text = fieldLabel, pos = (-0.4, 0.35 - yIndex * 0.2), scale = 0.07, fg = (1, 1, 1, 1), align = TextNode.ALeft)
        label.reparentTo(self.node)
        f = DirectEntry(text = '' ,
                        scale = 0.05,
                        initialText = initText, 
                        numLines = 1,
                        rolloverSound = None,
                        clickSound = None,
                        pos = (-0.4, 1, 0.25 - yIndex * 0.2),
                        focus = (not focus))
        f.reparentTo(self.frame)
        return f
    
    def GetValue(self, key):
        return self.fields[key].get()
        
    def Destroy(self):
        self.frame.destroy()
        self.node.removeNode()
        
    def OnButtonClicked(self, buttonText):
        if(buttonText == 'okay'):
            self.okayFunction(self)
        elif(buttonText == 'cancel'):
            self.cancelFunction(self)