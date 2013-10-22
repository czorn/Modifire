
from event.Event import Event

class EnvironmentEvent(Event):
    
    EventName = 'EnvironmentEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)

class EnvironmentChangeEvent(EnvironmentEvent):
    
    EventName = 'EnvironmentChangeEvent'
    
    def __init__(self, destroyedBlocks, addedBlocks):
        EnvironmentEvent.__init__(self, EnvironmentChangeEvent.EventName)
        self.destroyedBlocks = destroyedBlocks
        self.addedBlocks = addedBlocks
        
    def GetDestroyedBlocks(self):
        return self.destroyedBlocks
    
    def GetAddedBlocks(self):
        return self.addedBlocks