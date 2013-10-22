from event.Event import Event

class InventoryEvent(Event):
    
    EventName = 'InventoryEvent'
    
    def __init__(self, inventory, eventName = EventName):
        Event.__init__(self, eventName)
        self.inventory = inventory
        
    def GetInventory(self):
        return self.inventory
  
class InventoryChangeEvent(InventoryEvent):
    
    EventName = 'InventoryChangeEvent'
    
    def __init__(self, inventory):
        InventoryEvent.__init__(self, inventory, InventoryChangeEvent.EventName)
        
class SelectedItemChangeEvent(InventoryEvent):
    
    EventName = 'SelectedItemChangeEvent'
    
    def __init__(self, inventory, itemStack):
        InventoryEvent.__init__(self, inventory, SelectedItemChangeEvent.EventName)
        self.itemStack = itemStack
    
    def GetItemStack(self):
        return self.itemStack
    
# Changes to the weapon itself, such as adding a new attachment, or changing
# which block the Builder places
class SelectedItemAttributeChangeEvent(InventoryEvent):
    
    EventName = 'SelectedItemAttributeChangeEvent'
    
    def __init__(self, inventory, itemStack):
        InventoryEvent.__init__(self, inventory, SelectedItemAttributeChangeEvent.EventName)
        self.itemStack = itemStack
    
    def GetItemStack(self):
        return self.itemStack
    
    
class AmmoChangeEvent(InventoryEvent):
    
    EventName = 'AmmoChangeEvent'
    
    def __init__(self, inventory, item):
        InventoryEvent.__init__(self, inventory, AmmoChangeEvent.EventName)
        self.item = item
    
    def GetItem(self):
        return self.item