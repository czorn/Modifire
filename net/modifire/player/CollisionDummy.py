import Globals
from pandac.PandaModules import BitMask32, CollisionNode, CollisionSphere

class CollisionDummy():
    
    def __init__(self):
        self.pNode = render.attachNewNode('CollisionDummyNode')
        self.collisionGeom =  self.pNode.attachNewNode(CollisionNode('collisionDummy'))
        self.collisionGeom.node().addSolid(CollisionSphere(0, 0, 0.25 + 0.1, 0.25))
        self.collisionGeom.node().setFromCollideMask(Globals.WALL_BITMASK)
        self.collisionGeom.node().setIntoCollideMask(BitMask32.allOff())
        #self.collisionGeom.show()
        
    def SetPos(self, pos):
        self.pNode.setPos(pos)
        
    def GetPos(self):
        return self.pNode.getPos()
        
    def GetCollisionNode(self):
        return self.collisionGeom
    
    def GetNode(self):
        return self.pNode