from machine import Pin
import pycom
import time
from network import Bluetooth

bluetooth = Bluetooth()
bluetooth.set_advertisement(name='FiPy', service_uuid=0xffffff01234)

def conn_cb (bt_o):
    events = bt_o.events()
    if  events & Bluetooth.CLIENT_CONNECTED:
        print("Client connected")
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print("Client disconnected")

bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)

bluetooth.advertise(True)

srv1 = bluetooth.service(uuid=0xfff0, isprimary=True)

chr1 = srv1.characteristic(uuid=0x1000, value="ssid")

def char1_cb_handler(chr):

    events = chr.events()
    if  events & Bluetooth.CHAR_WRITE_EVENT:
        chr1.value(chr.value())
        print("Write request with value = {}".format(chr.value()))
    else:
        return chr1.value()

char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)
