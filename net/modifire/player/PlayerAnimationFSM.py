from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import LerpAnimInterval

class PlayerAnimationFSM(FSM):
    
    def __init__(self, player):
        FSM.__init__(self, 'PlayerAnimationFSM')
        self.player = player
        
    def enterIdle(self):
        pass
    
    def exitIdle(self):
        pass
    
    def enterWalking(self):
        pass
    
    def exitWalking(self):
        pass
    
    def enterIdleToWalk(self):            
        i1 = LerpAnimInterval(self.player.playerModel, 0.5, 'walk', 'run') 
        i1.start() 
    
    def enterWalkToIdle(self):            
        i1 = LerpAnimInterval(self.player.playerModel, 0.5, 'run', 'walk') 
        i1.start()
        