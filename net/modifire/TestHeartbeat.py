from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from pandac.PandaModules import Ramfile, NetDatagram, HTTPClient, DocumentSpec

  
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        wp = WindowProperties()
        wp.setSize(850, 480)
        wp.setTitle("GAME")
        base.win.requestProperties(wp)
        
        self.http = HTTPClient()
        
        baseUrl = 'http://modifire.net/heartbeat.php?'
        params = [
                  baseUrl,
                  'name=%s' % ('testname'),
                  'currentPlayers=%s' % (0),
                  'maxPlayers=%s' % (16),
                  'public=%s' % (True),
                  'port=%s' % (1234)
                  ]
        
        req = '&'.join(params)
        self.channel = self.http.makeChannel(True)
        self.channel.beginGetDocument(DocumentSpec(req))
        self.rf = Ramfile()
        self.channel.downloadToRam(self.rf)
        taskMgr.add(self.downloadTask, 'download')
         
    def downloadTask(self, task):
        if self.channel.run():
            # Still waiting for file to finish downloading.
            return task.cont
        if not self.channel.isDownloadComplete():
            print "Error downloading file."
            return task.done
        data = self.rf.getData()
        print "got data:"
        print data
        return task.done
            
            
def tskReaderPolling(self, task):
    if self.cReader.dataAvailable():
        datagram = NetDatagram()
        if self.cReader.getData(datagram):
            pass
        
    return task.cont

app = MyApp() 
app.run()
