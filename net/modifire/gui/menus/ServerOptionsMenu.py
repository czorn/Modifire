from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TransparencyAttrib, TextNode
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectEntry

import Settings

from gui.menus.Menu import Menu
from event.ServerEvent import ServerStartEvent

class ServerOptionsMenu(Menu):
    
    def __init__(self):
        Menu.__init__(self)
        
        fieldValues = {'Server Name' : Settings.SERVER_NAME,
                       'World Name' : Settings.LAST_WORLD }
        self.fields = {}
        
        y = 0
        for fieldLabel, initText in fieldValues.iteritems():
            self.fields[fieldLabel] = self.CreateField(fieldLabel, initText, y, False)
            y += 1
            
        self.instructions = OnscreenText(text = 'Press Enter to start server', pos = (-0.1, 0.1), scale = 0.09, fg = (1, 1, 1, 1), align = TextNode.ARight, parent = base.a2dBottomRight)
            
        self.Show()
        
        self.acceptOnce('enter', self.OnStart)
            
    def OnStart(self):
        Settings.SERVER_NAME = self.GetValue('Server Name')
        Settings.LAST_WORLD = self.GetValue('World Name')
        ServerStartEvent().Fire()
        self.Destroy()
        
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
        f.reparentTo(self.node)
        return f
    
    def GetValue(self, key):
        return self.fields[key].get()
    
    def Destroy(self):
        self.node.removeNode()
        self.instructions.destroy()