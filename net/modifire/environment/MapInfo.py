



class MapInfo():
    
    def __init__(self, author, size, spawn1, spawn2):
        self.author = author
        self.size = size
        self.spawn1 = spawn1
        self.spawn2 = spawn2
        
    def GetAuthor(self):
        return self.author
    
    def GetSize(self):
        return self.size