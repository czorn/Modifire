
from event.Event import Event

class WindowEvent(Event):
    
    EventName = 'WindowEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)
        
class WindowFocusEvent(WindowEvent):
    
    eventName = 'WindowFocusEvent'
    
    def __init__(self, isFocused):
        WindowEvent.__init__(self, WindowFocusEvent.EventName)
        self.isFocused = isFocused
        
    def GetIsFocused(self):
        return self.isFocused