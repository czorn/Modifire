from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import LerpFunc

import Settings
import Globals
from event.MenuEvent import MenuCloseEvent
from event.CameraEvent import ViewModeChangeEvent, ADSEvent
from event.WindowEvent import WindowFocusEvent
from panda3d.core import WindowProperties, Point2, Point3 #@UnresolvedImport

class Camera(DirectObject):
    
    FirstPersonMode = 0
    ThirdPersonMode = 1
    
    def __init__(self, parentNode):
        self.centerX = Settings.WIDTH / 2
        self.centerY = Settings.HEIGHT / 2
        self.parentNode = parentNode
        self.mode = 0
        self.windowIsFocused = True
        
        self.sensitivity = Settings.MOUSE_SENSITIVITY
        base.camera.reparentTo(parentNode)
        base.camLens.setFov(Globals.NORMAL_FOV)
        base.camLens.setNear(0.02)
        
        self.accept(MenuCloseEvent.EventName, self.OnMenuClosed)
        self.accept(WindowFocusEvent.EventName, self.OnWindowFocusEvent)
        self.accept(ADSEvent.EventName, self.OnADSEvent)
        
    def SetViewMode(self, mode):
        self.mode = (mode + 1) % 2
        self.ToggleViewMode()
        
    def ToggleViewMode(self):
        self.mode = (self.mode + 1) % 2
        
        # Mode 0 is First Person
        if(self.mode == Camera.FirstPersonMode):
            base.camera.setPos(0, 0, 0)
            
        # Mode 1 is Third Person
        elif(self.mode == Camera.ThirdPersonMode):
            base.camera.setPos(0, -5, 0)
            
        ViewModeChangeEvent(self.mode).Fire()
            
    def GetViewMode(self):
        return self.mode
        
    def Update(self):
        self.HandleFirstPersonLooking()
         
    # Rotate the camera based on the change in position of
    # the cursor since the last frame
    def HandleFirstPersonLooking(self):
        """ Typical First Person camera controls."""
        if (not self.windowIsFocused):
            return None
        
        x = self.GetX() 
        y = self.GetY() 
        deltaX = x - self.centerX
        deltaY = y - self.centerY
         
        newYaw = self.parentNode.getH() - 0.1* deltaX*self.sensitivity
        newPitch = self.parentNode.getP() - 0.09* deltaY*self.sensitivity
        
        if(newPitch > 89):
            newPitch = 89
        if(newPitch < -89):
            newPitch = -89
        self.parentNode.setH(newYaw)
        self.parentNode.setP(newPitch)
        
        base.win.movePointer(0, self.centerX, self.centerY)  
        
    def OnMenuClosed(self, menu):
        self.CenterCursor()      
        
    def CenterCursor(self):
        base.win.movePointer(0, self.centerX, self.centerY)
        
    def GetDirection(self):
        return self.parentNode.getNetTransform().getMat().getRow3(1)
    
    def GetX(self):
        if base.mouseWatcherNode.hasMouse():
            return base.win.getPointer(0).getX()
        else:
            return self.centerX
    
    def GetY(self):
        if base.mouseWatcherNode.hasMouse():
            return base.win.getPointer(0).getY()
        else:
            return self.centerY
        
    def ShowCursor(self):
        wp = WindowProperties()
        wp.setCursorHidden(False)
        base.win.requestProperties(wp)
        
    def HideCursor(self):
        wp = WindowProperties()
        wp.setCursorHidden(True)
        base.win.requestProperties(wp)
        
    def OnWindowResized(self):
        self.centerX = Settings.WIDTH / 2
        self.centerY = Settings.HEIGHT / 2
        
    # When the window is refocused, move the cursor to the center of the
    # screen
    def OnWindowFocusEvent(self, event):
        self.windowIsFocused = event.GetIsFocused()
        if(self.windowIsFocused):
            self.CenterCursor()

    # Lerps the Field of view from fov1 to fov2 over time from 0 -> 1
    # Lerps the Field of view from fov2 to fov1 over time from 1 -> 0 
    def LerpFOV(self, t, fov1, fov2):
        base.camLens.setFov(fov1 - (fov1 - fov2)*t)

    # Handles changes in aiming down the sight. If the player
    # is ADS, then we lerp the fov to simulate zooming in.
    def OnADSEvent(self, event):
        if(event.GetIsADS()):
            LerpFunc(self.LerpFOV, event.GetTime(), 0, 1, 'easeIn', [Globals.NORMAL_FOV, event.GetFOV()], "adsZoom").start()
            self.sensitivity = Settings.MOUSE_SENSITIVITY * event.GetMouseSpeedModifire()
        else:
            LerpFunc(self.LerpFOV, event.GetTime(), 1, 0, 'easeOut', [Globals.NORMAL_FOV, event.GetFOV()], "adsZoom").start()
            self.sensitivity = Settings.MOUSE_SENSITIVITY
        
    def Destroy(self):
        self.SetViewMode(Camera.FirstPersonMode)
        self.ignoreAll()
    
    # http://www.panda3d.org/forums/viewtopic.php?t=4130
    @staticmethod
    def Coord3dTo2d(nodePath): 
        coord3d = nodePath.getPos(base.cam) 
        coord2d = Point2() 
        base.camLens.project(coord3d, coord2d) 
        coordInRender2d = Point3(coord2d[0], 0, coord2d[1]) 
        coordInAspect2d = aspect2d.getRelativePoint(render2d, coordInRender2d) 
        return coordInAspect2d
        