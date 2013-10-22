from datetime import datetime

class Log():
    
    def __init__(self):
        self.FILE = 0
        self.active = True
        
    def Open(self, filename):
        try:
            self.FILE = open(filename, 'w')
            self.FILE.write( '%s [%s] %s (%s)' % (datetime.now(), 'INFO', 'Log File Created', filename))
        except:
            print '[ERROR] Could not open %s for writing' % (filename)
            self.active = False   
        
        
    def Close(self):
        if(self.active):
            self.FILE.close()
        
    def WriteError(self, msg):
        if(self.active):
            self.WriteLine(msg, 'ERROR')
        
    def WriteLine(self, msg, msgcode = 'INFO'):
        if(self.active):
            self.FILE.write('\n%s [%s] %s' % (datetime.now(), msgcode, msg))