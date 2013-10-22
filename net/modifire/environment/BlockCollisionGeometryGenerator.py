from pandac.PandaModules import CollisionPolygon, BitMask32, CollisionNode 

import Globals
from environment.BlockFace import BlockFace

# Creates the collision geometry for the Blocks

class BlockCollisionGeometryGenerator():
    
    
    # Given a list of face geometries,
    # returns a list of corresponding collision geometries
    @staticmethod
    def GenerateCollisionGeometry(geomFaces):
        collisionFaces = []
        
        for geomFace in geomFaces:
            tempVerts = list(geomFace.vertex)
            tempVerts.reverse()
            
            colPoly = CollisionPolygon(*tempVerts) 
            collision = CollisionNode('blockCollision')
            collision.addSolid(colPoly)
            collision.setFromCollideMask(BitMask32.allOff())
            
            if(geomFace.blockFace == BlockFace.TOP):
                collision.setIntoCollideMask(Globals.BLOCK_PICKER_BITMASK)
            else:
                collision.setIntoCollideMask(Globals.BLOCK_PICKER_BITMASK | Globals.WALL_BITMASK)
            
            collisionFaces.append(collision)
            
        return collisionFaces