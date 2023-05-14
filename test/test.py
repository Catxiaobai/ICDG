a = '12345'
b = 456
c = 65132
CALLDATA = '0x' + hex(int(a))[2:].zfill(8) + str(hex(b)[2:].zfill(32)) + str(
    hex(c)[2:].zfill(32))
print(CALLDATA)
