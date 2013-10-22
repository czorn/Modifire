
import InputKeys

WIDTH = 850
HEIGHT = 480
GRAVITY = -10
DEBUG_EVENT = 1
DEBUG_PLAYER_STATE = 1
DEBUG_FSM = 1
NAME = 'Player'
SERVER = '127.0.0.1'
IS_SERVER = 0
LAST_WORLD = 'MyWorld'
MOUSE_SENSITIVITY = 2.0
SERVER_NAME = 'Unnamed Server'
SERVER_PUBLIC = True
CHAT_HEIGHT = 0.05
SOUND_EFFECT_VOLUME = 1.0
AUTO_RELOAD = True
ADS_MOUSE_SENSITIVITY_MULTIPLIER = 0.5
SNIPER_ADS_MOUSE_SENSITIVITY_MULTIPLIER = 0.25
FRIENDLY_FIRE = False

# Key Bindings
KEY_BINDINGS = {InputKeys.MOVE_FORWARD : 'w',
                InputKeys.STRAFE_LEFT : 'a',
                InputKeys.MOVE_BACKWARD : 's',
                InputKeys.STRAFE_RIGHT : 'd',
                InputKeys.JUMP : 'space',
                InputKeys.RELOAD : 'r',
                InputKeys.USE : 'mouse1',
                InputKeys.ALTERNATE_USE : 'mouse3',
                InputKeys.INVENTORY : 'e'}

def Transpose(x, xDim):
    minDim = min(WIDTH, HEIGHT)
    return 1.0 * x / xDim * minDim