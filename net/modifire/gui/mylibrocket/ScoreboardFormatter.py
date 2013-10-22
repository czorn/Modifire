

from panda3d.rocket import DataFormatter #@UnresolvedImport

import Globals

class ScoreboardFormatter(DataFormatter):
    
    def __init__(self):
        DataFormatter.__init__(self, 'scoreboardFormatter')
        self.sf1 = ScoreboardIsAliveFormatter()
        self.sf2 = ScoreboardPidFormatter()
    
    def FormatData(self, raw_data):
        return raw_data[0]
    
class ScoreboardIsAliveFormatter(DataFormatter):
    def __init__(self):
        DataFormatter.__init__(self, 'scoreboardIsAliveFormatter')
    
    def FormatData(self, raw_data):
        if(raw_data[0] == 'True'):
            return '&nbsp;'
        else:
            return '&nbsp;&nbsp;x_x'
        
class ScoreboardPidFormatter(DataFormatter):
    
    def __init__(self):
        DataFormatter.__init__(self, 'scoreboardPidFormatter')
    
    def FormatData(self, raw_data):        
        # Tag our pid cell so we can color the row later
        if(int(raw_data[0]) == Globals.MY_PID):
            return '<div id="myPidCell">%s</div>' % (raw_data[0])
        else:
            return raw_data[0]