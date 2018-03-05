import binascii

def str2int(string):
    x = binascii.hexlify(string)
    x = int(x, 16)
    x = x + 0x200
    return x

def int2str(integer):
    integer = integer - 0x200
    integer = hex(integer)
    return binascii.unhexlify(integer[2:-1])

y = str2int("My name is Dan")
print(y)
x = int2str(y)
print(x)
