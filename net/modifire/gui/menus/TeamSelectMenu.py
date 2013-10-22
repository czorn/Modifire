
from direct.gui.OnscreenText import OnscreenText
from event.ClientEvent import TeamSelectEvent, ListOfConnectedPlayersReceivedEvent
from gui.menus.Menu import Menu
from game.Game import Game
from player.PlayerState import PlayerState

import Globals

class TeamSelectMenu(Menu):
    
    def __init__(self):
        Menu.__init__(self)
        self.LoadContent()
        self.accept(ListOfConnectedPlayersReceivedEvent.EventName, self.OnListOfConnectedPlayersReceivedEvent)
        
    def LoadContent(self):
        self.text = OnscreenText(text = 'A - Team 1 (?)\nS - Team 2 (?)\nD - Spectate (?)',  pos = (0, -0.5), scale = 0.07, fg = (1, 1, 1, 1))
        self.text.reparentTo(self.node)
        
    def OnTeamSelect(self, team):
        Globals.MY_TEAM = team
        TeamSelectEvent(team).Fire() 
        
    def OnListOfConnectedPlayersReceivedEvent(self, event):
        team1 = 0
        team2 = 0
        spectators = 0
        for pState in event.GetPlayerStates():
            if(pState.GetValue(PlayerState.TEAM) == Game.TEAM_1):
                team1 += 1
            elif(pState.GetValue(PlayerState.TEAM) == Game.TEAM_2):
                team2 += 1
            elif(pState.GetValue(PlayerState.TEAM) == Game.SPECTATE):
                spectators += 1
                
        self.text.setText('A - Team 1 (%s)\nS - Team 2 (%s)\nD - Spectate (%s)' % (team1, team2, spectators))