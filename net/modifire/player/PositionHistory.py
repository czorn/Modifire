
from pandac.PandaModules import Vec3
from collections import deque

import Globals

class PositionHistory():
    
    DEQUEUE_LENGTH = Globals.SERVER_SEND_RATE
    
    def __init__(self):
        self.posQueue = deque()
        
        for i in xrange(PositionHistory.DEQUEUE_LENGTH - 1):
            self.posQueue.append(None)
            
        self.posQueue.append(Vec3(0, 0, 0))
            
    def AddPosition(self, pos):
        self.posQueue.append(pos)
        self.posQueue.popleft()
        
    def GetPosition(self, index):
        if(PositionHistory.DEQUEUE_LENGTH - index - 1 < 0 or PositionHistory.DEQUEUE_LENGTH - index - 1 > PositionHistory.DEQUEUE_LENGTH - 1):
            print 'ERROR INDEX in position history', index
            index = 0
        print 'pos index', PositionHistory.DEQUEUE_LENGTH - index - 1
        return self.posQueue[PositionHistory.DEQUEUE_LENGTH - index - 1]
    
    def GetMostRecentPosition(self):
        pos = self.posQueue.pop()
        self.posQueue.append(pos)
        return pos