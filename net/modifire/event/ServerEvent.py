
from event.Event import Event

class ServerEvent(Event):
    
    EventName = 'ServerEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)  

class ServerStartEvent(ServerEvent):
    
    EventName = 'ServerStartEvent'
    
    def __init__(self):
        ServerEvent.__init__(self, ServerStartEvent.EventName)
            
class FinishedSendingEnvironmentEvent(ServerEvent):
    
    EventName = 'FinishedSendingEnvironmentEvent'
    
    def __init__(self, peerAddr):
        ServerEvent.__init__(self, FinishedSendingEnvironmentEvent.EventName)
        self.peerAddr = peerAddr
        
    def GetPeerAddr(self):
        return self.peerAddr