
def Int16ToBits(int16):
    return list(''.join([str((int16 >> y) & 1) for y in range(16-1, -1, -1)]))

bits = ['1', '1', '1', '1', '1', '1', '1', '0']
bits.extend(bits)

#print int(''.join(bits), 2)
print ''.join(bits)
print '00100001'
print int(''.join(bits), 2)
print Int16ToBits(int(''.join(bits), 2))

print '------------------------'

print 2**0 + 2**1
print 2**2
print (2**0 + 2**1) & 2**2