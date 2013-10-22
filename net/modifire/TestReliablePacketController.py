
import random
from collections import deque
from pandac.PandaModules import NetAddress, NetDatagram
from netcode.ReliablePacketController import ReliablePacketController

pq = []

def SendPacket(rpc, addr):
    global pq
    chance = random.random()
    p = rpc.CreateNewPacket(addr)
    rpc.SendPacket(p, addr)
    nd = NetDatagram()
    nd.appendData(p.GetDatagram().getMessage())#, p.GetDatagram().getLength())
    nd.setAddress(NetAddress())
    if(chance < 0.8):
        pq.append(nd)
        return nd

clientRPC = ReliablePacketController('Client')
serverRPC = ReliablePacketController('Server')

clientAddr =  NetAddress()
#clientAddr.setHost('123.123.123.123', 1234)

serverAddr = NetAddress()
#serverAddr.setHost('456.456.456.456', 4567)

print 'Server Send'
serverRPC.StartStream(clientAddr)
for i in xrange(150):
    p = SendPacket(serverRPC, clientAddr)
    if(p):
        print 'CLIENT:',
        clientRPC.OnPacketReceived(p)
    if((i+1) % 14 == 0):
        p = SendPacket(clientRPC, serverAddr)
        if(p):
            print 'SERVER:',
            serverRPC.OnPacketReceived(p)
    
serverRPC.EndStream(clientAddr)

while 1:
    p = SendPacket(clientRPC, serverAddr)
    if(p):
        serverRPC.OnPacketReceived(p)
        break
    
while 1:
    p = SendPacket(serverRPC, clientAddr)
    if(p):
        clientRPC.OnPacketReceived(p)
        break
    
while 1:
    p = SendPacket(clientRPC, serverAddr)
    if(p):
        serverRPC.OnPacketReceived(p)
        break
    
#print 'Client Receive'
#for p in pq:
#    clientRPC.OnPacketReceived(p)
#
#print 'Client Send'    
#for i in xrange(15):
#    SendPacket(clientRPC, serverAddr)
#    
#for p in pq:
#    serverRPC.OnPacketReceived(p)