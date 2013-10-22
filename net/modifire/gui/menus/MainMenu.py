from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib, VBase3
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton, DGG
from direct.interval.IntervalGlobal import Sequence, LerpHprInterval

from gui.Popup import Popup
from gui.AlertPopup import AlertPopup
from gui.FullscreenPopup import FullscreenPopup
from event.ClientEvent import ServerJoinResponseEvent
import Settings
import SettingsController
import Globals

"""
egg-texture-cards -o Button_Offline.egg -p 500,75 offline.png offline_over.png
egg-texture-cards -o Button_Multiplayer.egg -p 500,75 multiplayer.png multiplayer_over.png
egg-texture-cards -o Button_Options.egg -p 500,75 options.png options_over.png
egg-texture-cards -o Button_Exit.egg -p 500,75 exit.png exit_over.png

"""

class MainMenu(DirectObject):
    
    def __init__(self):
        self.node = aspect2d.attachNewNode('MainMenu')
        self.buttons = []
        self.LoadContent()
        self.SetupEventHandlers()
        
    def SetupEventHandlers(self):
        self.accept(ServerJoinResponseEvent.EventName, self.OnServerJoinResponseEvent)
        
        
    def LoadContent(self):
        bg = OnscreenImage(image = 'Assets/Images/Menus/MainMenu/background.png', scale = (2, 1, 1))
        bg.setTransparency(TransparencyAttrib.MAlpha)
        bg.reparentTo(self.node)
        bg.setBin('fixed', 1)
        
        title = OnscreenImage(image = 'Assets/Images/Menus/MainMenu/title.png')
        title.setTransparency(TransparencyAttrib.MAlpha)
        title.reparentTo(self.node)
        
        self.spinner = OnscreenImage(image = 'Assets/Images/Menus/MainMenu/loadingSpinner.png', pos = (-0.15, 1, 0.15), scale = 128.0/1024.0)
        self.spinner.setTransparency(TransparencyAttrib.MAlpha)
        self.spinner.reparentTo(base.a2dBottomRight)
        self.spinner.setBin('gui-popup', 0)
        self.spinner.hide()
        
        self.LoadButton('Button_Offline', 'offline', 'offline_over', 0, 0.2, self.OnButtonClicked, ['offline'])
        self.LoadButton('Button_Multiplayer', 'multiplayer', 'multiplayer_over', 0, 0, self.OnButtonClicked, ['multiplayer'])
        self.LoadButton('Button_Options', 'options', 'options_over', 0, -0.2, self.OnButtonClicked, ['options'])
        self.LoadButton('Button_Exit', 'exit', 'exit_over', 0, -0.4, self.OnButtonClicked, ['exit'])
        
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
            Globals.ROCKET_CONTEXT.LoadDocument('Assets/libRocket/multiplayer.rml').Show()
            self.DisableButtons()
            self.acceptOnce('multiplayerPopupClose', self.OnMultiplayerClose)
        
        elif(buttonText == 'options'):
            Globals.ROCKET_CONTEXT.LoadDocument('Assets/libRocket/options.rml').Show()
            self.DisableButtons()
            self.acceptOnce('optionsPopupClose', self.OnOptionsClose)
            
        elif(buttonText == 'exit'):
            self.CreateAlertPopup('Exit Game', 'Do you really want to exit?', self.OnExitPopupOkay, self.OnExitPopupCancel)
            
        elif(buttonText == 'offline'):
            Globals.ROCKET_CONTEXT.LoadDocument('Assets/libRocket/offline.rml').Show()
            self.DisableButtons()
            self.acceptOnce('offlinePopupClose', self.OnOfflineClose)
            
    def CreatePopup(self, title, fields, values, onOkay, onCancel):
        p = Popup(title, fields, values, onOkay, onCancel)
        self.OnPopupCreated(p)
        
    def CreateAlertPopup(self, title, text, onOkay, onCancel):
        p = AlertPopup(title, text, onOkay, onCancel)
        self.OnPopupCreated(p)
        
    def CreateFullScreenPopup(self, title, fields, values, onOkay, onCancel):
        p = FullscreenPopup(title, fields, values, onOkay, onCancel)
        self.OnPopupCreated(p)                              
            
    def OnOfflineClose(self, accept):
        if(accept):
            SettingsController.SaveClientSettings()
            taskMgr.doMethodLater(0.1, messenger.send, 'as', ['startOffline'])
        self.EnableButtons()
        
    def OnOptionsClose(self, accept):
        if(accept):
            SettingsController.SaveClientSettings()
        self.EnableButtons()
            
    def OnMultiplayerClose(self, accept):
        if(accept):
            SettingsController.SaveClientSettings()
            self.StartLoadingSpinner()
            self.DisableButtons()
            taskMgr.doMethodLater(0.1, messenger.send, 'as1', ['mainMenuMulti'])
        else:
            self.EnableButtons()
        
    def DisableButtons(self):
        for b in self.buttons:
            b['state'] = DGG.DISABLED
            
    def EnableButtons(self):
        for b in self.buttons:
            b['state'] = DGG.NORMAL
        
    def OnAlertPopupClose(self, popup):
        self.DestroyPopup(popup)
        
    def OnExitPopupOkay(self, popup):
        self.DestroyPopup(popup)
        messenger.send('mainMenuExit')
        
    def OnExitPopupCancel(self, popup):
        self.DestroyPopup(popup)
            
    def OnPopupCreated(self, popup):
        self.DisableButtons()
            
    def DestroyPopup(self, popup):
        popup.Destroy()
        del popup
        
        self.EnableButtons()
            
    def Hide(self):
        self.node.hide()
        
    def Show(self):
        self.node.show()
        
    def StartLoadingSpinner(self):
        self.spinner.show()
        self.spinSequence = Sequence(LerpHprInterval(self.spinner, 2, VBase3(0, 0, 180), VBase3(0, 0, 0)),
                                     LerpHprInterval(self.spinner, 2, VBase3(0, 0, 360), VBase3(0, 0, 180)))
        self.spinSequence.loop()
        
    def StopLoadingSpinner(self):
        self.spinSequence.finish()
        self.spinner.hide()
        
    def OnServerJoinResponseEvent(self, event):
        self.StopLoadingSpinner()
        self.EnableButtons()
        if(not event.GetResponse()):
            p = AlertPopup('Join Game Failed', event.GetReason(), self.ClosePopup, self.ClosePopup)
            self.OnPopupCreated(p)
        
    def ClosePopup(self, popup):
        self.DestroyPopup(popup)
        
        
        