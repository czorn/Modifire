
from event.Event import Event

class DebugEvent(Event):
    
    EventName = 'DebugEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)  

class ChunkTimeEvent(DebugEvent):
    
    EventName = 'ChunkTimeEvent'
    
    def __init__(self, t):
        DebugEvent.__init__(self, ChunkTimeEvent.EventName)
        self.t = t
        
    def GetTime(self):
        return self.t
    
class BandwidthInfoEvent(DebugEvent):
    
    EventName = 'BandwidthInfoEvent'
    
    def __init__(self, in1, out1):
        DebugEvent.__init__(self, BandwidthInfoEvent.EventName)
        self.in1 = in1
        self.out1 = out1
        
    def GetIncoming(self):
        return self.in1
    
    def GetOutgoing(self):
        return self.out1