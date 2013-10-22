




class ServerDataCollector():
    
    def __init__(self):
        self.Reset()
        
    def Reset(self):
        self.users = []
        self.attackers = []
        self.victims = []
        self.victimHealths = []
        self.deaths = []
        self.respawns = []