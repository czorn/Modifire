
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Func

class BulletTracer():
    
    def __init__(self, start, end):
        model = loader.loadModel('Assets/Models/Effects/Tracer')
        print 'Loaded Assets/Models/Effects/Tracer'
        model.setScale(0.007, 2, 0.007)
        model.setPos(start)
        model.lookAt(end)
        model.reparentTo(render)
        model.setLightOff()
        
        Sequence(LerpPosInterval(model, 0.002 * (end-start).length(), end),
                 Func(self.CleanUp, model)).start()
        
        
    def CleanUp(self, model):
        model.removeNode()