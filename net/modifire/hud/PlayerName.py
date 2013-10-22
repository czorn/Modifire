
from direct.interval.IntervalGlobal import LerpColorScaleInterval, Sequence, Func
from panda3d.core import Vec4 #@UnresolvedImport
from pandac.PandaModules import TextNode

import Globals
import Settings

from Camera import Camera

class PlayerName():
    
    def __init__(self, name, parentNode):
        self.parentNode = parentNode
        
        self.nameTextNode = TextNode('nameTextNode')
        self.nameTextNode.setText(name)
        self.nameTextNode.setTextColor(Globals.COLOR_WHITE)
        self.nameTextNode.setShadow(0.05, 0.05)
        self.nameTextNode.setShadowColor(Globals.COLOR_WHITE)
        self.nameTextNode.set_align(TextNode.ACenter)
        self.nameTextNodeTextPath = aspect2d.attachNewNode(self.nameTextNode)
        self.nameTextNodeTextPath.setScale(Settings.CHAT_HEIGHT)
        
        self.hidden = True
        self.nameTextNodeTextPath.hide()
        self.fadeSeq = Sequence(LerpColorScaleInterval(self.nameTextNodeTextPath, 1, Globals.COLOR_TRANSPARENT),
                                Func(self.nameTextNodeTextPath.hide))
        
        self.reshowOnInView = False
    
    def SetColor(self, color):
        self.nameTextNode.setTextColor(color)
    
    def IsHidden(self):
        return self.hidden
    
    def FadeOut(self):
        #print 'fo'
        if(not self.IsHidden()):
            #print 'really fo'
            self.hidden = True
            self.fadeSeq.start()
            
    def Hide(self):
        self.nameTextNodeTextPath.hide()
        self.hidden = True
    
    def Show(self):
        if(self.IsHidden()):
            if(self.fadeSeq.isPlaying()):
                self.fadeSeq.finish()
                
            self.nameTextNodeTextPath.show()
            self.nameTextNodeTextPath.setColorScale(Globals.COLOR_WHITE)
            self.hidden = False
            #print 'really show'
            
        
    def Update(self):
        self.nameTextNodeTextPath.setPos(Camera.Coord3dTo2d(self.parentNode))
             
        # If the node is visible
        if(base.camNode.isInView(self.parentNode.getPos(base.cam))):
            if(self.IsHidden() and self.reshowOnInView):
                self.Show()
        else:
            if(not self.IsHidden()):
                self.Hide()
                
                
                
                
                
                