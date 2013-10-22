

import Settings
import InputKeys
    
CLIENT_FILENAME = 'game.ini'
SERVER_FILENAME = 'server.ini'

def InputKeyToText(inputKey):
    return {InputKeys.MOVE_FORWARD : 'Move_Forward',
            InputKeys.MOVE_BACKWARD : 'Move_Backwards',
            InputKeys.STRAFE_LEFT : 'Strafe_Left',
            InputKeys.STRAFE_RIGHT : 'Strafe_Right',
            InputKeys.JUMP : 'Jump',
            InputKeys.RELOAD : 'Reload',
            InputKeys.USE : 'Use/Fire',
            InputKeys.ALTERNATE_USE : 'Alternate_Use/Toggle_Sights',
            InputKeys.INVENTORY : 'Inventory'}[inputKey]


def LoadServerSettings():
    ProcessServerSettings( LoadSettings(SERVER_FILENAME) )
    
def LoadClientSettings():
    ProcessClientSettings( LoadSettings(CLIENT_FILENAME) )
    
def LoadSettings(filename):
    confFile = {'name':Settings.NAME,
                'mouse_sensitivity':Settings.MOUSE_SENSITIVITY,
                'server':Settings.SERVER,
                'world_name':Settings.LAST_WORLD,
                'server_name':Settings.SERVER_NAME,
                'public':Settings.SERVER_PUBLIC,
                'auto_reload':str(Settings.AUTO_RELOAD),
                'friendly_fire':str(Settings.FRIENDLY_FIRE),
                InputKeyToText(InputKeys.MOVE_FORWARD) : Settings.KEY_BINDINGS[InputKeys.MOVE_FORWARD],
                InputKeyToText(InputKeys.MOVE_BACKWARD) : Settings.KEY_BINDINGS[InputKeys.MOVE_BACKWARD],
                InputKeyToText(InputKeys.STRAFE_LEFT) : Settings.KEY_BINDINGS[InputKeys.STRAFE_LEFT],
                InputKeyToText(InputKeys.STRAFE_RIGHT) : Settings.KEY_BINDINGS[InputKeys.STRAFE_RIGHT],
                InputKeyToText(InputKeys.JUMP) : Settings.KEY_BINDINGS[InputKeys.JUMP],
                InputKeyToText(InputKeys.RELOAD) : Settings.KEY_BINDINGS[InputKeys.RELOAD],
                InputKeyToText(InputKeys.USE) : Settings.KEY_BINDINGS[InputKeys.USE],
                InputKeyToText(InputKeys.ALTERNATE_USE) : Settings.KEY_BINDINGS[InputKeys.ALTERNATE_USE],
                InputKeyToText(InputKeys.INVENTORY) : Settings.KEY_BINDINGS[InputKeys.INVENTORY]
                }
    
    try:
        FILE = open(filename, 'r')
    except IOError:
        CreateINIFile()
        FILE = open(filename, 'r')
        
    while 1 :
        line = FILE.readline()
        if(not line):
            break
        
        if(len(line) > 1 and line[0] != '#'):
            (var, ignore, data) = line.partition("=")
            confFile[var.strip()] = data.strip()
            #print '%s : %s' % (var.strip(), data.strip())

    FILE.close()
    
    return confFile

def ProcessClientSettings(confFile):
    Settings.NAME = confFile['name']
    Settings.MOUSE_SENSITIVITY = float(confFile['mouse_sensitivity'])
    Settings.SERVER = confFile['server']
    Settings.LAST_WORLD = confFile['world_name']
    Settings.AUTO_RELOAD = (confFile['auto_reload'] == 'True')
    
    Settings.KEY_BINDINGS[InputKeys.MOVE_FORWARD] = confFile[InputKeyToText(InputKeys.MOVE_FORWARD)]
    Settings.KEY_BINDINGS[InputKeys.MOVE_BACKWARD] = confFile[InputKeyToText(InputKeys.MOVE_BACKWARD)]
    Settings.KEY_BINDINGS[InputKeys.STRAFE_LEFT] = confFile[InputKeyToText(InputKeys.STRAFE_LEFT)]
    Settings.KEY_BINDINGS[InputKeys.STRAFE_RIGHT] = confFile[InputKeyToText(InputKeys.STRAFE_RIGHT)]
    Settings.KEY_BINDINGS[InputKeys.JUMP] = confFile[InputKeyToText(InputKeys.JUMP)]
    Settings.KEY_BINDINGS[InputKeys.RELOAD] = confFile[InputKeyToText(InputKeys.RELOAD)]
    Settings.KEY_BINDINGS[InputKeys.USE] = confFile[InputKeyToText(InputKeys.USE)]
    Settings.KEY_BINDINGS[InputKeys.ALTERNATE_USE] = confFile[InputKeyToText(InputKeys.ALTERNATE_USE)]
    Settings.KEY_BINDINGS[InputKeys.INVENTORY] = confFile[InputKeyToText(InputKeys.INVENTORY)]
    
def ProcessServerSettings(confFile):
    Settings.SERVER_NAME = confFile['server_name']
    Settings.SERVER_PUBLIC = confFile['public']
    Settings.LAST_WORLD = confFile['world_name']
    Settings.FRIENDLY_FIRE = (confFile['friendly_fire'] == 'True')
    
def SaveSettings(filename, listOfSettingNameTuples):
    FILE = open(filename, 'w')
    for heading, settingsDict in listOfSettingNameTuples:
        FILE.write('%s\n' % heading)
        for k, v in settingsDict.iteritems():
            FILE.write('%s = %s\n' % (k, v))
        FILE.write('\n')
    FILE.close()
    
def SaveClientSettings():
    mySettings =   {'name':Settings.NAME,
                    'mouse_sensitivity':Settings.MOUSE_SENSITIVITY,
                    'server':Settings.SERVER,
                    'world_name':Settings.LAST_WORLD,
                    'auto_reload':Settings.AUTO_RELOAD}
    
    myKeys =   {InputKeyToText(InputKeys.MOVE_FORWARD) : Settings.KEY_BINDINGS[InputKeys.MOVE_FORWARD],
                InputKeyToText(InputKeys.MOVE_BACKWARD) : Settings.KEY_BINDINGS[InputKeys.MOVE_BACKWARD],
                InputKeyToText(InputKeys.STRAFE_LEFT) : Settings.KEY_BINDINGS[InputKeys.STRAFE_LEFT],
                InputKeyToText(InputKeys.STRAFE_RIGHT) : Settings.KEY_BINDINGS[InputKeys.STRAFE_RIGHT],
                InputKeyToText(InputKeys.JUMP) : Settings.KEY_BINDINGS[InputKeys.JUMP],
                InputKeyToText(InputKeys.RELOAD) : Settings.KEY_BINDINGS[InputKeys.RELOAD],
                InputKeyToText(InputKeys.USE) : Settings.KEY_BINDINGS[InputKeys.USE],
                InputKeyToText(InputKeys.ALTERNATE_USE) : Settings.KEY_BINDINGS[InputKeys.ALTERNATE_USE],
                InputKeyToText(InputKeys.INVENTORY) : Settings.KEY_BINDINGS[InputKeys.INVENTORY]}
    SaveSettings(CLIENT_FILENAME, [('#Settings', mySettings), ('#Key Bindings', myKeys)])
    
def SaveServerSettings():
    mySettings = {'server_name':Settings.SERVER_NAME,
                  'public':Settings.SERVER_PUBLIC,
                  'world_name':Settings.LAST_WORLD,
                  'friendly_fire':Settings.FRIENDLY_FIRE}
    SaveSettings(SERVER_FILENAME, [('#Settings', mySettings)])
    
def CreateINIFile():
    SaveClientSettings()
    SaveServerSettings()