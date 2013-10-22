
from panda3d.rocket import DataSource #@UnresolvedImport

class BlockInventoryDataSource(DataSource): 
    
    def __init__(self): 
        self.width = 5
        self.height = 3
        DataSource.__init__(self, 'blockInventory') 


    def GetRow(self, table_name, index, columns):
        print table_name, index, columns
        row = [] 
        
        if(index > self.width-1): 
            return row 
                
        if(table_name == 'slots'): 
            for i, col in enumerate(columns):
                if(col[0] != '#'):
                    row.append(str(index * self.width + i))
                    
        return row 
        
    def GetNumRows(self, table_name): 
        if(table_name == 'slots'): 
            return self.height 

        return 0 
