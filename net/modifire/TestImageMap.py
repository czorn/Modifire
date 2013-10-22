
import struct

FILE = open('dust2.bmp')

i = 0

for j in xrange(18):
    FILE.read(3)

heights = []
for i in xrange(128):
    rows = []
    for j in xrange(128):
        pixel = FILE.read(3)
        print i, j, pixel
        rows.append(int(100.0 * struct.unpack('B', pixel[0][0])[0] / 255))
    heights.append(rows)
    #FILE.read(3)

print heights