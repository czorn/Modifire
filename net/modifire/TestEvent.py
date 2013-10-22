from direct.showbase.ShowBase import ShowBase
from event.ChatEvent import ChatEnteredEvent

  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept(ChatEnteredEvent.EventName, self.do)
        c = ChatEnteredEvent('asd', '123').Fire()
        
        
    def do(self, event):
        print event.GetEventName()

app = MyApp() 
app.run()








    
    
run()