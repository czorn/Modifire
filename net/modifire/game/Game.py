import random

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Vec3, Vec4, Point3

import Settings
from player.PlayerState import PlayerState
from event.PlayerEvent import PlayerRespawnEvent, PlayerDeathEvent, PlayerAttackEvent
from item.ItemId import ItemId

class Game(DirectObject):
    
    (TEAM_1,
    TEAM_2,
    SPECTATE) = range(3)
    
    RESPAWN_TIME = 7
     
    def __init__(self, engine, playerController):
        self.engine = engine
        self.playerController = playerController
        self.teams = [[], [], []]   # Team 1, Team 2, Spectators
        self.accept(PlayerRespawnEvent.EventName, self.OnPlayerRespawnEvent)
        self.accept(PlayerDeathEvent.EventName, self.OnPlayerDeathEvent)
        self.accept(PlayerAttackEvent.EventName, self.OnPlayerAttackEvent)
     
    def Update(self):
        pass
                
    def AddPlayerToTeam(self, player, teamId):
        for team in self.teams:
            for p in team:
                if p == player:
                    team.remove(p)
                    
        self.teams[teamId].append(player)
        player.GetPlayerState().UpdateValue(PlayerState.TEAM, teamId)
        
        if(teamId == Game.SPECTATE):
            player.GetPlayerState().UpdateValue(PlayerState.PLAYING_STATE, PlayerState.PS_SPECTATE)
        
    def OnPlayerRespawnEvent(self, event):
        pass
        
    def OnPlayerDeathEvent(self, event):
        attacker = event.GetAttacker()
        victim = event.GetVictim()
        if(attacker !=  victim):
            attacker.GetPlayerState().UpdateValue(PlayerState.KILLS, attacker.GetPlayerState().GetValue(PlayerState.KILLS) + 1)
            
        victim.GetPlayerState().UpdateValue(PlayerState.DEATHS, victim.GetPlayerState().GetValue(PlayerState.DEATHS) + 1)         
        
    def OnPlayerAttackEvent(self, event):
        attacker = event.GetAttacker()
        victim = event.GetVictim()
        
        if(attacker != victim):
            # Update the attacker's score
            attacker.GetPlayerState().UpdateValue(PlayerState.SCORE, attacker.GetPlayerState().GetValue(PlayerState.SCORE) + event.GetDamage())
        
    def FindRespawnPoint(self, spawnRegion):
        if(spawnRegion):
            return Point3(2, 2, 20)
        else:
            env = self.engine.GetEnvironment()
            return env.GetHighestBlock(random.randint(0, env.GetNumBlocksX() - 1), random.randint(0, env.GetNumBlocksY() - 1))
        
    def Destroy(self):
        self.ignoreAll()
        del self.engine
        del self.playerController
        