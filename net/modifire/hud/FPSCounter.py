from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode
from direct.gui.OnscreenText import OnscreenText

import GameTime
from event.DebugEvent import ChunkTimeEvent, BandwidthInfoEvent

class FPSCounter(DirectObject):
    
    def __init__(self):
        
        self.node = base.a2dTopLeft.attachNewNode('Debug Info')
        self.node.setPos(0.03, 0, -0.15)
        
        self.fpsText =  OnscreenText(text = '', pos = (0, 0), scale = 0.06, fg = (1, 1, 1, 1), align = TextNode.ALeft, mayChange = True)
        self.fpsText.reparentTo(self.node)
        self.fps = 60
        self.lastTextUpdateTime = 0
        
        self.chunkText =  OnscreenText(text = '', pos = (0, -0.07), scale = 0.05, fg = (1, 1, 1, 1), align = TextNode.ALeft, mayChange = True)
        self.chunkText.reparentTo(self.node)
        
        self.bandwidthText = OnscreenText(text = '', pos = (0, -0.14), scale = 0.05, fg = (1, 1, 1, 1), align = TextNode.ALeft, mayChange = True)
        self.bandwidthText.reparentTo(self.node)
        
        self.accept(ChunkTimeEvent.EventName, self.UpdateChunkTime)
        self.accept(BandwidthInfoEvent.EventName, self.UpdateBandwidth)
        
    def Update(self):
        if(GameTime.deltaTime == 0):
            return
        
        self.fps += 0.1 * ((1.0 / GameTime.deltaTime) - self.fps) 
        
        if(GameTime.time - self.lastTextUpdateTime > 0.5):
            self.fpsText.setText('FPS: %s' % (str(int(self.fps))))
            self.lastTextUpdateTime = GameTime.time
            
    def UpdateChunkTime(self, event):
        self.chunkText.setText('Chunk: %s' % (str(event.GetTime())))
        
    def UpdateBandwidth(self, event):
        self.bandwidthText.setText('In: %s\nOut: %s' % (event.GetIncoming(), event.GetOutgoing()))
        
    def Destroy(self):  
        self.fpsText.removeNode()
        del self.fpsText
        self.chunkText.removeNode()
        del self.chunkText
        self.bandwidthText.removeNode()
        del self.bandwidthText
        self.ignoreAll()
        
        
        
    