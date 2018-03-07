import pycom
import time
import network
from nvstring import NvsExtract
from machine import reset
# all variables
# switches
MODE_S = "mode"
WIFI_S = "wifi"
MQTT_S = "mqtt"
LORA_S = "lora"
LTE_S = "lte"
# characteristics
# wifi
SSID = "ssid"
PASS = "pass"
# MQTT
M_SERVER = "server"
M_PORT = "port"
# LORA
APPKEY = "appkey"
APPSKEY = "APPSKEY"
NWKSKEY = "nwkSkey"

class Deploy():
# deploy mode
    def __init__(self):


    def __Init(self):
        # check if mode is 1 and if not, enter low power state
        if NvsExtract(MODE_S).retval() == '0':
            reset()
        if NvsExtract(MODE_S).retval() == '1':
            self.boot_up()

    def boot_up(self):
        # start the deploy mode setup by doing all the checks
        if NvsExtract(WIFI_S).retval() == '1':
            self.WiFi_Setup()

        if NvsExtract(MQTT_S).retval() == '1':
            self.MQTT_Setup()

        if NvsExtract(LORA_S).retval() == '1':
            self.LoRa_Setup()

        # not yet complete

    def Sensor_Setup(self):
        # Using Pysense board currently, so we will employ those sensors

    def WiFi_Setup(self):
        # Use nvram values to connect to a WiFi

    def MQTT_Setup(self):
        # Connect to a mqtt server

    def LoRa_Setup(self):
        # connect to a LoRaWAN gateway

    def LTE_Setup(self):
        # connect to the internet using LTE
