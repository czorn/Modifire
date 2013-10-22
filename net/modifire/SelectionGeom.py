from pandac.PandaModules import GeomNode, GeomVertexData, GeomVertexFormat, Geom
from pandac.PandaModules import GeomLines, GeomVertexWriter, Texture, TextureAttrib, LineSegs, Vec4, Point3

# The white cube that surrounds the block currently selected by the player

class SelectionGeom():
    def __init__(self):
        points = []
        points.append(Point3(-0.001, -0.001, -0.001))
        points.append(Point3(-0.001, -0.001, 1.001))
        
        # Vert front right
        points.append(Point3(1.001, -0.001, -0.001))
        points.append(Point3(1.001, -0.001, 1.001))
        
        # Vert back right
        points.append(Point3(1.001, 1.001, -0.001))
        points.append(Point3(1.001, 1.001, 1.001))
        
        # Vert back left
        points.append(Point3(-0.001, 1.001, -0.001))
        points.append(Point3(-0.001, 1.001, 1.001))
        
        segs = LineSegs( ) 
        segs.setThickness( 5.0 ) 
        segs.setColor( Vec4(1,1,1,1) ) 
        
        self.DrawLine(segs, points, 0, 1)
        self.DrawLine(segs, points, 2, 3)
        self.DrawLine(segs, points, 4, 5)
        self.DrawLine(segs, points, 6, 7)
        
        self.DrawLine(segs, points, 0, 2)
        self.DrawLine(segs, points, 1, 3)
        self.DrawLine(segs, points, 4, 6)
        self.DrawLine(segs, points, 5, 7)
        
        self.DrawLine(segs, points, 0, 6)
        self.DrawLine(segs, points, 1, 7)
        self.DrawLine(segs, points, 2, 4)
        self.DrawLine(segs, points, 3, 5)
        
        self.selectionGeom = render.attachNewNode(segs.create())
        self.selectionGeom.setLightOff()
        
    def DrawLine(self, segs, points, u, v):
        segs.moveTo(points[u])
        segs.drawTo(points[v])
        
    def SetPos(self, x, y, z):
        self.selectionGeom.setPos(x, y, z)
        
    def GetPos(self):
        return self.selectionGeom.getPos()
    
    def Show(self):
        self.selectionGeom.show()
        
    def Hide(self):
        self.selectionGeom.hide()
        
    def Destroy(self):
        self.selectionGeom.removeNode()