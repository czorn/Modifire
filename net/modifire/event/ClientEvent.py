
from event.Event import Event

class ClientEvent(Event):
    
    EventName = 'ClientEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)  

class LoadEngineEvent(ClientEvent):
    
    EventName = 'LoadEngineEvent'
    
    def __init__(self):
        ClientEvent.__init__(self, LoadEngineEvent.EventName)

class EngineLoadedEvent(ClientEvent):
    
    EventName = 'EngineLoadedEvent'
    
    def __init__(self):
        ClientEvent.__init__(self, EngineLoadedEvent.EventName)
        
class ServerJoinResponseEvent(ClientEvent):
    
    EventName = 'ServerJoinResponseEvent'
    
    def __init__(self, response, reason):
        ClientEvent.__init__(self, ServerJoinResponseEvent.EventName)    
        self.response = response
        self.reason = reason
        
    def GetResponse(self):
        return self.response
    
    def GetReason(self):
        return self.reason
        
class TeamSelectEvent(ClientEvent):
    
    EventName = 'TeamSelectEvent'
    
    def __init__(self, team):
        ClientEvent.__init__(self, TeamSelectEvent.EventName)
        self.team = team
        
    def GetTeam(self):
        return self.team
    
class LoadProgressEvent(ClientEvent):
    
    EventName = 'LoadProgressEvent'
    
    def __init__(self, text, value):
        ClientEvent.__init__(self, LoadProgressEvent.EventName)
        self.text = text
        self.value = value
        
    def GetText(self):
        return self.text
    
    def GetValue(self):
        return self.value
    
class ListOfConnectedPlayersReceivedEvent(ClientEvent):
    
    def __init__(self, playerStates):
        ClientEvent.__init__(self, ListOfConnectedPlayersReceivedEvent.EventName)
        self.playerStates = playerStates
        
    def GetPlayerStates(self):
        return self.playerStates
    
class PeerTimeoutEvent(ClientEvent):
    
    EventName = 'PeerTimeoutEvent'
    
    def __init__(self, peerAddr):
        ClientEvent.__init__(self, PeerTimeoutEvent.EventName)
        self.peerAddr = peerAddr
        
    def GetPeerAddr(self):
        return self.peerAddr
            