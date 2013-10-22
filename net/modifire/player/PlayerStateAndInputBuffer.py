
from player.PlayerState import PlayerState
from player.Input import Input

class PlayerStateAndInputBuffer():
    
    def __init__(self, currentState = None, newestInput = None, bufferedInput = None):
        self.currentState = currentState
        self.newestInput = newestInput
        self.bufferedInput = bufferedInput
        
    def SetPlayerState(self, ps):
        self.currentState = ps
        
    def GetPlayerState(self):
        return self.currentState
    
    def UpdateInput(self, newInput):
        """ Adds new input and sets current input as buffered input."""
        self.bufferedInput = self.newestInput
        self.newestInput = newInput
        
    def GetNewestInput(self):
        return self.newestInput
    
    def GetBufferedInput(self):
        return self.bufferedInput
    
    def GoodToGo(self):
        return (self.newestInput is not None) and (self.bufferedInput is not None)