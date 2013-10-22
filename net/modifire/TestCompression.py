
import random
import zlib

def compress(blocks):
    cBlocks = []
    
    last = None
    i = 0
    for b in blocks:
        if(b == last):
            i += 1
        else:
            cBlocks.append(b)
            cBlocks.append(i)
            i = 1
            last = b
    return cBlocks




blocks = []

cSize = 16

for x in xrange(cSize):
    for y in xrange(cSize):
        for z in xrange(cSize):
            blocks.append(chr(random.randint(0, 1)))
            
print len(blocks)
print '\n\n\n-----------\n\n\n'
print len(compress(blocks))
