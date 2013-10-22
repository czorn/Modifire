
import random

from particle.Particle import Particle
from pandac.PandaModules import Vec3, Texture

import GameTime

class ParticleEmitter():
    
    def __init__(self, location, normalVector, gravity, numParticles, particleScale, particleSpeed, particleSpread, particleLifetime, textureFileLoc, textureBlendType, texCoordU = [0, 1], texCoordV = [0, 1]):
        self.location = location
        self.normalVector = normalVector
        self.gravity = gravity
        self.numParticles = numParticles
        self.particleScale = particleScale
        self.particleSpeed = particleSpeed
        self.particleSpread = particleSpread
        self.particleLifetime = particleLifetime
        self.textureBlendType = textureBlendType
        self.texCoordU = texCoordU
        self.texCoordV = texCoordV
        self.particles = []
        self.texture = loader.loadTexture(textureFileLoc)
        self.texture.setMagfilter(Texture.FTNearest) 
        self.texture.setMinfilter(Texture.FTNearest) 
        self.timeAlive = 0
        
    def Start(self):
        for i in xrange(self.numParticles):
            direct = self.normalVector * self.particleSpeed + Vec3(random.random() * self.particleSpread, random.random() * self.particleSpread, random.random() * self.particleSpread)
            p = Particle(direction = direct, 
                         particleSpeed = self.particleSpeed, 
                         gravity = self.gravity, 
                         particleLifetime = self.particleLifetime, 
                         scale = self.particleScale,
                         texture = self.texture, 
                         textureBlendType = self.textureBlendType, 
                         texCoordU = self.texCoordU, 
                         texCoordV = self.texCoordV)
            p.SetPos(self.location)
            self.particles.append(p)
            
        #taskMgr.doMethodLater(self.particleLifetime, self.Finish, 'Finish Particles')
        taskMgr.add(self.Update, 'ParticleEmitterUpdate_%s' % (str(self)))
        
    def SetLocation(self, pos):
        self.location = pos
            
    def Update(self, task):
        dt = GameTime.deltaTime
        self.timeAlive += dt
        if(self.timeAlive > self.particleLifetime):
            self.Finish()
            return task.done
        
        for p in self.particles:
            p.Update(dt)
        
        return task.cont
            
    def Finish(self, task = None):
        for p in self.particles:
            p.CleanUp()
        self.particles = []