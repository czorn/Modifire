
# A cube in game
# Makes up the game environment

class Block():
    def __init__(self, idNum):
        self.id = idNum              # The material of the block
        self.parentChunk = None      # The chunk this block belongs to
    
    # Air has an id of 0, so anything greater than
    # it is solid
    def IsSolid(self):
        return self.id > 0
    
    # Update the ID and tell the parent chunk
    # that it needs to be redrawn
    def SetId(self, newId):
        self.id = newId
        
    def GetId(self):
        return self.id
            
    # Mark the block as needing to be redrawn
#    def SetDirty(self, val):
#        if(self.parentChunk):
#            self.parentChunk.SetDirty(1)
    
    
        
#    def SetParentChunk(self, val):
#        self.parentChunk = val 