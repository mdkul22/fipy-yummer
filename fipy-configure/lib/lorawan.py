from network import LoRa
import socket
import binascii
import struct

# IN PROGRESS
class LoraNode():

    def __init__(self, appSkey, nwkSkey):
        # dev UI details also needed
        # Initialize LoRa in LORAWAN mode.
        # Please pick the region that matches where you are using the device:
        # Asia = LoRa.AS923
        # Australia = LoRa.AU915
        # Europe = LoRa.EU868
        # United States = LoRa.US915
        lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

        # create an ABP authentication params
        dev_addr = struct.unpack(">l", binascii.unhexlify('90 53 07 24'.replace(' ','')))[0]
        nwk_swkey = binascii.unhexlify(nwkSkey)
        app_swkey = binascii.unhexlify(appSkey)
        print(nwk_swkey)

        # join a network using ABP (Activation By Personalization)
        lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
        # create a LoRa socket
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        # set the LoRaWAN data rate
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
        self.s.bind(5)
        # make the socket blocking
        # (waits for the data to be sent and for the 2 receive windows to expire)
        self.s.setblocking(True)
        print("Connected to LoRa network")

    def sendData(self, string):
        # send some data
        try:
            self.s.send(string)
        except OSError as e:
            if e.args[0] == 11:
                print("weird error")
