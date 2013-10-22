from panda3d.rocket import RocketRegion, RocketInputHandler, LoadFontFace #@UnresolvedImport
from direct.directbase import DirectStart

from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'sync-video 0')

#from inventory.BlockInventoryDataSource import BlockInventoryDataSource
#from inventory.BlockInventoryDataFormatter import BlockInventoryDataFormatter
from gui.Scoreboard import Scoreboard
from gui.mylibrocket.ScoreboardFormatter import ScoreboardFormatter

import Globals

LoadFontFace("Assets/libRocket/Fonts/Delicious-Roman.otf")
LoadFontFace("Assets/libRocket/Fonts/SAF.otf")

r = RocketRegion.make('pandaRocket', base.win)
r.setActive(1)
r.initDebugger()
r.setDebuggerVisible(True)
context = r.getContext()
Globals.ROCKET_CONTEXT = context

#b = BlockInventoryDataSource()
#bf = BlockInventoryDataFormatter()
#s = Scoreboard()
#s.NewRow(1, 'Testname')
#s.NewRow(-1, 'Testname2')
#s.Show()
#sf = ScoreboardFormatter()

context.LoadDocument('Assets/libRocket/offline.rml').Show()
#context.LoadDocument('Assets/libRocket/scoreboard.rml').Show()
#context.LoadDocument('Assets/libRocket/blockInventory.rml').Show()
#context.LoadDocument('Assets/libRocket/mainMenu.rml').Show()

ih = RocketInputHandler()
base.mouseWatcher.attachNewNode(ih)
r.setInputHandler(ih)

#r.initDebugger()
#r.setDebuggerVisible(True)

from panda3d.rocket import DataSource

class HighScoreDataSource(DataSource): 
    def __init__(self, name): 
        self.scores = [] # could be any name 
        self.scores.append({'name': 'Mike', 'wave': 1, 'score': "42", "colour": "USSExcelsior"}) 
        
        DataSource.__init__(self, name) 


    def GetRow(self, table_name, index, columns): 
        row = list() 
        
        if index > len(self.scores)-1: 
            return row 
                
        if(table_name == 'scores'): 
            for col in columns: 
                
                if col not in self.scores[index]: 
                    continue # skip columns we don't know 
                
                if(col == 'name'): 
                    row.append(self.scores[index][col]) 

                elif(col == 'score'): 
                    row.append(self.scores[index][col]) 

                elif(col == 'colour'): 
                    row.append(self.scores[index][col]) 

                elif(col == 'wave'): 
                    row.append(self.scores[index][col]) 

        return row 
        
    def GetNumRows(self, table_name): 
        if(table_name == 'scores'): 
            return len(self.scores) 

        return 0 

hs = HighScoreDataSource("high_scores") 

run()