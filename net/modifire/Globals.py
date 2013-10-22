from pandac.PandaModules import BitMask32
from panda3d.rocket import RocketRegion, RocketInputHandler, LoadFontFace
from panda3d.core import Vec3, Vec4 #@UnresolvedImport

import Settings

VERSION = '0.11a Alpha'

UP_VECTOR = Vec3(0, 0, 1)
OFFLINE = True
GRAVITY = -17
FIXED_UPDATE_DELTA_TIME = 0.015
MAX_SELECT_DISTANCE = 5
WORLD_SEED = 0
MY_PID = -1
MY_TEAM = -1
BLOCKS = None
SKY_COLOR = (0.4, 0.8, 1)
ENV_LOAD_ARGS = [48, 48, True, 16]              # Parameters for level generation 

# Collision Tags
(TAG_COLLISION,
 TAG_PLAYER,
 TAG_BLOCK) = [str(x) for x in range(3)]

(COLLISION_LEG,
 COLLISION_BODY,
 COLLISION_HEAD,
 COLLISION_BLOCK) = range(4)

TIME_STAMP = 0
DEBUG_CSP = False

(
GLOBAL_CHAT,
TEAM_CHAT
) = range(2)

# Collision Bitmasks
BLOCK_PICKER_BITMASK = BitMask32.bit(1)
ITEM_BITMASK = BitMask32.bit(2)
WALL_BITMASK = BitMask32.bit(3)
PLAYER_BITMASK = BitMask32.bit(4)

PORT_SERVER_LISTENER = 5556
PORT_TCP = 5556
PORT_CLIENT_LISTENER = 5558

(
KEY_FWD,
KEY_BACK,
KEY_LEFT,
KEY_RIGHT,
KEY_JUMP,
) = range(5)

TICK_RATE = 66
TICK_DELAY = 1.0/ TICK_RATE
CLIENT_SEND_RATE = 33
CLIENT_SEND_DELAY = 1.0 / CLIENT_SEND_RATE
CLIENT_SEND_DELAY = 0.03
SERVER_SEND_RATE = 20
SERVER_SEND_DELAY = 1.0 / SERVER_SEND_RATE

SIMULATED_DELAY = 0 / 2000.0


MAX_PLAYERS = 16
CURRENT_PLAYERS = 0

# Fonts
FONT_SAF = None #loader.loadFont('Assets/Fonts/SAF.otf')

# 3D Audio
AUDIO_3D = None

# LibRocket
ROCKET_REGION = None
ROCKET_CONTEXT = None

# Colors
COLOR_BLACK = Vec4(0, 0, 0, 1)
COLOR_WHITE = Vec4(1, 1, 1, 1)
COLOR_GREY = Vec4(0.2, 0.2, 0.2, 1)
COLOR_PINK = Vec4(1, 0, 1, 1)
COLOR_BLUE = Vec4(0, 0, 1, 1)
COLOR_RED = Vec4(0.72, 0, 0, 1)
COLOR_TRANSPARENT = Vec4(1, 1, 1, 0)

TEAM_COLORS = [COLOR_RED, COLOR_BLUE, COLOR_GREY]

# Field of View
NORMAL_FOV = 90

def ConvertFromImageAbsoluteToAspect2D(x, y, imageDim):
    screenWidth = Settings.WIDTH
    screenHeight = Settings.HEIGHT
    scaledImageDim = min(screenWidth, screenHeight)
    scaledImageCenter = scaledImageDim / 2 
    scale = 1.0 * scaledImageDim / imageDim
    scaledX = scale * x
    scaledY = scale * y
    
    xPrime = 1.0 * (scaledX - scaledImageCenter) / scaledImageCenter
    yPrime = -1.0 * (scaledY - scaledImageCenter) / scaledImageCenter
    
    return [xPrime, yPrime]

def ConvertFromScreenPixelToAspect2D(x, y):
    centerWidth = Settings.WIDTH / 2
    centerHeight = Settings.HEIGHT / 2
    minDim = min(Settings.HEIGHT, Settings.WIDTH)
    
    return [2.0 * (x - centerWidth) / minDim, -2.0 * (y - centerHeight) / minDim]
    

def GetAspect2DMousePos():
    x = base.win.getPointer(0).getX()
    y = base.win.getPointer(0).getY()
    return ConvertFromScreenPixelToAspect2D(x, y)

def LoadRocket():
    global ROCKET_REGION, ROCKET_CONTEXT
    LoadFontFace("Assets/libRocket/Fonts/Delicious-Roman.otf")
    
    ROCKET_REGION = RocketRegion.make('pandaRocket', base.win)
    ROCKET_REGION.setActive(1)
    ROCKET_REGION.setSort(200)
    ROCKET_CONTEXT = ROCKET_REGION.getContext()
    
    ih = RocketInputHandler()
    base.mouseWatcher.attachNewNode(ih)
    ROCKET_REGION.setInputHandler(ih)
    print 'made region'

