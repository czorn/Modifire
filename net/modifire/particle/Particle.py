
from pandac.PandaModules import CardMaker
from pandac.PandaModules import Point2

class Particle():
    
    def __init__(self, direction, particleSpeed, gravity, particleLifetime, scale, texture, textureBlendType, texCoordU, texCoordV):
        self.direction = direction
        self.particleSpeed = particleSpeed
        self.gravity = gravity
        self.particleLifetime = particleLifetime
        self.scale = scale
        self.texture = texture
        self.textureBlendType = textureBlendType
        self.texCoordU = texCoordU
        self.texCoordV = texCoordV
        self.timeAlive = 0
        
        
        
        self.node = render.attachNewNode('Particle')
        cm = CardMaker('ParticleCard')
        cm.setUvRange(Point2(texCoordU[0], texCoordV[0]), Point2(texCoordU[1], texCoordV[1]))
        card = self.node.attachNewNode(cm.generate())
        #card.setPos(-self.scale / 2.0, 0, -self.scale / 2.0)
        card.setScale(self.scale)
        card.setTexture(self.texture)
        card.setLightOff()
        card.setBillboardPointEye()
        
    def Update(self, deltaTime):
        self.timeAlive += deltaTime
        if(self.timeAlive < self.particleLifetime):
            self.direction += self.gravity * deltaTime
            self.node.setPos(self.node.getPos() + self.direction * deltaTime)
            
    def SetPos(self, pos):
        self.node.setPos(pos)
            
    def CleanUp(self):
        self.node.removeNode()