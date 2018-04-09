from network import WLAN
from mqtt import MQTTClient
import machine
import time

def settimeout(duration):
    pass

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.EXT_ANT)
wlan.connect("thingQbator", auth=(WLAN.WPA2, "C1sco12345"), timeout=5000)

while not wlan.isconnected():
     machine.idle()

print("Connected to Wifi\n")
client = MQTTClient("demo", "broker.hivemq.com", port=1883)
client.settimeout = settimeout
client.connect()

while True:
     print("Sending ON")
     client.publish("/lights", "ON")
     time.sleep(1)
     print("Sending OFF")
     client.publish("/lights", "OFF")
     time.sleep(1)
