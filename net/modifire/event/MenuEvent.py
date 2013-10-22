
from event.Event import Event

class MenuEvent(Event):
    
    EventName = 'MenuEvent'
    
    def __init__(self, menu, eventName = EventName):
        Event.__init__(self, eventName)
        self.menu = menu
        
    def GetMenu(self):
        return self.menu    

class MenuCloseEvent(MenuEvent):
    
    EventName = 'MenuCloseEvent'
    
    def __init__(self, menu):
        MenuEvent.__init__(self, menu, MenuCloseEvent.EventName)
        
class MenuOpenEvent(MenuEvent):
    
    EventName = 'MenuOpenEvent'
    
    def __init__(self, menu):
        MenuEvent.__init__(self, menu, MenuOpenEvent.EventName)