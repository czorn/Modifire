from panda3d.core import Vec3
from player.PlayerState import PlayerState

class Input():
    
    def __init__(self, keys = [], lookingDir = Vec3(0, 1, 0), clicks = [], t = 0):
        self.keys = keys
        self.lookingDir = lookingDir
        self.timestamp = t
        
        if(PlayerState.CLICK_1 in clicks):
            self.click1 = True
        else:
            self.click1 = False
            
        if(PlayerState.CLICK_3 in clicks):
            self.click3 = True
        else:
            self.click3 = False
        
    def GetTimestamp(self):
        return self.timestamp
    
    def SetTimestamp(self, t):
        self.timestamp = t
    
    def GetLookingDir(self):
        return self.lookingDir
    
    def GetKeys(self):
        return self.keys