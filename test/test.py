a = '12345'
b = 456
c = 65132
CALLDATA = '0x' + hex(int(a))[2:].zfill(8) + str(hex(b)[2:].zfill(32)) + str(
    hex(c)[2:].zfill(32))
print(CALLDATA[10:])
print(int(CALLDATA[42:], 16))
if 13 < 0xf:
    print(1)
print(len(CALLDATA))
print(int(0xffffffffffffffffffffffffffffffff))