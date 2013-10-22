
class Event():
    
    EventName = 'Event'
    
    def __init__(self, eventName = EventName):
        self.eventName = eventName
        
    def GetEventName(self):
        return self.eventName
    
    def Fire(self, task = None):
        messenger.send(self.eventName, [self])
        