from panda3d.rocket import DataSource #@UnresolvedImport

import Globals

from game.Game import Game
from player.PlayerState import PlayerState
from gui.mylibrocket.ScoreboardFormatter import ScoreboardFormatter
#from gui.mylibrocket.ScoreboardFormatter import ScoreboardIsAliveFormatter

class Scoreboard(DataSource):

    def __init__(self):
        self.rows = {}
        self.sortedRows = [[], [], []]    # Contains a sorted array for team 1 and team 2
        #self.docHandle = None
        DataSource.__init__(self, 'scoreboard') 
        
#        for i in range(5):
#            p = PlayerState(None)
#            p.SetValue(PlayerState.PID, i)
#            self.AddRow(p)
            
        #self.SortByScore()
        
        self.sf0 = ScoreboardFormatter()
        self.docHandle = None
        #self.docHandle = Globals.ROCKET_CONTEXT.LoadDocument('Assets/libRocket/scoreboard.rml')
        
    def Show(self):
        self.docHandle = Globals.ROCKET_CONTEXT.LoadDocument('Assets/libRocket/scoreboard.rml')
        self.docHandle.Show()
        
    def Hide(self):
        self.docHandle.owner_document.Close()

    def AddRow(self, pid, name, kills, deaths, assists, ping, team, pClass = 0, score = 0, isAlive = True):
        row =   Row(pid = pid,
                    name = name,
                    kills = kills,
                    deaths = deaths,
                    assists = assists,
                    team = team,
                    ping = ping,
                    pClass = pClass,
                    score = score,
                    isAlive = isAlive
                    )
        self.rows[pid] = row
        self.SortByScore()
        
    def NewRow(self, pid, name):
        self.AddRow(pid, name, 0, 0, 0, 0, Game.SPECTATE, 0, 0, True)
        
    def HasRow(self, pid):
        return pid in self.rows.keys()
    
    def RemoveRow(self, pid):
        if(self.HasRow(pid)):
            del self.rows[pid]
    
    def UpdateRow(self, pid, kills, deaths, assists, score, ping):
        if(self.HasRow(pid)):
            row = self.rows[pid]
            row.kills = kills
            row.deaths = deaths
            row.assists = assists
            row.score = score
            row.ping = ping
            self.SortByScore()
            
    def UpdateTeam(self, pid, team):
        if(self.HasRow(pid)):
            self.rows[pid].team = team
            self.SortByScore()
            
    def UpdateIsAlive(self, pid, isAlive):
        self.rows[pid].isAlive = isAlive
        
        if(self.rows[pid].team == Game.TEAM_1):
            self.NotifyRowChange('team1')
        
        elif(self.rows[pid].team == Game.TEAM_2):
            self.NotifyRowChange('team2')
        
        elif(self.rows[pid].team == Game.SPECTATE):
            self.NotifyRowChange('spectators')

    def SortByScore(self):
        team1 = []
        team2 = []
        spectators = []
        for x in self.rows.values():
            if(x.team == Game.TEAM_1):
                team1.append(x)
            elif(x.team == Game.TEAM_2):
                team2.append(x)
            elif(x.team == Game.SPECTATE):
                spectators.append(x)
                
        self.sortedRows = [self.SortArrayByScore(team1), self.SortArrayByScore(team2), self.SortArrayByScore(spectators)]
                
        self.NotifyRowChange('team1')
        self.NotifyRowChange('team2')
        self.NotifyRowChange('spectators')
                
    def SortArrayByScore(self, team):
        team = sorted(team, key = lambda x:x.name)
        team = sorted(team, key = lambda x:x.score, reverse = True)
        return team

    def GetRow(self, tableName, index, columns):
        colValues = []
        
        if(tableName == 'team1'):
            myDict = self.sortedRows[0]
        elif(tableName == 'team2'):
            myDict = self.sortedRows[1]
        elif(tableName == 'spectators'):
            myDict = self.sortedRows[2]
        else:
            return []

        for col in columns:
            
            if col == 'pid':
                colValues.append(str(myDict[index].pid))

            elif col == 'name':
                colValues.append(str(myDict[index].name))

            elif col == 'kills':
                colValues.append(str(myDict[index].kills))

            elif col == 'deaths':
                colValues.append(str(myDict[index].deaths))

            elif col == 'assists':
                colValues.append(str(myDict[index].assists))

            elif col == 'score':
                colValues.append(str(myDict[index].score))

            elif col == 'ping':
                colValues.append(str(myDict[index].ping))

            elif col == 'isAlive':
                colValues.append(str(myDict[index].isAlive))
                
        return colValues

    def GetNumRows(self, tableName):        
        if(tableName == 'team1'):
            return len(self.sortedRows[0])
        elif(tableName == 'team2'):
            return len(self.sortedRows[1])
        elif(tableName == 'spectators'):
            return len(self.sortedRows[2])
        else:
            return 0
        
    def Update(self):
        pass


class Row():

    def __init__(self, pClass, pid, name, kills, deaths, assists, team, score, ping, isAlive):
        self.playerClass = pClass
        self.name = name
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.ping = ping
        self.score = score
        self.pid = pid
        self.isAlive = isAlive
        self.team = team
