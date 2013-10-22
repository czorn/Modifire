
from event.Event import Event

class HUDEvent(Event):
    
    EventName = 'HUDEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)  

class CrossHairEvent(HUDEvent):
    
    EventName = 'CrossHairEvent'
    
    def __init__(self, filename, show):
        HUDEvent.__init__(self, CrossHairEvent.EventName)
        self.filename = filename
        self.show = show
        
    def GetFilename(self):
        return self.filename
        
    def GetShow(self):
        return self.show