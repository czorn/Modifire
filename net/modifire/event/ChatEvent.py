
from event.Event import Event

class ChatEvent(Event):
    
    EventName = 'ChatEvent'
    
    def __init__(self, eventName = EventName):
        Event.__init__(self, eventName)  

class ChatOpenEvent(ChatEvent):
    
    EventName = 'ChatOpenEvent'
    
    def __init__(self):
        ChatEvent.__init__(self, ChatOpenEvent.EventName)
        
class ChatCloseEvent(ChatEvent):
    
    EventName = 'ChatCloseEvent'
    
    def __init__(self):
        ChatEvent.__init__(self, ChatCloseEvent.EventName)
        
class ChatEnteredEvent(ChatEvent):
    
    EventName = 'ChatEnteredEvent'
    
    def __init__(self, messageType, message):
        ChatEvent.__init__(self, ChatEnteredEvent.EventName)
        self.messageType = messageType
        self.message = message
        
    def GetMessageType(self):
        return self.messageType
    
    def GetMessage(self):
        return self.message
        
class ChatReceivedEvent(ChatEvent):
    
    EventName = 'ChatReceivedEvent'
    
    def __init__(self, messageType, player, message):
        ChatEvent.__init__(self, ChatReceivedEvent.EventName)
        self.messageType = messageType
        self.player = player
        self.message = message
        
    def GetMessageType(self):
        return self.messageType
    
    def GetPlayer(self):
        return self.player
    
    def GetMessage(self):
        return self.message
    
class ChatDeathEvent(ChatEvent):
    
    EventName = 'ChatDeathEvent'
    
    def __init__(self, attackerName, victimName, weaponName, wasHeadshot):
        ChatEvent.__init__(self, ChatReceivedEvent.EventName)
        self.attackerName = attackerName
        self.victimName = victimName
        self.weaponName = weaponName
        self.wasHeadshot = wasHeadshot
        
    def GetAttackerName(self):
        return self.attackerName
    
    def GetVictimName(self):
        return self.victimName
    
    def GetWeaponName(self):
        return self.weaponName
    
    def WasHeadshot(self):
        return self.wasHeadshot
    
        
