
from event.Event import Event

class CameraEvent(Event):
    
    EventName = 'CameraEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)  

class ViewModeChangeEvent(CameraEvent):
    
    EventName = 'ViewModeChangeEvent'
    
    def __init__(self, viewMode):
        CameraEvent.__init__(self, ViewModeChangeEvent.EventName)
        self.viewMode = viewMode
        
    def GetViewMode(self):
        return self.viewMode
    
class ADSEvent(CameraEvent):
    
    EventName = 'ADSEvent'
    
    def __init__(self, isADS, adsTime, fov, mouseSpeedModifire):
        CameraEvent.__init__(self, ADSEvent.EventName)
        self.isADS = isADS
        self.adsTime = adsTime
        self.fov = fov
        self.mouseSpeedModifire = mouseSpeedModifire
        
    def GetIsADS(self):
        return self.isADS
    
    def GetTime(self):
        return self.adsTime
    
    def GetFOV(self):
        return self.fov
    
    def GetMouseSpeedModifire(self):
        return self.mouseSpeedModifire
    
    
    
    
    
    