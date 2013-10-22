from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton, DGG

from gui.menus.Menu import Menu
from gui.AlertPopup import AlertPopup

"""
egg-texture-cards -o Button_Multiplayer.egg -p 500,75 multiplayer.png multiplayer_over.png
egg-texture-cards -o Button_Options.egg -p 500,75 options.png options_over.png
egg-texture-cards -o Button_Exit.egg -p 500,75 exit.png exit_over.png

"""

class InGameMenu(Menu):
    
    def __init__(self):
        Menu.__init__(self)
        self.buttons = []
        self.LoadContent()
        
    def LoadContent(self):
        bg = OnscreenImage(image = 'Assets/Images/Inventory/BlackScreen.png', scale = (2, 1, 1))
        bg.setTransparency(TransparencyAttrib.MAlpha)
        bg.reparentTo(self.node)
        
        self.LoadButton('Button_Multiplayer', 'multiplayer', 'multiplayer_over', 0, 0, self.OnButtonClicked, ['multiplayer'])
        self.LoadButton('Button_Options', 'options', 'options_over', 0, -0.3, self.OnButtonClicked, ['options'])
        self.LoadButton('Button_Exit', 'exit', 'exit_over', 0, -0.6, self.OnButtonClicked, ['exit'])
        
    def LoadButton(self, egg, up, over, x, y, cmd, args):
        maps = loader.loadModel("Assets/Images/Menus/MainMenu/%s" % (egg))
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
                         scale = (1, 1, 75.0/500.0))
        b.reparentTo(self.node)
        self.buttons.append(b)
        
    def OnButtonClicked(self, buttonText):
        if(buttonText == 'multiplayer'):
            pass
        elif(buttonText == 'options'):
            pass
        elif(buttonText == 'exit'):
            p = AlertPopup('Leave Game', 'Do you really want to leave this game?', self.OnExitPopupOkay, self.OnExitPopupCancel)
            
    def OnExitPopupOkay(self, popup):
        self.DestroyPopup(popup)
        messenger.send('goBackToMain')    
        
    def OnExitPopupCancel(self, popup):
        self.DestroyPopup(popup)
            
    def OnPopupCreated(self, popup):
        for button in self.buttons:
            button['state'] = DGG.DISABLED
            
    def DestroyPopup(self, popup):
        popup.Destroy()
        del popup
        
        for button in self.buttons:
            button['state'] = DGG.NORMAL
            
    def Hide(self):
        self.node.hide()   
        
    def Show(self):
        self.node.show()     
        
    def Destroy(self):
        self.node.removeNode()
        for b in self.buttons:
            b.destroy()
        