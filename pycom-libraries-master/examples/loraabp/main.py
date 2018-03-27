from network import LoRa
import socket
import binascii
import struct
import time
import json
from SI7006A20 import SI7006A20
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
y = 0
temp = SI7006A20()
while True:
    dict = {"name": 'temp', "val" : x, "humidity" : y}
    msg = json.dumps(dict)
    s.send(msg)
    time.sleep(20)
    print("Sent\n" + str(x))
    x = temp.temperature()
    y = temp.humidity()

# get any data received...
data = s.recv(64)
print(data)
