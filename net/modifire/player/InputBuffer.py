
from player.PlayerState import PlayerState
from player.Input import Input

class InputBuffer():
    
    def __init__(self, newestInput = None, bufferedInput = None):
        self.newestInput = newestInput
        self.bufferedInput = bufferedInput
    
    def UpdateInput(self, newInput):
        """ Adds new input and sets current input as buffered input."""
        self.bufferedInput = self.newestInput
        self.newestInput = newInput
        
    def Clear(self):
        self.newestInput = None
        self.bufferedInput = None
        
    def GetNewestInput(self):
        return self.newestInput
    
    def GetBufferedInput(self):
        return self.bufferedInput
    
    # True if we have both sets of inputs
    def GoodToGo(self):
        return (self.newestInput is not None) and (self.bufferedInput is not None)