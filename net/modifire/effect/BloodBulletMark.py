
from pandac.PandaModules import Vec3

from environment.BlockGeometryGenerator import BlockGeometryGenerator
from particle.ParticleEmitter import ParticleEmitter

class BloodBulletMark():
    
    def __init__(self, location, normalVector, blockId):
        (u, v) = BlockGeometryGenerator.BlockIdToUV(0)
        
        ParticleEmitter(location = location, 
                             normalVector = normalVector, 
                             gravity = Vec3(0, 0, -17), 
                             numParticles = 3, 
                             particleScale = 0.08,
                             particleSpeed = 2, 
                             particleSpread = 2, 
                             particleLifetime = 0.4, 
                             textureFileLoc = 'Assets/Images/Textures/blocks.png', 
                             textureBlendType = None, 
                             texCoordU = u, 
                             texCoordV = v).Start()