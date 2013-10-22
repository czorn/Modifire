# http://unity3d.com/support/documentation/ScriptReference/Time.html

from time import time as ostime
from time import clock

def GetTime():
    #t = ostime()
    t = clock()
    t1 = t - int(t / 10000) * 10000
    return round(t1 * 1000) / 1000.0

time = GetTime()
fixedTime = GetTime()
deltaTime = 0.0001
fixedDeltaTime = 0

def UpdateTime(currentTime):
    global deltaTime, time
    
    deltaTime = currentTime - time
    time = currentTime
    
def UpdateFixedTime(currentFixedTime):
    global fixedDeltaTime, fixedTime
    
    fixedDeltaTime = currentFixedTime - fixedTime
    fixedTime = currentFixedTime
    
def ToMilliseconds(t):
    return int(t * 1000)

def FromMilliseconds(t):
    return t / 1000.0