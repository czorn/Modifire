from direct.fsm.FSM import FSM

class InputFSM(FSM):
    
    def __init__(self, engine, chat, menuController):
        FSM.__init__(self, 'InputFSM')
        self.engine = engine
        self.chat = chat
        self.menuController = menuController
        
    def enterGame(self):
        print 'game'
        self.engine.EnableKeyboardListening()
        
    def exitGame(self):
        self.engine.DisableKeyboardListening()
    
    def enterChat(self):
        self.chat.EnableKeyboardListening()
        
    def exitChat(self):
        self.chat.DisableKeyboardListening()
    
    def enterMenu(self):
        self.menuController.EnableKeyboardListening()
    
    def exitMenu(self):
        self.menuController.DisableKeyboardListening()