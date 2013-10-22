


class FileHandler():
    
    def __init__(self):
        self.openFiles = {}
        
    def StartFileWriter(self, fileloc, filename):
        print fileloc, filename
        FILE = open(fileloc, 'w')
        self.openFiles[filename] = FILE
        
    def WriteLinesToFile(self, filename, lines):
        #print filename, lines
        FILE = self.openFiles[filename]
        
        for line in lines:
            FILE.write(line)
            
    def CloseFile(self, filename):
        print 'FILE CLOSED', filename
        self.openFiles[filename].close()
        del self.openFiles[filename]
        messenger.send('fileTransferComplete', [filename])