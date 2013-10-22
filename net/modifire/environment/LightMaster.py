from pandac.PandaModules import  VBase2
from environment.BlockFace import BlockFace

class LightMaster():

    @staticmethod
    def AddLightUVs(geom, block):
        bid = block.light
        u0 = 0
        u1 = 1
        
        v1 = ((bid + 1) / 16.0)
        v0 = (1.0 * bid / 16.0)
        #print u0, u1, v0, v1
        
        geom.lighttex.append(VBase2(u0, v0))
        geom.lighttex.append(VBase2(u0, v1))
        geom.lighttex.append(VBase2(u1, v1))
        geom.lighttex.append(VBase2(u1, v0))
        
        return geom
    
    @staticmethod
    def SetLightValue(env, block):
    #    for i in xrange(7):
    #        adj = env.GetAdjacentBlock(block, BlockFace.TOP)
    #        if(adj.IsSolid()):
    #            break
    #        block.light = 15
    #        return None    
    #    if(not block.IsSolid()):
    #        print 'non solid with block above'
    #    adjacentLights = []
    #    
    #    for i in xrange(6):
    #        b = env.GetAdjacentBlock(block, i)
    #        adjacentLights.append(b.light)
    #    
    #    block.light = max(adjacentLights) - 1
        
        if(LightMaster.IsLightSource(env, block)):
            block.light = 15
            print 'light source', block.x, block.y, block.z
        else:
            adjacentLights = []
            
            for i in xrange(6):
                b = env.GetAdjacentBlock(block, i)
                adjacentLights.append(b.light)
            print adjacentLights
            block.light = max(adjacentLights) - 1
        block.light = 15
                    
    @staticmethod
    def IsLightSource(env, block):
        if(block.IsSolid()):
            return 0
        adj = block
        for i in xrange(7):
            adj = env.GetAdjacentBlock(adj, BlockFace.TOP)
            if(adj.IsSolid()):
                return 0
        return 1
