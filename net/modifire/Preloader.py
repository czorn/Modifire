import os
from direct.gui.OnscreenImage import OnscreenImage
from mydirect.showbase import Audio3DManager

import Globals

# Loads models and textures into memory so the game doesn't hang while playing

class Preloader():
    
    @staticmethod
    def Preload():
        loader.loadModel('Assets/Models/Items/SMGAuto')
        loader.loadModel('Assets/Models/Items/RifleAuto')
        loader.loadModel('Assets/Models/Items/SniperBolt')
        loader.loadModel('Assets/Models/Players/ralph')
        
        currentDir = os.getcwd()
    
        for root, dirs, files in os.walk(currentDir):
            for f in files:
                if f.endswith('.png'):
                    i = root.find('Assets')
                    s = '%s/%s' % (root[i:].replace('\\', '/'), f)
                    #loader.loadTexture(s)
                    x = OnscreenImage(image = s)
                    x.reparentTo(render)
                    x.destroy()
                    print 'Loaded', s
                    
        Globals.FONT_SAF = loader.loadFont('Assets/Fonts/SAF.otf')
        Globals.FONT_SAF.setPixelsPerUnit(60)
        print 'Loaded Assets/Fonts/SAF.otf'
        
        Globals.AUDIO_3D = Audio3DManager.Audio3DManager(base.sfxManagerList[0], base.camera)
        Globals.AUDIO_3D.setDistanceFactor(15.0)
        
        Globals.LoadRocket()
                    