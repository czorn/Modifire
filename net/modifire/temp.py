import sys 
from pandac.PandaModules import loadPrcFileData 
loadPrcFileData("", "win-size 500 500") 
import direct.directbase.DirectStart 
from direct.task import Task 
from pandac.PandaModules import * 

props = WindowProperties() 
props.setCursorHidden(True) 
props.setMouseMode(WindowProperties.MRelative) 
base.disableMouse() 
base.win.requestProperties(props) 
p = loader.loadModel("smiley") 
p.reparentTo(render) 
camera.setPos(0, 0, 200) 
camera.lookAt(p) 
base.oldx = 0 
base.oldy = 0 

def movepointer(task): 
    md = base.win.getPointer(0) 
    x = md.getX() 
    y = md.getY() 
    if x != base.oldx or y != base.oldy: 
        print -1 *(base.oldx - x), base.oldy - y 
        p.setX(p, (-0.1 *(base.oldx - x))) 
        p.setY(p, (base.oldy - y)*0.1) 
    base.oldx = x 
    base.oldy = y 
    return Task.cont 

taskMgr.add(movepointer, "foobar") 
base.accept("f1", p.setPos, [0, 0, 0]) 
base.accept("escape", sys.exit) 
run() 