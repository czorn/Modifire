
from panda3d.rocket import DataFormatter #@UnresolvedImport

class BlockInventoryDataFormatter(DataFormatter):
    
    def __init__(self):
        DataFormatter.__init__(self, 'blockInventoryFormatter')
    
    def FormatData(self, raw_data):
        index1 = int(raw_data[0])
        top = (index1 / 16) * 16
        left = (index1 % 16) * 16
        right = left + 16
        bottom = top + 16
        return '<button class="blockInventory" onclick="print %s" style="background-image: ../Images/blocks.png %spx %spx %spx %spx;"></button>' % (raw_data[0], left, top, right, bottom)