import Globals
from pandac.PandaModules import PerlinNoise2
from environment.Block import Block
from event.ClientEvent import LoadProgressEvent


class EnvironmentGenerator():
    
    def __init__(self):
        self.seed = 0
        self.usePerlin = False
        self.height = 12
        
    def SetUsePerlin(self, val):
        self.usePerlin = val
        
    def SetHeight(self, val):
        self.height = val
        
    def SetSeed(self, value):
        if(isinstance(value, str)):
            sum1 = 0
            for c in value:
                sum1 += ord(c)
            self.seed = sum1
        else:
            self.seed = value
        
    def GetHeight(self, midZ, dz, x, y):
        """" Returns the height of the top layer of the
        ground for the x, y, column.
        """
        
        #return 10
        if(self.usePerlin):
            return midZ + dz * self.pn(x/50.0, y/50.0)
        else:
            return self.height
    
    def GenerateNewEnvironment(self, xmax, ymax, zmax):
        """ Fills and returns a 3D array of block objects that
        represents the environment.
        """
        self.SetSeed(Globals.WORLD_SEED)
        self.pn = PerlinNoise2(1, 1, 256, self.seed)
        
        # Create ALL the blocks!
        blocks = []
        for x in xrange(0, xmax):
            row = []
            for y in xrange(0, ymax):
                col = []
                for z in xrange(0, zmax):
                    
                    # Determine the id of the block. 'h' is the height of the ground for
                    # the x-y column. If this block is below 'h', it is one of two dirt
                    # blocks, otherwise it is air.
                    h = self.GetHeight(self.height, self.height / 3 * 2, x, y)
                    if(z <= h):
                        if(z <= h - 1):
                            bid = 1
                        else:
                            bid = 2
                    else:
                        bid = 0
                        
                    col.append(bid)
                row.append(col)
            blocks.append(row)
            LoadProgressEvent('Generate ALL the blocks!', (1.0 * (x+1) / xmax)).Fire()
            
        return blocks
        