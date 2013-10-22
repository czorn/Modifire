from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties #@UnresolvedImport
from particle.ParticleEmitter import ParticleEmitter
from pandac.PandaModules import Vec3

  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        wp = WindowProperties()
        wp.setSize(850, 480)
        wp.setTitle("GAME")
        base.win.requestProperties(wp)
        
        self.bid = 1
        self.accept('a', self.Make)
        self.accept('s', self.Change)
    
    def Change(self):
        self.bid += 1
    
    def Make(self):
        bid = self.bid
        
        u0 = (bid % 16) / 16.0
        u1 = ((bid % 16) + 1) / 16.0
        
        v0 = 1 - ((bid / 16) + 1 / 16.0)
        v1 = 1 - ((bid / 16) / 16.0)
        
        self.pe = ParticleEmitter(location = Vec3(0, 5, 0), 
                             normalVector = Vec3(1, 0, 0), 
                             gravity = Vec3(0, 0, -30), 
                             numParticles = 3, 
                             particleSpeed = 20, 
                             particleSpread = 5, 
                             particleLifetime = 1, 
                             textureFileLoc = 'Assets/Images/Textures/blocks.png', 
                             textureBlendType = None, 
                             texCoordU = [u0, u1], 
                             texCoordV = [v0, v1])
        self.pe.Start()

app = MyApp() 
app.run()
