

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from pandac.PandaModules import Vec3, DirectionalLight, AmbientLight, Vec4

import time
import random

from environment.BlockGeometryGenerator import BlockGeometryGenerator
from environment.Block import Block
  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        wp = WindowProperties()
        wp.setSize(850, 480)
        wp.setTitle("GAME")
        base.win.requestProperties(wp)
        
        bgg = BlockGeometryGenerator()
        
        blocks = []
        
        for x in xrange(1):
            for y in xrange(512):
                for z in xrange(64):
                    bid = random.randint(0, 255)
                    blocks.append(bid)
                    bgg.GenerateBlockGeometry(x, y, z, Block(bid), [0])
                    #blocks[x * 512 * 64 + y * 64 + z] = 1
            print x
            
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)

app = MyApp() 
app.run()
