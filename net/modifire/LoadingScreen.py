from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject

from event.ClientEvent import LoadProgressEvent, EngineLoadedEvent

class LoadingScreen(DirectObject):

    def __init__(self):
        self.node = base.aspect2d.attachNewNode('loadingScreen')
        self.loadText = "Loading"
        self.textObject = OnscreenText(text = self.loadText, pos = (0, 0, -0.5), scale = 0.09, fg = (1, 1, 1, 1))
        self.textObject.reparentTo(self.node)
        self.bar = DirectWaitBar(text = "", value = 50, pos = (0,.4,.4))
        self.bar.reparentTo(self.node)
        
        self.accept(LoadProgressEvent.EventName, self.OnLoadProgressEvent)
        self.acceptOnce(EngineLoadedEvent.EventName, self.Destroy)
        
    def OnLoadProgressEvent(self, event):
        self.Progress(event.GetText(), event.GetValue())
        
    def Progress(self, text, val):
        self.textObject.setText(text)
        val1 = val * 100
        self.bar['value'] = val1
        base.graphicsEngine.renderFrame()
            
    def Destroy(self, event = None):
        self.textObject.destroy()
        self.node.removeNode()
        self.bar.destroy()
        self.ignoreAll()
        print 'destroyed loadingscreen'