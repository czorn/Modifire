from netcode.Snapshot import Snapshot
import copy

class ClientSnapshotHandler():
    
    def __init__(self):
        self.snapshots = LinkedList()
        temp = Snapshot()
        temp.timestamp = 0
        self.snapshots.Init(Node(temp, None))
        self.index = 0
        
    def AddSnapshot(self, snapshot):
        self.snapshots.Add(copy.deepcopy(snapshot))
        #print 'added', snapshot.GetTimestamp()
    
    def GetOldStates(self, oldTime):        
        n = self.snapshots.GetHead()
        if n is None:
            return []
        
        # Get rid of old states
        while(n.next != None and n.data.timestamp < oldTime):
            n = n.next
        
        self.snapshots.SeverAt(n)
            
        # Get all of the useful ones
        states = []    
        while(n != None):
            states.append(n.data)
            n = n.next
        
        return states
    
    def UpdateOldStates(self, states):
        n = self.snapshots.GetHead()
        i = 0
        
        while(n != None):
            n.data = states[i]
            n = n.next
            i += 1
        
class Node():
    
    def __init__(self, data, nextNode):
        self.next = nextNode
        self.data = data
        
    def __str__(self):
        if self.next == None:
            x = [self.data.timestamp, self.data.vars, None]
        else:
            x = [self.data.timestamp, self.data.vars, self.next.data.timestamp]
        return str(x)
        
class LinkedList():
    
    def __init__(self):
        self.head = None
        self.tail = None
        
    def Init(self, node):
        self.head = node
        self.tail = node
        
    def Add(self, data):
        n = Node(copy.deepcopy(data), None)
        self.tail.next = n
        self.tail = self.tail.next
        #self.Display()
        
    def SeverAt(self, node):
        self.head = node
        
    def GetNext(self, node):
        return node.next
    
    def GetHead(self):
        return self.head
    
    def Display(self):
        n = self.head
        print 'LIST'
        while(n != None):
            print n
            n = n.next
        print 'END LIST'
            
            
            
            
            