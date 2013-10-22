
from pandac.PandaModules import Ramfile, HTTPClient, DocumentSpec
import Settings
import Globals
import urllib

class Heartbeat():
    
    def __init__(self):
        self.http = HTTPClient()
        
        self.SendHeartbeat()
        #taskMgr.doMethodLater(10, self.SendHeartbeat, 'SendHeartbeat')
        
    def SendHeartbeat(self, task = None):
        baseUrl = 'http://modifire.net/heartbeat.php?'
        values = {'name' : Settings.SERVER_NAME,
                  'currentPlayers' : Globals.CURRENT_PLAYERS,
                  'maxPlayers' : Globals.MAX_PLAYERS,
                  'public' : Settings.SERVER_PUBLIC,
                  'port' : Globals.PORT_SERVER_LISTENER,
                  'version' : Globals.VERSION}
        
        for key, value in values.iteritems():
            values[key] = urllib.quote(str(value))
        
        params = [
                  baseUrl,
                  'name=%s' % (values['name']),
                  'currentPlayers=%s' % (values['currentPlayers']),
                  'maxPlayers=%s' % (values['maxPlayers']),
                  'public=%s' % (values['public']),
                  'port=%s' % (values['port']),
                  'version=%s' % (values['version'])
                  ]
        
        req = '&'.join(params)
        self.channel = self.http.makeChannel(True)
        self.channel.beginGetDocument(DocumentSpec(req))
        self.rf = Ramfile()
        self.channel.downloadToRam(self.rf)
        taskMgr.add(self.downloadTask, 'download')
        
        if(task):
            return task.again
         
    def downloadTask(self, task):
        if self.channel.run():
            return task.cont
        if not self.channel.isDownloadComplete():
            return task.done
        data = self.rf.getData()
        return task.done