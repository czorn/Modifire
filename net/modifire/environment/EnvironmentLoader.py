import os, errno, shutil
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib

from environment.EnvironmentGenerator import EnvironmentGenerator
from environment.Block import Block
from environment.ChunkOfBlocks import ChunkOfBlocks
from environment.MapInfo import MapInfo
from environment.Environment import Environment
from event.ClientEvent import LoadProgressEvent
import Globals
import Settings
import time
import struct

class EnvironmentLoader():
    """ Loads an environment into the game."""
    
    def __init__(self):
        self.envGen = EnvironmentGenerator()    # Used to create a new environment
        self.SetupDirectories()
        self.isSaving = False
        
        self.saveImage = OnscreenImage(image = 'Assets/Images/HUD/Save.png', scale = 128.0 / 1024, pos = (0.8, 0, -0.85))
        self.saveImage.setTransparency(TransparencyAttrib.MAlpha)
        self.saveImage.reparentTo(aspect2d)
        self.saveImage.hide()
        
        taskMgr.setupTaskChain('EnvironmentSave', numThreads = 1,
                       frameSync = False)
        
    def SetupDirectories(self):
        """ Creates the necessary directories for saving
        and loading environments.
        """
        self.MkDir('Assets')
        self.MkDir('Assets/OfflineLevels')
        self.MkDir('Assets/ServerLevels')
    
    def MkDir(self, dirName):
        """ Creates the specified directory.""" 
        try:
            os.makedirs(dirName)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
    
    def HasFile(self, filename):
        """ Returns whether the file exists in the current directory."""
        if(Settings.IS_SERVER):
            filename = 'Assets/ServerLevels/%s' % (filename)
            return os.path.exists(filename)
        else:
            filename = 'Assets/OfflineLevels/%s' % (filename)
            return os.path.exists(filename)
    
    def ImportToLocation(self, filename, blocks, xOff, yOff, zOff):
        """ Imports an environment into the current environment at
        the specified location.
        """
        importedBlocks = self.LoadEnvironment(filename)
        
        x1 = len(importedBlocks) 
        y1 = len(importedBlocks[0])
        z1 = len(importedBlocks[0][0])
        
        for x in xrange(x1):
            for y in xrange(y1):
                for z in xrange(z1):
                    blocks[x + xOff][y + yOff][z + zOff].id = importedBlocks[x][y][z].id
        
        return blocks
    
    def LoadEnvironmentFromServer(self, blockIds, mapInfo):
        blocks = self.CreateBlockArray(blockIds)
        return Environment(blocks, mapInfo)
    
    def LoadEnvironment(self, mapName):
        """ Loads the environment from a file if it exists. Generates a new
        environment otherwise"""
        mapInfo = None
        blockIds = None
        print 'Loading Environment', mapName
        
        # Look for a recent, edited version of the file
        if(self.HasFile('%s.map' % (mapName))):
            (mapInfo, blockIds) = self.OpenMapFile('%s.map' % (mapName))
            
        # If its not there, look for a prebuilt version
        elif(self.HasFile('%s.mapc' % (mapName))):
            (mapInfo, blockIds) = self.OpenMapFile('%s.mapc' % (mapName))
        
        if(not blockIds):
            xmax = Globals.ENV_LOAD_ARGS[0]
            ymax = Globals.ENV_LOAD_ARGS[1]
            self.envGen.SetUsePerlin(Globals.ENV_LOAD_ARGS[2])
            self.envGen.SetHeight(Globals.ENV_LOAD_ARGS[4])
            blockIds = self.envGen.GenerateNewEnvironment(xmax, ymax, 48)
            mapInfo = MapInfo('Unknown', [xmax, ymax, 48], {}, {})
            
        blocks = self.CreateBlockArray(blockIds)
        return Environment(blocks, mapInfo)        
        
    def CreateBlockArray(self, blockIds):   
        xmax = len(blockIds)
        ymax = len(blockIds[0])
        zmax = len(blockIds[0][0])
        
        blocks = []
        for x in xrange(xmax):
            row = []
            for y in xrange(ymax):
                col = []
                for z in xrange(zmax):
                    col.append(Block(blockIds[x][y][z]))
                row.append(col)
            LoadProgressEvent('Build ALL the Blocks!', 1.0 * x / xmax).Fire()
            blocks.append(row)
            
        return blocks
        
    @staticmethod
    def Blocks1Dto3D(blocks1D, numBlocksX, numBlocksY, numBlocksZ):
        blocks = []
        
        i = 0
        for x in xrange(numBlocksX):
            rows = []
            for y in xrange(numBlocksY):
                cols = []
                for z in xrange(numBlocksZ):
                    cols.append(blocks1D[i])
                    i += 1
                rows.append(cols)
            LoadProgressEvent('Convert ALL the Data Structures!', 1).Fire()
            blocks.append(rows)
                   
        return blocks
    
    def ReadHeading(self, FILE):
        # Heading for maps:
        # @author = name 
        # @size = x, y, z
        # @spawn1 = x, y, z, w, d, h
        # @spawn2 = x, y, z, w, d, h
            
        (ignore1, ignore2, data) = FILE.readline().partition("=")
        author = data.strip()
        
        (ignore1, ignore2, data) = FILE.readline().partition("=")
        (xmax, ymax, zmax) = data.strip().split()
        
        (ignore1, ignore2, data) = FILE.readline().partition("=")
        (x, y, z, w, d, h) = data.strip().split()
        spawn1 = {'x':x, 'y':y, 'z':z, 'w':w, 'd':d, 'h':h}
        
        (ignore1, ignore2, data) = FILE.readline().partition("=")
        (x, y, z, w, d, h) = data.strip().split()
        
        spawn2 = {'x':x, 'y':y, 'z':z, 'w':w, 'd':d, 'h':h}
        
        return MapInfo(author, [int(xmax), int(ymax), int(zmax)], spawn1, spawn2)
        
    def WriteHeading(self, FILE, mapInfo):
        FILE.write('@author = %s\n' % mapInfo.GetAuthor())
        size = mapInfo.GetSize()
        FILE.write('@size = %s %s %s\n' % (size[0], size[1], size[2]))
        FILE.write('@spawn1 = 0 0 0 0 0 0\n')
        FILE.write('@spawn2 = 0 0 0 0 0 0\n')
        
    def OpenMapFile(self, mapFilename):
        """ Opens the environment from a file."""
        
        if(Settings.IS_SERVER):
            FILE = open('Assets/ServerLevels/%s' % (mapFilename), "r")
        else:
            FILE = open('Assets/OfflineLevels/%s' % (mapFilename), "r")
            
        mapInfo = self.ReadHeading(FILE)
        size = mapInfo.GetSize()
        xmax = size[0]
        ymax = size[1]
        zmax = size[2]
        
        blocks = []
        for x in xrange(xmax):
            for y in xrange(ymax):
                for z in xrange(zmax):
                    blocks.append(int(FILE.readline().strip()))
        FILE.close()
        blockIds = EnvironmentLoader.Blocks1Dto3D(blocks, xmax, ymax, zmax)
        
        return (mapInfo, blockIds)
        
    def OpenImage(self):
        FILE = open('dust2.bmp')
        for j in xrange(18):
            FILE.read(3)
        
        heights = []
        for i in xrange(128):
            rows = []
            for j in xrange(128):
                pixel = FILE.read(3)
                h = round(100.0 * struct.unpack('B', pixel[0][0])[0] / 255)
                rows.append(h)
            heights.append(rows)
        FILE.close()
        
        blocks = []
        numBlocksX = Environment.GetNumBlocksX()
        numBlocksY = Environment.GetNumBlocksY()
        numBlocksZ = Environment.GetNumBlocksZ()
        
        i = 0
        for x in xrange(numBlocksX):
            rows = []
            for y in xrange(numBlocksY):
                cols = []
                for z in xrange(numBlocksZ):
                    if(z == heights[y][x]):
                        cols.append(5)
                    if(z < heights[y][x]):
                        cols.append(6)
                    else:
                        cols.append(0)
                    i += 1
                rows.append(cols)
            LoadProgressEvent('de ALL the dust2!', 1).Fire()
            blocks.append(rows)
            
        Globals.BLOCKS = blocks
        
    def SaveEnvironment(self, environment):
        """ Saves the current environment to a file."""
        
        if(self.isSaving):
            return
        
        if(self.HasFile('%s.map' % (Settings.LAST_WORLD))):
            if(Settings.IS_SERVER):
                shutil.copyfile('Assets/ServerLevels/%s.map' % (Settings.LAST_WORLD), 'Assets/ServerLevels/%s.map.bak' % (Settings.LAST_WORLD))
            else:
                shutil.copyfile('Assets/OfflineLevels/%s.map' % (Settings.LAST_WORLD), 'Assets/OfflineLevels/%s.map.bak' % (Settings.LAST_WORLD))
        
        if(Settings.IS_SERVER):
            FILE = open('Assets/ServerLevels/%s.map' % (Settings.LAST_WORLD),"w")
        else:
            FILE = open('Assets/OfflineLevels/%s.map' % (Settings.LAST_WORLD),"w")
            
        mapInfo = environment.GetMapInfo()
        self.WriteHeading(FILE, mapInfo)
        
        saveTask = taskMgr.add(self.SaveTask, 'SaveTask', taskChain = 'RUDP_Heartbeat')
        saveTask.x = 0
        saveTask.y = 0
        saveTask.z = 0
        saveTask.FILE = FILE
        saveTask.blocks = environment.GetBlocks()
        saveTask.numBlocksX = mapInfo.GetSize()[0]
        saveTask.numBlocksY = mapInfo.GetSize()[1]
        saveTask.numBlocksZ = mapInfo.GetSize()[2]
        self.isSaving = True
        self.saveImage.show()
        
        print 'Starting save task', Settings.LAST_WORLD
        
    def SaveTask(self, task):
        for i in xrange(2048):
            task.FILE.write("%i\n" % (task.blocks[task.x][task.y][task.z].GetId()))
            i += 1
            
            task.z = (task.z + 1) % task.numBlocksZ
            if(task.z == 0):
                task.y = (task.y + 1) % task.numBlocksY
                if(task.y == 0):
                    task.x = (task.x + 1) % task.numBlocksX
                    
            if(task.x == 0 and task.y == 0 and task.z == 0):
                task.FILE.close()
                self.isSaving = False
                print 'done saving', time.time()
                self.saveImage.hide()
                return task.done
        return task.cont
        
    @staticmethod
    def FindExistingWorlds():
        worlds = []
        for world in os.listdir('Assets/OfflineLevels'):
            world = world.split('.')[0]
            if(world not in worlds):
                worlds.append(world)
        print worlds
        return worlds
         
        
