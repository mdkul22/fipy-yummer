from network import LoRa
import socket
import binascii
import struct

# IN PROGRESS
class LoraNode():

    def __init__(self, appkey, appSkey, nwkSkey):

        # Initialize LoRa in LORAWAN mode.
        # Please pick the region that matches where you are using the device:
        # Asia = LoRa.AS923
        # Australia = LoRa.AU915
        # Europe = LoRa.EU868
        # United States = LoRa.US915
        lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AS923)

        # create an ABP authentication params
        dev_addr = struct.unpack(">l", binascii.unhexlify(appkey))[0]
        nwk_swkey = binascii.unhexlify(nwkSkey)
        app_swkey = binascii.unhexlify(appSkey)

        # join a network using ABP (Activation By Personalization)
        lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
        # create a LoRa socket
        s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        # set the LoRaWAN data rate
        s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
        # make the socket blocking
        # (waits for the data to be sent and for the 2 receive windows to expire)
        s.setblocking(True)
        print("Connected to LoRa network")

    def sendData(self, string)
        # send some data
        s.send(bytes(string))
