from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import GeomNode
from pandac.PandaModules import Vec3, DirectionalLight, AmbientLight, Vec4,Point3
from pandac.PandaModules import Fog
from direct.filter.CommonFilters import CommonFilters

from random import randint 
from environment.Block import Block
from environment.ChunkOfBlocks import ChunkOfBlocks
from environment.BlockFace import BlockFace
from Exceptions import *
import time
import copy
import Globals
import Settings
#from environment.EnvironmentLoader import EnvironmentLoader
#from environment.EnvironmentGenerator import EnvironmentGenerator
from event.ClientEvent import LoadProgressEvent

numTextures = 3 

class Environment(DirectObject):
        
    def __init__(self, blocks, mapInfo):        
        self.destroyedBlocks = []
        self.addedBlocks = []
        self.hasChanged = 0
        self.node = GeomNode('gnode') 
        self.chunks = [] 
        self.collisionGeom = 0
        self.blocks = blocks
        self.mapInfo = mapInfo   
        
        self.xmax = self.mapInfo.GetSize()[0]
        self.ymax = self.mapInfo.GetSize()[1]
        self.zmax = self.mapInfo.GetSize()[2]
        
        self.InitializeChunks()
                    
        terrain = render.attachNewNode(self.node) 
        #terrain.flattenStrong()
        #terrain.setRenderModeWireframe() 
        terrain.analyze()
        
        if(not Settings.IS_SERVER):
            self.SetupLights()
            
    def InitializeChunks(self):
        """ Builds the chunks for the first time."""
        numXChunks = self.xmax / ChunkOfBlocks.CHUNK_SIZE
        numYChunks = self.ymax / ChunkOfBlocks.CHUNK_SIZE
        numZChunks = self.zmax / ChunkOfBlocks.CHUNK_SIZE
        
        # Creating all of the chunks for the environment
        for x in xrange(numXChunks):
            rowOfGeoms = []
            for y in xrange(numYChunks): 
                colOfGeoms = []
                for z in xrange(numZChunks):
                    myChunk = ChunkOfBlocks(x, y, z, self, self.blocks, self.node, x * numYChunks * numZChunks + y * numZChunks + z)
                    colOfGeoms.append(myChunk)
                rowOfGeoms.append(colOfGeoms)
                LoadProgressEvent('Construct ALL the Geometry!', (1.0 * (x+1) / numXChunks)).Fire()
            self.chunks.append(rowOfGeoms)
            
        print self.xmax, ' x ', self.ymax, ' x ', self.zmax
        print self.node.getNumGeoms()
            
    def ClearBlockNotifications(self):
        """ Clears the list of recently added and removed blocks."""
        self.destroyedBlocks = []
        self.addedBlocks = []
        
    def HasChanged(self):
        """ Returns whether the environment has been changed by players since last checked."""
        if self.hasChanged:
            self.hasChanged = 0
            return True
        return False
         
    def Update(self):
        for row in self.chunks:
            for col in row:
                for chunk in col:
                    if(chunk.IsDirty()):
                        chunk.Update()
            
    def AreValidIndices(self, x, y, z):
        return not (x >= self.GetNumBlocksX() or y >= self.GetNumBlocksY() or z >= self.GetNumBlocksZ() or x < 0 or y < 0 or z < 0)      
    
    # Removes a block to the specified location. If we are connected
    # to a server and this is a prediction, we need to make
    # sure it gets verified by the server
    def DestroyBlock(self, x, y, z, firstTime = True):
        if(z == 0):
            return
        
        if(self.AreValidIndices(x, y, z)):
            oldId = copy.deepcopy(self.blocks[x][y][z].GetId())
            self.blocks[x][y][z].SetId(0)
            self.GetChunkFromBlockCoords(x, y, z).SetDirty(True)
            self.NotifyNeighborsToUpdate(x, y, z)
            self.hasChanged = True
            
            if(not Globals.OFFLINE and firstTime):
                if (x, y, z, oldId) not in self.destroyedBlocks:
                    self.destroyedBlocks.append((x, y, z, oldId))
                if(not Settings.IS_SERVER):
                    taskMgr.doMethodLater(1, self.CheckDestroyed, 'CheckDestroyed', extraArgs = [(x, y, z, oldId)])
        
    # Adds a block to the specified location. If we are connected
    # to a server and this is a prediction, we need to make
    # sure it gets verified by the server
    def AddBlock(self, x, y, z, bid, firstTime = True):
        if(self.AreValidIndices(x, y, z)):
            self.blocks[x][y][z].SetId(bid)
            self.GetChunkFromBlockCoords(x, y, z).SetDirty(True)
            self.NotifyNeighborsToUpdate(x, y, z)
            self.hasChanged = True
            
            if(not Globals.OFFLINE and firstTime):
                if (x, y, z, bid) not in self.addedBlocks:
                    self.addedBlocks.append((x, y, z, bid))
                if(not Settings.IS_SERVER):
                    taskMgr.doMethodLater(1, self.CheckPlaced, 'CheckPlaced', extraArgs = [(x, y, z, bid)])
        
    # When we add or remove a block, we need to notify it's neighbors
    # in case an adjacent block face needs to be drawn or removed
    def NotifyNeighborsToUpdate(self, x, y, z):
        for blockFace in xrange(6):
            (x1, y1, z1) = self.GetAdjacentBlockCoords(x, y, z, blockFace)
            c = self.GetChunkFromBlockCoords(x1, y1, z1)
            if(c):
                c.SetDirty(True)
     
    # If we predicted destroying a block, but the server
    # didn't verify it, replace it       
    def CheckDestroyed(self, myTuple):
        if(myTuple in self.destroyedBlocks):
            self.AddBlock(myTuple[0], myTuple[1], myTuple[2], myTuple[3], False)
    
    # If we predicted placing a block, but the server
    # didn't verify it, destroy it       
    def CheckPlaced(self, myTuple):
        if(myTuple in self.addedBlocks):
            self.DestroyBlock(myTuple[0], myTuple[1], myTuple[2], False)
            
    # When we receive an environment change from the server,
    # remove it from the list to be verified
    def Verified(self, myTuple):
        if myTuple in self.destroyedBlocks:
            self.destroyedBlocks.remove(myTuple)
            
        elif myTuple in self.addedBlocks:
            self.addedBlocks.remove(myTuple)
            
    def GetHighestBlock(self, x, y):
        z = 0
        while((self.AreValidIndices(x, y, z) and self.blocks[x][y][z].IsSolid())
              or (self.AreValidIndices(x, y, z+1) and self.blocks[x][y][z+1].IsSolid())):
            z += 1
            
        return Point3(x + 0.5, y + 0.5, z + 0.1)
        
    def SetupLights(self):
        a = 0.5
        d = 0.2
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor(Vec4(a, a, a, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)
        
        dir = [Vec3(1, 1, 1), Vec3(-1, -0.5, -1), Vec3(-0.5, -1, -1)]
        for i in xrange(3):
            directionalLight = DirectionalLight("directionalLight")
            directionalLight.setDirection(dir[i])
            directionalLight.setColor(Vec4(d, d, d, 1))
            render.setLight(render.attachNewNode(directionalLight))
        
        myFog = Fog("Fog Name")
        myFog.setColor(*Globals.SKY_COLOR)
        myFog.setLinearRange(40, 70)
        base.camera.attachNewNode(myFog)
        render.setFog(myFog)
        
        base.setBackgroundColor(*Globals.SKY_COLOR)
#        
    def GetBlocks(self):
        return self.blocks
    
    def GetAdjacentBlockCoords(self, x, y, z, blockFace):
        dx = 0
        dy = 0
        dz = 0 
        
        if(blockFace == BlockFace.TOP):
            dz = 1
        elif(blockFace == BlockFace.BOTTOM):
            dz = -1
            
        elif(blockFace == BlockFace.NORTH):
            dy = 1
        elif(blockFace == BlockFace.SOUTH):
            dy = -1
            
        elif(blockFace == BlockFace.WEST):
            dx = -1
        elif(blockFace == BlockFace.EAST):
            dx = 1
        else:
            raise InvalidBlockFaceException(blockFace)
            
        x += dx
        y += dy
        z += dz
        
        return (x, y, z)
    
    def GetAdjacentBlock(self, x, y, z, blockFace):
        """ Returns the block adjacent to the specified coordinates on the side of blockface."""
        (x, y, z) = self.GetAdjacentBlockCoords(x, y, z, blockFace)
        
        if(not self.AreValidIndices(x, y, z)):
            b = Block(0)
            return b
        else:
            return self.blocks[x][y][z]
    
    def GetChunk(self, x, y, z):
        return self.chunks[x][y][z]
    
    def GetChunkFromBlockCoords(self, x, y, z):
        if(self.AreValidIndices(x, y, z)):
            return self.chunks[x / ChunkOfBlocks.CHUNK_SIZE][y / ChunkOfBlocks.CHUNK_SIZE][z / ChunkOfBlocks.CHUNK_SIZE]
        else:
            return None
    
    @staticmethod
    def GetChunkSize():
        return ChunkOfBlocks.CHUNK_SIZE
    
    def GetNumBlocksX(self):
        return self.xmax
    
    def GetNumBlocksY(self):
        return self.ymax
    
    def GetNumBlocksZ(self):
        return self.zmax
        
    def GetDestroyedBlocks(self):
        """ Returns the blocks that have been destroyed by players."""
        return self.destroyedBlocks
        
    def GetAddedBlocks(self):
        """ Returns the blocks that have been added by players."""
        return self.addedBlocks
    
    def GetMapInfo(self):
        return self.mapInfo
        
    def Destroy(self):
        render.setLightOff()
        
    
    def AO(self):
        print self.xx['ns'], self.xx['r'], self.xx['a'], self.xx['s'], self.xx['f']
        self.filters.setAmbientOcclusion(numsamples = self.xx['ns'],
                                    radius = self.xx['r'],
                                    amount = self.xx['a'],
                                    strength = self.xx['s'],
                                    falloff = self.xx['f'])
        
  

            
            