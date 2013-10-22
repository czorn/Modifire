import os

def Run():
    
    i = 0
    
    currentDir = os.getcwd()
    
    for root, dirs, files in os.walk(currentDir):
        for f in files:
            if f.endswith('.py'):
                FILE = open('\\'.join([root, f]))
                j = 0
                while 1:
                    lines = FILE.readlines(100000)
                    if not lines:
                        break
                    for line in lines:
                        j += 1
                print f, j
                i += j
    
    print 'Total', i
    
Run()