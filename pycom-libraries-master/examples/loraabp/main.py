from network import LoRa
import socket
import binascii
import struct
import time

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
# create an ABP authentication params
dev_addr = struct.unpack(">l", binascii.unhexlify('90 53 07 24'.replace(' ','')))[0]
nwk_swkey = binascii.unhexlify('2B 7E 15 16 28 AE D2 A6 AB F7 15 88 09 CF 4F 3C'.replace(' ',''))
app_swkey = binascii.unhexlify('2B 7E 15 16 28 AE D2 A6 AB F7 15 88 09 CF 4F 3C'.replace(' ',''))

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
print("Done")
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.bind(5)
# make the socket non-blocking
s.setblocking(True)

# send some data
x = 0

while True:
    s.send("string")
    time.sleep(20)
    print("Sent\n" + str(x))
    x += 1

# get any data received...
data = s.recv(64)
print(data)
