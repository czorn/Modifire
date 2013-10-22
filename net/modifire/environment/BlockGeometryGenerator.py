from pandac.PandaModules import  VBase3, VBase2

from environment.BlockGeom import BlockGeom
from environment.BlockFace import BlockFace
from environment.LightMaster import LightMaster

class BlockGeometryGenerator():
    
    @staticmethod
    def BlockIdToUV(bid):
        u0 = (bid % 16) / 16.0
        u1 = ((bid % 16) + 1) / 16.0
        
        v0 = 1 - ((bid / 16) + 1) / 16.0
        v1 = 1 - (bid / 16) / 16.0
        
        return ([u0, u1], [v0, v1])

    def GenerateBlockGeometry(self, x, y, z, block, faces):
        
        ((u0, u1), (v0, v1)) = BlockGeometryGenerator.BlockIdToUV(block.id)
        
        geomFaces = []
        
        for blockFace in faces:
            geomFaces.append(self.CreateBlockFace(block, blockFace, x, y, z, u0, u1, v0, v1))
        
        return geomFaces 
    
    def CreateBlockFace(self, block, blockFace, x, y, z, u0, u1, v0, v1):
        faceGeom = None
        if(blockFace == BlockFace.TOP):
            faceGeom = self.CreateBlockFaceTop(x, y, z, u0, u1, v0, v1)
            
        elif(blockFace == BlockFace.BOTTOM):
            faceGeom = self.CreateBlockFaceBottom(x, y, z, u0, u1, v0, v1)
            
        elif(blockFace == BlockFace.NORTH):
            faceGeom = self.CreateBlockFaceNorth(x, y, z, u0, u1, v0, v1)
            
        elif(blockFace == BlockFace.SOUTH):
            faceGeom = self.CreateBlockFaceSouth(x, y, z, u0, u1, v0, v1)
            
        elif(blockFace == BlockFace.WEST):
            faceGeom = self.CreateBlockFaceWest(x, y, z, u0, u1, v0, v1)
            
        elif(blockFace == BlockFace.EAST):
            faceGeom = self.CreateBlockFaceEast(x, y, z, u0, u1, v0, v1)
            
        #faceGeom = LightMaster.AddLightUVs(faceGeom, block)
        
        faceGeom.blockFace = blockFace
            
        return faceGeom
    
    def CreateBlockFaceTop(self, x, y, z, u0, u1, v0, v1):
        z += 1
        geom = BlockGeom()
        
        geom.vertex.append(VBase3(x, y, z))
        geom.normal.append(VBase3(0, 0, 1))
        geom.vertex.append(VBase3(x, y+1, z))
        geom.normal.append(VBase3(0, 0, 1))
        geom.vertex.append(VBase3(x+1, y+1, z))
        geom.normal.append(VBase3(0, 0, 1))
        geom.vertex.append(VBase3(x+1, y, z))
        geom.normal.append(VBase3(0, 0, 1))
        
        geom.texcoord.append(VBase2(u0, v0))
        geom.texcoord.append(VBase2(u0, v1))
        geom.texcoord.append(VBase2(u1, v1))
        geom.texcoord.append(VBase2(u1, v0))
    
        return geom
    
    def CreateBlockFaceBottom(self, x, y, z, u0, u1, v0, v1):
        geom = BlockGeom()
        
        geom.vertex.append(VBase3(x, y, z)) 
        geom.vertex.append(VBase3(x+1, y, z)) 
        geom.vertex.append(VBase3(x+1, y+1, z))
        geom.vertex.append(VBase3(x, y+1, z)) 
                             
        geom.normal.append(VBase3(0, 0, -1))
        geom.normal.append(VBase3(0, 0, -1))
        geom.normal.append(VBase3(0, 0, -1))
        geom.normal.append(VBase3(0, 0, -1))
        
        geom.texcoord.append(VBase2(u0, v0))
        geom.texcoord.append(VBase2(u0, v1))
        geom.texcoord.append(VBase2(u1, v1))
        geom.texcoord.append(VBase2(u1, v0))
        
        return geom
    
    def CreateBlockFaceNorth(self, x, y, z, u0, u1, v0, v1):
        y += 1
        geom = BlockGeom()
    
        geom.vertex.append(VBase3(x, y, z)) 
        geom.vertex.append(VBase3(x+1, y, z)) 
        geom.vertex.append(VBase3(x+1, y, z+1)) 
        geom.vertex.append(VBase3(x, y, z+1))
        
        geom.normal.append(VBase3(0, 1, 0))
        geom.normal.append(VBase3(0, 1, 0))
        geom.normal.append(VBase3(0, 1, 0))
        geom.normal.append(VBase3(0, 1, 0))
        
        geom.texcoord.append(VBase2(u1, v0))
        geom.texcoord.append(VBase2(u0, v0))
        geom.texcoord.append(VBase2(u0, v1))
        geom.texcoord.append(VBase2(u1, v1))
        #geom.texcoord.append(VBase2(u1, v0))
        
        return geom
    
    def CreateBlockFaceSouth(self, x, y, z, u0, u1, v0, v1):
        geom = BlockGeom()
        
        geom.vertex.append(VBase3(x, y, z))
        geom.vertex.append(VBase3(x, y, z+1)) 
        geom.vertex.append(VBase3(x+1, y, z+1)) 
        geom.vertex.append(VBase3(x+1, y, z)) 
        
        geom.normal.append(VBase3(0, -1, 0))
        geom.normal.append(VBase3(0, -1, 0))
        geom.normal.append(VBase3(0, -1, 0))
        geom.normal.append(VBase3(0, -1, 0))
        
        geom.texcoord.append(VBase2(u0, v0))
        geom.texcoord.append(VBase2(u0, v1))
        geom.texcoord.append(VBase2(u1, v1))
        geom.texcoord.append(VBase2(u1, v0))
        
        return geom
    
    def CreateBlockFaceWest(self, x, y, z, u0, u1, v0, v1):
        geom = BlockGeom()
         
        geom.vertex.append(VBase3(x, y, z)) 
        geom.vertex.append(VBase3(x, y+1, z)) 
        geom.vertex.append(VBase3(x, y+1, z+1)) 
        geom.vertex.append(VBase3(x, y, z+1)) 
        
        geom.normal.append(VBase3(-1, 0, 0))
        geom.normal.append(VBase3(-1, 0, 0))
        geom.normal.append(VBase3(-1, 0, 0))
        geom.normal.append(VBase3(-1, 0, 0))
        
        geom.texcoord.append(VBase2(u1, v0))
        geom.texcoord.append(VBase2(u0, v0))
        geom.texcoord.append(VBase2(u0, v1))
        geom.texcoord.append(VBase2(u1, v1))
        #geom.texcoord.append(VBase2(u1, v0))
        
        return geom
    
    def CreateBlockFaceEast(self, x, y, z, u0, u1, v0, v1):
        x += 1
        geom = BlockGeom()
        
        geom.vertex.append(VBase3(x, y, z))
        geom.vertex.append(VBase3(x, y, z+1)) 
        geom.vertex.append(VBase3(x, y+1, z+1)) 
        geom.vertex.append(VBase3(x, y+1, z)) 
        
        geom.normal.append(VBase3(1, 0, 0))
        geom.normal.append(VBase3(1, 0, 0))
        geom.normal.append(VBase3(1, 0, 0))
        geom.normal.append(VBase3(1, 0, 0))
        
        geom.texcoord.append(VBase2(u0, v0))
        geom.texcoord.append(VBase2(u0, v1))
        geom.texcoord.append(VBase2(u1, v1))
        geom.texcoord.append(VBase2(u1, v0))
        
        return geom