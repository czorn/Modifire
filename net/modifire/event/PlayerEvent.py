
from event.Event import Event

class PlayerEvent(Event):
    
    EventName = 'PlayerEvent'
    
    def __init__(self, player, eventName = EventName):
        Event.__init__(self, eventName)
        self.player = player
        
    def GetPlayer(self):
        return self.player    

class PlayerDeathEvent(PlayerEvent):
    
    EventName = 'PlayerDeathEvent'
    
    def __init__(self, player, attacker, wasHeadshot):
        PlayerEvent.__init__(self, player, PlayerDeathEvent.EventName)
        self.attacker = attacker
        self.wasHeadshot = wasHeadshot
        
        from player.PlayerState import PlayerState
        
    def GetVictim(self):
        return self.player
        
    def GetAttacker(self):
        return self.attacker
    
    def WasHeadshot(self):
        return self.wasHeadshot
        
class PlayerRespawnEvent(PlayerEvent):
    
    EventName = 'PlayerRespawnEvent'
    
    def __init__(self, player, pos):
        PlayerEvent.__init__(self, player, PlayerRespawnEvent.EventName)
        self.pos = pos
        
    def GetPos(self):
        return self.pos
    
  
class PlayerJoinEvent(PlayerEvent):
    
    EventName = 'PlayerJoinEvent'
    
    def __init__(self, player, pid, name, playingState, teamId, item, itemData):
        PlayerEvent.__init__(self, player, PlayerJoinEvent.EventName)
        self.pid = pid
        self.name = name
        self.playingState = playingState
        self.teamId = teamId
        self.item = item
        self.itemData = itemData
        
    def GetPid(self):
        return self.pid
    
    def GetName(self):
        return self.name
    
    def GetTeamId(self):
        return self.teamId
    
    def GetPlayingState(self):
        return self.playingState
    
    def GetItemId(self):
        return self.item
    
    def GetItemData(self):
        return self.itemData
    
class PlayerDisconnectEvent(PlayerEvent):
    
    EventName = 'PlayerDisconnectEvent'
    
    def __init__(self, player):
        PlayerEvent.__init__(self, player, PlayerDisconnectEvent.EventName)
        
        
class PlayerSelectedEvent(PlayerEvent):
    
    EventName = 'PlayerSelectedEvent'
    
    def __init__(self, player):
        PlayerEvent.__init__(self, player, PlayerSelectedEvent.EventName)
        
class PlayerAttackEvent(PlayerEvent):
    
    EventName = 'PlayerAttackEvent'
    
    def __init__(self, player, victim, damage, wasHeadshot):
        PlayerEvent.__init__(self, player, PlayerAttackEvent.EventName)
        self.victim = victim
        self.damage = damage
        self.wasHeadshot = wasHeadshot
        
    def GetAttacker(self):
        return self.player
        
    def GetVictim(self):
        return self.victim
    
    def GetDamage(self):
        return self.damage
    
    def WasHeadshot(self):
        return self.wasHeadshot
    
class PlayerHitEvent(PlayerEvent):
    
    EventName = 'PlayerHitEvent'
    
    def __init__(self, player, victim, wasHeadshot):
        PlayerEvent.__init__(self, player, PlayerHitEvent.EventName)
        self.victim = victim
        self.wasHeadshot = wasHeadshot
        
    def GetAttacker(self):
        return self.player
        
    def GetVictim(self):
        return self.victim
    
    def GetDamage(self):
        return self.damage
    
    def WasHeadshot(self):
        return self.wasHeadshot
    
class PlayerHealthEvent(PlayerEvent):
    
    EventName = 'PlayerHealthEvent'
    
    def __init__(self, player, health):
        PlayerEvent.__init__(self, player, PlayerHealthEvent.EventName)
        self.health = health
        
    def GetHealth(self):
        return self.health
    
class PlayerReloadEvent(PlayerEvent):
    
    EventName = 'PlayerReloadEvent'
    
    def __init__(self, player):
        PlayerEvent.__init__(self, player, PlayerReloadEvent.EventName)
        
        
class TeamChangeEvent(PlayerEvent):
    
    EventName = 'TeamChangeEvent'
    
    def __init__(self, player, teamId):
        PlayerEvent.__init__(self, player, TeamChangeEvent.EventName)
        self.teamId = teamId
        
    def GetTeam(self):
        return self.teamId
        
        