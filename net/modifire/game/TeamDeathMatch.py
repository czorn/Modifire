
from game.Game import Game
from player.PlayerState import PlayerState

class TeamDeathMatch(Game):
    
    def __init__(self, maxScore = 25):
        Game.__init__(self)
        self.scores = [0, 0]
        self.maxScore = 25
        
    def OnPlayerDeathEvent(self, event):
        attacker = event.GetAttacker()
        victim = event.GetVictim()
        if(attacker !=  victim):
            teamId = attacker.GetPlayerState().GetValue(PlayerState.TEAM)
            self.scores[teamId] += 1
            if(self.scores[teamId] >= self.maxScore):
                print 'GAME OVER. TEAM ', teamId, ' WON'
            