
from pandac.PandaModules import Point3

class BoundingBox():
    
    def __init__(self, centerNode, halfWidths):
        self.centerNode = centerNode
        self.xw = halfWidths[0]
        self.yw = halfWidths[1]
        self.zw = halfWidths[2]
        self.lastAxisCollisions = [0, 0, 0]
        
    def IsCollidingWithBlock(self, bx, by, bz):
        bw = 0.5
        bCenter = Point3(bx + bw, by + bw, bz + bw)
        myCenter = self.centerNode.getPos(render)
        diff = bCenter - myCenter
        xTotal = abs(diff.getX())
        yTotal = abs(diff.getY())
        zTotal = abs(diff.getZ())
        
        if(xTotal >= self.xw + bw):
            return False
        
        if(yTotal >= self.yw + bw):
            return False
                
        if(zTotal >= self.zw + bw):
            return False
        
        if(myCenter.getX() > bCenter.getX()):
            self.lastAxisCollisions[0] = bCenter.getX() + bw - (myCenter.getX() - self.xw) + 0.001
        else:
            self.lastAxisCollisions[0] = bCenter.getX() - bw - (myCenter.getX() + self.xw) - 0.001
            
        if(myCenter.getY() > bCenter.getY()):
            self.lastAxisCollisions[1] = bCenter.getY() + bw - (myCenter.getY() - self.yw) + 0.001
        else:
            self.lastAxisCollisions[1] = bCenter.getY() - bw - (myCenter.getY() + self.yw) - 0.001
            
        if(myCenter.getZ() > bCenter.getZ()):
            self.lastAxisCollisions[2] = bCenter.getZ() + bw - (myCenter.getZ() - self.zw) + 0.001
        else:
            self.lastAxisCollisions[2] = bCenter.getZ() - bw - (myCenter.getZ() + self.zw) - 0.001
            
        return True