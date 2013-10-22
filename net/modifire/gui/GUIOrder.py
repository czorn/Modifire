
class GUIOrder():
    (
    HUD,
    HUD_ITEM,
    MENU,
    INV_LOW,
    INV_HIGH,
    CHAT
    ) = range(6)
    
    ORDER = {HUD : 10,
             HUD_ITEM : 11,
             MENU : 30,
             INV_LOW : 31,
             INV_HIGH : 32,
             CHAT : 50}