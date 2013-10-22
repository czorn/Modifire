from pandac.PandaModules import GeomNode, GeomVertexData, GeomVertexFormat, Geom, NodePath
from pandac.PandaModules import GeomTriangles, GeomVertexWriter, Texture, TextureAttrib
from pandac.PandaModules import TextureStage, GeomVertexArrayFormat, InternalName
import time
from environment.BlockFace import BlockFace
from environment.BlockGeometryGenerator import BlockGeometryGenerator
from environment.BlockCollisionGeometryGenerator import BlockCollisionGeometryGenerator
from environment.LightMaster import LightMaster
from event.DebugEvent import ChunkTimeEvent
import Globals

def ThreadedUpdate(self, blocks, blockTexture, x, y, z):
    """ Creates new visible geometry and collision geometry
    for the chunk.
    
    This function is separate from the class because at one time
    I was trying to place this function in a true thread so the update
    was not noticeable to the player.
    """
    before = time.clock()
    
    geom = ChunkOfBlocks.CreateNewGeomDict(self)
    geom = ChunkOfBlocks.UpdateCollisionAndGeom(self, geom, blocks, x, y, z)
    self.ReplaceGeom(geom)
    
    after3 = time.clock()
    ChunkTimeEvent(int((after3 - before) * 1000)).Fire()

class ChunkOfBlocks():
    
    CHUNK_SIZE = 8      # The dimensions of the Chunk (The Chunk is CHUNK_SIZE by CHUNK_SIZE by CHUNK_SIZE)
    
    def __init__(self, x, y, z, environment, blocks, node, geomId):
        self.x = x
        self.y = y
        self.z = z
        self.environment = environment  # The environment object for the world
        self.blocks = blocks            # The 3D array of Block objects
        self.geom = 0                   # A dict used to hold all of the data for geometry creation
        self.node = node                # The parent node of the geometry
        self.geomId = geomId            # The id of the geometry wrt the parent (needed for updating the geometry)
        self.dirty = 0                  # A flag for whether the Chunk needs updating
        self.wallCollisionGeom = 0      # The Collision Geometry players can walk into (currently not in use)
        self.floorCollisionGeom = 0     # The Collision Geometry players can stand on (currently not in use)
        self.geomGen = BlockGeometryGenerator()
        
        self.blockTexture = loader.loadTexture('Assets/Images/Textures/blocks.png')
        self.lightMapTexture = loader.loadTexture('Assets/Images/Textures/lightMap.png')
        
        self.CreateVertexFormat()
        self.geom = self.CreateNewGeomDict()
        self.UpdateCollisionAndGeom(self.geom, blocks, x, y, z)
        self.AddGeom()
        
    def Update(self):
        """ Recreates the Chunk."""
        ThreadedUpdate(self, self.blocks, self.blockTexture, self.x, self.y, self.z)
        self.dirty = 0    
        
    def AddGeom(self):
        """ Adds the geom data to the parent node so that it can be rendered."""
        self.node.addGeom(self.geom['geom']) 
        self.SetGeomTexture()
        
    def ReplaceGeom(self, geom):
        """ Replaces the current visible geometry with the 
        geometry described in 'geom'.
        """
        self.geom = geom
        self.node.setGeom(self.geomId, geom['geom']) 
        self.SetGeomTexture()
        
    def SetGeomTexture(self):
        """ Applies the texture to the visible geometry of the Chunk."""
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MDecal)
        ts.setTexcoordName('light')

        # Setup the block texture
        attrib = TextureAttrib.make(self.GetTexture())
        
        # Add the light overlay
        #attrib = attrib.addOnStage(ts, geom['lighttexture'])
        
        # Apply the texture to the node
        self.node.setGeomState(self.geomId, 
                               self.node.getGeomState(self.geomId).addAttrib(attrib))
        
    def UpdateLighting(self, block):
        """ Determines the proper light value for the block."""
        LightMaster.SetLightValue(self.environment, block) 
    
    def CreateNewGeomDict(self):
        """ Creates all of the Geometry data structures needed
        to create the visible block geometry.
        """
        gvd = GeomVertexData('chunk', self.geomVertexFormat, Geom.UHStatic) #GeomVertexFormat.getV3n3t2()
        geom = Geom(gvd) 
        prim = GeomTriangles(Geom.UHStatic) 
        vertex = GeomVertexWriter(gvd, 'vertex') 
        texcoord = GeomVertexWriter(gvd, 'texcoord') 
        lighttex = GeomVertexWriter(gvd, 'texcoord.light')
        normal = GeomVertexWriter(gvd, 'normal')
        tex = self.blockTexture 
        tex.setMagfilter(Texture.FTNearest) 
        tex.setMinfilter(Texture.FTNearest) 
        lighttexture = self.lightMapTexture 
        lighttexture.setMagfilter(Texture.FTNearest) 
        lighttexture.setMinfilter(Texture.FTLinearMipmapLinear) 
        geom = {'geom':geom, 
                      'prim':prim, 
                      'normal':normal,
                      'vertex':vertex, 
                      'texcoord':texcoord, 
                      'lighttex':lighttex, 
                      'index':0, 
                      'gvd':gvd, 
                      'lighttexture':lighttexture,
                      'texture':tex}
        
        return geom
        
    def UpdateCollisionAndGeom(self, geom, blocks, x, y, z):
        """ Creates the visible Geometry for the block as well as 
        its Collision Geometry. Returns the geometry data.
        
        @param geom:       The empty dict for the geometry data
        @param blocks:     The 3D array of Block objects for the environment
        @param x, y, z:    The starting coordinates of this geometry in global space
        """ 
        
        # Remove the old collision geometries (since we're updating, chances
        # are that they have changed)
        if(self.wallCollisionGeom):
            self.wallCollisionGeom.removeNode()
        if(self.floorCollisionGeom):
            self.floorCollisionGeom.removeNode()
            
        # Create the new wall and floor geometries
        wallCollisionGeom = NodePath('wallCollisionGeom') 
        wallCollisionGeom.reparentTo(render)
        floorCollisionGeom = NodePath('floorCollisionGeom') 
        floorCollisionGeom.reparentTo(render)
        
        # For each bock, if the block has geometry,
        # add it to the chunks geometry
        for x1 in xrange(ChunkOfBlocks.CHUNK_SIZE): 
            for y1 in xrange(ChunkOfBlocks.CHUNK_SIZE):
                for z1 in xrange(ChunkOfBlocks.CHUNK_SIZE):
                    
                    x2 = x * ChunkOfBlocks.CHUNK_SIZE + x1
                    y2 = y * ChunkOfBlocks.CHUNK_SIZE + y1
                    z2 = z * ChunkOfBlocks.CHUNK_SIZE + z1
                    
                    #print x, y, z, x1, y1, z1, x2, y2, z2
                    b = blocks[x2][y2][z2]
                    b.SetParentChunk(self)
                    
                    ## self.UpdateLighting(b)
                    
                    # Look to adjacent blocks to figure out which BlockFaces of the current
                    # block need to be rendered
                    if(b.IsSolid()):
                        facesToDraw = []
                        for blockSide in xrange(6):
                            adjacent = self.environment.GetAdjacentBlock(x2, y2, z2, blockSide)
                            if(not adjacent.IsSolid()):         # If any blockfaces are adjacent to air, 
                                facesToDraw.append(blockSide)   # they need to be drawn
                                
                        # Create the visible geometry and the collision geometry for each face of this block
                        geomFaces = self.geomGen.GenerateBlockGeometry(x2, y2, z2, b, facesToDraw)
                        collisionFaces = BlockCollisionGeometryGenerator.GenerateCollisionGeometry(geomFaces)
                        
                        # For every drawn face of the block, we need to contain all of
                        # geometry data in a primitive
                        for k in xrange(len(geomFaces)):
                            geomFace = geomFaces[k]
                            
                            # For every vertex on a face, add the data to the geom dict             
                            for index in xrange(0, len(geomFace.vertex)):
                                geom['vertex'].addData3f(geomFace.vertex[index])
                                geom['texcoord'].addData2f(geomFace.texcoord[index])
                                #geom['lighttex'].addData2f(geomFace.lighttex[index])
                                geom['normal'].addData3f(geomFace.normal[index])
                            
                            i = geom['index'] 
                            d = i * (3 + 1) 
                            geom['prim'].addVertices(d, d + 2, d + 1) 
                            geom['prim'].addVertices(d, d + 3, d + 2) 
                            geom['index'] += 1 
                            
                            # FIX ME - K DOES NOT CORRESPOND DIRECTLY TO THE BLOCK FACE
#                            if(k == BlockFace.TOP or k == BlockFace.BOTTOM):
#                                floorCollisionGeom.attachNewNode(collisionFaces[k])
#                            else:
#                                wallCollisionGeom.attachNewNode(collisionFaces[k])
                            
                            wallCollisionGeom.attachNewNode(collisionFaces[k])
                            
                            NodePath(collisionFaces[k]).setPythonTag(Globals.TAG_COLLISION, Globals.COLLISION_BLOCK)
                            NodePath(collisionFaces[k]).setPythonTag(Globals.TAG_BLOCK, b)
                            
        # Close the geometry and add it to the node
        geom['prim'].closePrimitive() 
        geom['geom'].addPrimitive(geom['prim']) 
        self.floorCollisionGeom = floorCollisionGeom
        self.wallCollisionGeom = wallCollisionGeom
        
        return geom
    
    def CreateVertexFormat(self):
        """ Creates a custom vertex format. 
        
        This was needed so that I could add a second array of texture data for having
        multiple textures for a BlockFace
        """
    
        array = GeomVertexArrayFormat()
        array.addColumn(InternalName.make('vertex'), 3,
                        Geom.NTFloat32, Geom.CPoint)
        array.addColumn(InternalName.make('normal'), 3,
                        Geom.NTFloat32, Geom.CVector)
        array.addColumn(InternalName.make('texcoord'), 2,
                Geom.NTFloat32, Geom.CTexcoord)
        array.addColumn(InternalName.make('texcoord.light'), 2,
                Geom.NTFloat32, Geom.CTexcoord)
        gvformat = GeomVertexFormat()
        gvformat.addArray(array)
        gvformat = GeomVertexFormat.registerFormat(gvformat)
        self.geomVertexFormat = gvformat
        
    def IsDirty(self):
        """ Returns whether the chunk has been flagged as needing an update."""
        return self.dirty
    
    def SetDirty(self, value):
        """ Sets the dirty flag of the Chunk to 'value'."""
        self.dirty = value
        
    def GetTexture(self):
        """ Returns the texture object used for Blocks."""
        return self.geom['texture']
        