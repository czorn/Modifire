from direct.fsm.FSM import FSM
from Engine import Engine
from event.ClientEvent import EngineLoadedEvent
import Settings

class ServerFSM(FSM):
    
    def __init__(self, server):
        FSM.__init__(self, 'ServerFSM')
        self.server = server
    
    def enterLoadingEngine(self):
        print '[ServerFSM ] enterLoadingEngine'
            
        self.server.engine = Engine(-1, 'level.map', server = True)
        self.server.engine.server = self.server
        EngineLoadedEvent().Fire()
        self.demand('CreateNetworkObjects')
        
    def exitLoadingEngine(self):
        pass
    
    def enterCreateNetworkObjects(self):
        if(Settings.DEBUG_FSM):
            print '[ServerFSM ] enterCreateNetworkObjects'
        if(self.server.CreateNetworkObjects()):
            self.demand('EngineRunning')
        else:
            self.demand('ServerStopped')
            
    def exitCreateNetworkObjects(self):
        pass
    
    def enterEngineRunning(self):
        if(Settings.DEBUG_FSM):
            print '[ServerFSM ] enterEngineRunning'
        
        self.server.StartBroadcastGameState()
    
    def enterEngineStop(self):
        pass
    
    def enterServerStopped(self):
        if(Settings.DEBUG_FSM):
            print '[ClientFSM ] enterServerStopped'
        pass