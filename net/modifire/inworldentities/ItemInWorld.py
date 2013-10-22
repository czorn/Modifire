from panda3d.core import VBase3
from panda3d.core import CollisionNode, BitMask32, CollisionSphere
from direct.interval.IntervalGlobal import Sequence, LerpHprInterval
import Globals
from random import randint 
import Settings  

class ItemInWorld():
    
    def __init__(self, itemType, modelName, collisionString):
        self.type = itemType
        self.itemNode = render.attachNewNode('itemNode')
        self.velocity = VBase3(0, 0, 0)
        self.zVelocity0 = 0
        self.timeElapsed = 0
        self.LoadContent(modelName)   
        self.SetupCollision(collisionString)
        
    def SetupCollision(self, collisionString):
        radius = 0.2
        collisionGeom = self.itemNode.attachNewNode(CollisionNode('itemCollision'))
        collisionGeom.node().addSolid(CollisionSphere(0, 0, radius/2.0, radius))
        collisionGeom.node().setFromCollideMask(BitMask32.allOff())
        collisionGeom.node().setIntoCollideMask(Globals.ITEM_BITMASK)
        collisionGeom.node().setTag('item', collisionString)
        
    def LoadContent(self, modelName):
        loader.loadModel("Assets/Models/Items/%s" % (modelName), callback = self.OnModelLoaded)
        
    def OnModelLoaded(self, m):
        self.model = m
        self.model.setScale(0.2)
        self.model.reparentTo(self.itemNode)
        self.model.setPos(VBase3(0, 0, 0.5 + (10 - randint(0, 20))/500.0))
        
        self.spinSequence = Sequence(LerpHprInterval(self.model, 2, VBase3(180, 0, 0), VBase3(0, 0, 0)),
                                     LerpHprInterval(self.model, 2, VBase3(360, 0, 0), VBase3(180, 0, 0)))
        self.spinSequence.loop()
    
    def SetPos(self, pos):
        self.itemNode.setPos(pos)
        
    def GetPos(self):
        return self.itemNode.getPos()
        
    def UpdatePos(self, deltaTime):
        self.timeElapsed += deltaTime
        dz = (self.zVelocity0 + Settings.GRAVITY * self.timeElapsed) * deltaTime
        self.velocity.setZ(self.velocity.getZ() + dz)
        self.itemNode.setPos(self.itemNode.getPos() + self.velocity * deltaTime)
        
    def Destroy(self):
        self.itemNode.removeNode()
        
    def StartSpin(self):
        pass
        
        
    def StopSpin(self):
        self.spinSequence.stop()