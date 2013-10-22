
from environment.EnvironmentLoader import EnvironmentLoader
from event.ClientEvent import LoadProgressEvent


class EnvironmentReceiver():
    
    def __init__(self, totalPackets, xmax, ymax, zmax):
        self.totalPackets = totalPackets
        self.currentPackets = 0.0
        self.blocks = []
        self.xmax = xmax
        self.ymax = ymax
        self.zmax = zmax
        
    def OnPacketReceived(self, data):
        totalBlocks = data.getRemainingSize()
        for i in xrange(totalBlocks):
            self.blocks.append(data.getUint8())
            
        self.currentPackets += 1.0
        LoadProgressEvent('Download ALL the Environment!', self.currentPackets / self.totalPackets).Fire()
        
    def GetBlocks(self):
        return EnvironmentLoader.Blocks1Dto3D(self.blocks, self.xmax, self.ymax, self.zmax)
    