from panda3d.core import WindowProperties, Vec3
from direct.showbase.DirectObject import DirectObject

from event.MenuEvent import MenuOpenEvent, MenuCloseEvent
from event.ClientEvent import TeamSelectEvent
from event.WindowEvent import WindowFocusEvent
from gui.menus.InGameMenu import InGameMenu
from gui.menus.TeamSelectMenu import TeamSelectMenu
from gui.Scoreboard import Scoreboard

import Globals
from event.PlayerEvent import PlayerRespawnEvent


# Handles all mouse interaction with menus
class MenuController(DirectObject):
    
    def __init__(self, engine, invGUI):
        self.engine = engine
        self.invGUI = invGUI
        self.inGameMenu = InGameMenu()
        self.teamSelectMenu = TeamSelectMenu()
        #self.scoreboard = Scoreboard()
        self.currentMenu = None
        #self.SetupModifierKeys()
        self.HideCursor()
        self.accept(WindowFocusEvent.EventName, self.OnWindowFocusEvent)
          
        
    def EnableKeyboardListening(self):
        print self.currentMenu
        self.acceptOnce('escape', self.CloseCurrentMenu)
        if(self.currentMenu == self.invGUI):
            self.accept('e', self.CloseInventory)
        elif(self.currentMenu == self.teamSelectMenu):
            self.acceptOnce('a', self.teamSelectMenu.OnTeamSelect, extraArgs = [0])
            self.acceptOnce('s', self.teamSelectMenu.OnTeamSelect, extraArgs = [1])
            #self.acceptOnce('d', self.teamSelectMenu.OnTeamSelect, extraArgs = [2])
            self.accept(TeamSelectEvent.EventName, self.OnTeamSelectEvent)
#        elif(self.currentMenu == self.scoreboard):
#            self.acceptOnce('tab', self.CloseCurrentMenu)
        
    def DisableKeyboardListening(self):
        self.ignore('escape')
        self.ignore(TeamSelectEvent.EventName)
        self.ignore('e')
        self.ignore('a')
        self.ignore('s')
        self.ignore('d')
        
    def Update(self):
        if(self.IsMenuOpen()):
            self.currentMenu.Update()
        
    def IsMenuOpen(self):
        return self.currentMenu is not None
                
    def OnMenuOpened(self):
        self.cursorIsVisible = 1
        self.ShowCursor()
        MenuOpenEvent(self.currentMenu).Fire()
        
    def OnMenuClosed(self):
        self.cursorIsVisible = 0
        self.currentMenu = None
        self.HideCursor()
        MenuCloseEvent(self.currentMenu).Fire()
        
    def ShowCursor(self):
        wp = WindowProperties()
        wp.setCursorHidden(False)
        base.win.requestProperties(wp)
        
    def HideCursor(self):
        wp = WindowProperties()
        wp.setCursorHidden(True)
        base.win.requestProperties(wp)

    def CloseCurrentMenu(self):
        self.currentMenu.Hide()
        self.OnMenuClosed()
        
    def OpenMenu(self, menu):
        self.currentMenu = menu
        self.currentMenu.Show()
        self.OnMenuOpened()
        
    def OpenInventory(self):
        self.OpenMenu(self.invGUI)
        
    def CloseInventory(self):
        if(self.currentMenu == self.invGUI):
            self.CloseCurrentMenu()
            
    def OpenInGameMenu(self):
        self.OpenMenu(self.inGameMenu)
        
    def OpenTeamSelectMenu(self):
        self.OpenMenu(self.teamSelectMenu)
        
#    def OpenScoreboard(self):
#        self.OpenMenu(self.scoreboard)
        
    def OnTeamSelectEvent(self, team):
        #self.engine.OnTeamSelected(team)
        self.CloseCurrentMenu()
        if(Globals.OFFLINE):
            PlayerRespawnEvent(self.engine.GetPlayerController().GetMyself(), self.engine.GetEnvironment().GetHighestBlock(2, 2)).Fire() 
        
    def OnWindowFocusEvent(self, event):
        if(event.GetIsFocused() and not self.IsMenuOpen()):
            self.HideCursor()
        else:
            self.ShowCursor()
        
    def Destroy(self):
        self.invGUI.Destroy()
        self.inGameMenu.Destroy()
        self.teamSelectMenu.Destroy()
        
        del self.invGUI
        del self.inGameMenu
        del self.teamSelectMenu
        del self.currentMenu
        self.ignoreAll()
        
#    def SetupModifierKeys(self):
#        self.modifierKeys = {'SHIFT':0, 'CTRL':0}
#        self.accept('shift', self.setKey, ['SHIFT', 1])
#        self.accept('shift-up', self.setKey, ['SHIFT', 0])
#        self.accept('control', self.setKey, ['CTRL', 1])
#        self.accept('control-up', self.setKey, ['CTRL', 0])
        