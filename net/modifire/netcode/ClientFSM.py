from direct.fsm.FSM import FSM
import Settings

class ClientFSM(FSM):
    
    def __init__(self, client):
        FSM.__init__(self, 'ClientFSM')
        self.client = client
        
    def enterCreateNetworkObjects(self):
        if(Settings.DEBUG_FSM):
            print '[ClientFSM ] EnterCreateNetworkObjects'
        
        if(self.client.CreateNetworkObjects()):
            self.demand('Idle')
        else:
            self.demand('Error')
            
    def exitCreateNetworkObjects(self):
        pass 
    
    def enterIdle(self, reason = ''):
        if(Settings.DEBUG_FSM):
            print '[ClientFSM ] EnterIdle', reason
        
    def exitIdle(self):
        pass 
    
    def enterWaitingForJoinResponse(self):
        pass
    
    def enterWaitingForEnvironment(self):
        pass
            
    def enterPlayingGame(self):
        if(Settings.DEBUG_FSM):
            print '[ClientFSM ] enterPlayingGame'
            
    def exitPlayingGame(self):
        self.client.dataHandler.SendClientDisconnect()    
    
    def enterError(self):
        if(Settings.DEBUG_FSM):
            print '[ClientFSM ] EnterError'
        pass