from panda3d.core import Vec3
from inventory.MainInventory import MainInventory
from item.ItemId import ItemId
from player.PositionHistory import PositionHistory

# This is information about players that the server
# will send clients. Clients will use it
# to update players
class PlayerState():
    (USED_ITEM,
     VICTIM,
     HEALTH,
     DIED,
     RESPAWNED,
     CURRENT_ITEM,
     IS_WALKING,
     VICTIM_ATTACK_TYPE,
     IS_GROUNDED,
     KEYS_PRESSED,
     PID,
     LOOKING_DIRECTION,
     Z_VELOCITY,
     TIME_ELAPSED,
     CLICK_1,
     CLICK_2,
     CLICK_3,
     TIMESTAMP,
     MAIN_INVENTORY,
     NAME,
     PLAYING_STATE,
     POSITION,
     POSITION_HISTORY,
     START,
     KILLS,
     DEATHS,
     SCORE,
     ASSISTS,
     PING,
     CLASS,
     TEAM,
     CURRENT_SERVER_TIME,
     LAST_SERVER_TIME) = range(33)
     
    (PS_SPECTATE,
     PS_PLAYING_DEAD,
     PS_PLAYING) = range(3)
     
    (VAT_NONE,
     VAT_HEADSHOT,
     VAT_KILLSHOT,
     VAT_BOTH) = range(4)
    
    def __init__(self, player, isSnapshot = False):
        self.player = player
        
        if(isSnapshot):
            self.vars = {}
        else:
            self.vars = {PlayerState.IS_WALKING : 0,
                         PlayerState.IS_GROUNDED : 0,
                         PlayerState.PID : -1,
                         PlayerState.KEYS_PRESSED : [],
                         PlayerState.Z_VELOCITY : 0,
                         PlayerState.TIME_ELAPSED : 0,
                         PlayerState.CLICK_1 : 0,
                         PlayerState.CLICK_2 : 0,
                         PlayerState.CLICK_3 : 0,
                         PlayerState.TIMESTAMP : 0,
                         PlayerState.HEALTH : 100,
                         PlayerState.NAME : 'DefaultName',
                         PlayerState.KILLS : 0,
                         PlayerState.ASSISTS : 0,
                         PlayerState.DEATHS : 0,
                         PlayerState.CLASS : None,
                         PlayerState.SCORE : 0,
                         PlayerState.PING : 0,
                         PlayerState.MAIN_INVENTORY : MainInventory(),
                         PlayerState.LOOKING_DIRECTION : Vec3(1, 0, 0),
                         PlayerState.PLAYING_STATE : PlayerState.PS_SPECTATE,
                         PlayerState.CURRENT_ITEM : ItemId.NoItem,
                         PlayerState.POSITION_HISTORY : PositionHistory(),
                         PlayerState.CURRENT_SERVER_TIME : 0,
                         PlayerState.LAST_SERVER_TIME : 0,
                         PlayerState.TEAM : None,
                         PlayerState.POSITION : Vec3(1, 1, 20)}
        
        self.varsToUpdate = []
        self.timestamp = 0     
        self.posUpdate = True     
        
    def GetReliableChanges(self):
        change = 0
        #print self.varsToUpdate
        for dVar in self.varsToUpdate:
            if(dVar == PlayerState.USED_ITEM):
                if(PlayerState.VICTIM in self.varsToUpdate):
                    change += 2**PlayerState.VICTIM
                else:
                    change += 2**PlayerState.USED_ITEM
            if(dVar == PlayerState.HEALTH):
                change += 2**PlayerState.HEALTH
            if(dVar == PlayerState.DIED):
                change += 2**PlayerState.DIED
            if(dVar == PlayerState.RESPAWNED):
                change += 2**PlayerState.RESPAWNED
            if(dVar == PlayerState.CURRENT_ITEM):
                change += 2**PlayerState.CURRENT_ITEM
            if(dVar == PlayerState.IS_WALKING):
                change += 2**PlayerState.IS_WALKING
                
        #print change
        return change

    def GetDeltaVars(self):
        return self.varsToUpdate
    
    def ClearDeltaVars(self):
        self.varsToUpdate = []
    
    def GetValue(self, value):
        return self.vars[value]
    
    def SetValue(self, key, value):
        self.vars[key] = value
        
    def HasValue(self, key):
        return key in self.vars.keys()
    
    def GetPlayer(self):
        return self.player
    
    def UpdateDeltaVars(self, key):
        if(not (key in self.varsToUpdate)):
            self.varsToUpdate.append(key)
    
    def UpdateValue(self, key, value):
        updated = False
        
        if(not self.HasValue(key)):
            self.vars[key] = 0
        
        if(key == PlayerState.KEYS_PRESSED):
            if(value != self.vars[PlayerState.KEYS_PRESSED]):
                self.UpdateDeltaVars(PlayerState.KEYS_PRESSED)
                self.SetValue(PlayerState.KEYS_PRESSED, value)
                    
                if(len(value) > 0):
                    self.UpdateValue(PlayerState.IS_WALKING, True)
                else:
                    self.UpdateValue(PlayerState.IS_WALKING, False)
                    
                updated = True
                
        elif(key == PlayerState.POSITION):
            
            # Has the player moved?
            if(not self.ArePositionsEqual(value, self.vars[PlayerState.POSITION])):
                self.SetValue(PlayerState.POSITION, value)
                self.UpdateDeltaVars(PlayerState.POSITION)
                
                updated = True
        
        else:
            if(value != self.vars[key]):
                self.vars[key] = value
                self.UpdateDeltaVars(key)
                
                updated = True
        
        return updated
            
            
    def ArePositionsEqual(self, pos1, pos2):
        x1 = int(pos1.getX() * 1000)
        y1 = int(pos1.getY() * 1000)
        z1 = int(pos1.getZ() * 1000)
        
        x2 = int(pos2.getX() * 1000)
        y2 = int(pos2.getY() * 1000)
        z2 = int(pos2.getZ() * 1000)
        
        return (x1 == x2) and (y1 == y2) and (z1 == z2)
            
    def GetPlayer(self):
        return self.player
            
            