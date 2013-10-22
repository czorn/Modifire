from panda3d.core import VBase3

from player.Input import Input

class Snapshot():
    
    def __init__(self, myInput = Input(), pos = VBase3(0, 0, 0), t = 0):
        self.inputCommands = myInput
        self.pos = pos
        self.timestamp = t
        
    def GetInput(self):
        return self.inputCommands
    
    def GetPosition(self):
        return self.pos
    
    def GetTimestamp(self):
        return self.timestamp