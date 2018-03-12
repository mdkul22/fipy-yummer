from network import LoRa
import socket
import binascii
import struct

# IN PROGRESS 
class LoraNode():

    def __init__(self):

# Initialize LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
        lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an ABP authentication params
        dev_addr = struct.unpack(">l", binascii.unhexlify('00 00 00 05'.replace(' ','')))[0]
        nwk_swkey = binascii.unhexlify('2B 7E 15 16 28 AE D2 A6 AB F7 15 88 09 CF 4F 3C'.replace(' ',''))
        app_swkey = binascii.unhexlify('2B 7E 15 16 28 AE D2 A6 AB F7 15 88 09 CF 4F 3C'.replace(' ',''))

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)

# send some data
s.send(bytes([0x01, 0x02, 0x03]))
