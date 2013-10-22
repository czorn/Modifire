
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject

import Globals

from gui.GUIOrder import GUIOrder
from game.Game import Game

class RespawnCountdown(DirectObject):
    
    def __init__(self):
        self.node = aspect2d.attachNewNode('RespawnCountdown')
        self.node.setBin('fixed', GUIOrder.ORDER[GUIOrder.HUD_ITEM])
        self.node.hide()
        
        self.text = OnscreenText(text = 'Respawn in X...', scale = 0.11, fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1), mayChange = True, font = Globals.FONT_SAF)
        self.text.reparentTo(self.node)
        
    def Start(self):
        self.node.show()
        self.text.setText('Respawn in %s...' % (Game.RESPAWN_TIME))
        t = taskMgr.doMethodLater(1, self.Update, 'UpdateRespawnCountdown')
        t.i = Game.RESPAWN_TIME
        
    def Update(self, task):
        task.i -= 1
        
        if(task.i == 0):
            self.Stop()
            return task.done
        
        self.text.setText('Respawn in %s...' % (task.i))
        return task.again
        
    def Stop(self):
        self.node.hide()