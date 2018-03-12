import pycom
import time
from network import WLAN
from nvstring import NvsExtract
from machine import reset, idle
from mqtt import MQTTClient
from SI7006A20 import SI7006A20
from machine import Timer
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
# SENSORS
TEMP = "tempsensor"
ALT = "altsensor"
ACCL = "acclsensor"
LIGHT = "lightsensor"
# freqs
TEMP_F = "temp_f"
ALT_F = "alt_f"
ACCL = "accl_f"
LIGHT_F = "light_f"
class Deploy():
# deploy mode
    def __init__(self):
        self.__Init()

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
    def WiFi_Setup(self):
        # Use nvram values to connect to a WiFi
        wlan = WLAN(mode=WLAN.STA)
        wlan.antenna(WLAN.EXT_ANT)
        NvsExtract(SSID)
        wlan.connect(NvsExtract(SSID).retval(),auth=(WLAN.WPA2, NvsExtract(PASS).retval()), timeout=5000)

        while not wlan.isconnected():
            idle()

        print("Connected to WiFi\n")

    def MQTT_Setup(self):
        # Connect to a mqtt server
        self.client = MQTTClient("FiPy", NvsExtract(M_SERVER).retval(), port=int(NvsExtract(M_PORT).retval()))
        self.client.connect()
        print("MQTT Connected")
        self.Sensor_Setup()
        if self.tFrequency  != 0:
            # alarm basically used for callbacks to prevent polling
            pub_t = Timer.alarm(self.mqtt_publish, self.tFrequency, periodic=True)

    def t_publish(self, freq):
        temp_sensor = SI7006A20()
        self.client.publish("temperature", temp_sensor.temperature())
        self.client.publish("humidity", temp_sensor.humidity())


    def LoRa_Setup(self):
        pass
        # connect to a LoRaWAN gateway

    def Sensor_Setup(self):
        # Using Pysense board currently, so we will employ those sensors
        if NvsExtract(TEMP) == '1':
            self.tFrequency = int(NvsExtract(TEMP_F))
        if NvsExtract(ALT) == '1':
            self.altFrequency = int(NvsExtract(ALT_F))
        if NvsExtract(ACCL) == '1':
            self.acclFrequency = int(NvsExtract(ACCL_F))
        if NvsExtract(LIGHT) == '1':
            self.lightFrequency = int(NvsExtract(LIGHT_F))
        else:
            self.tFrequency = 0
            self.altFrequency = 0
            self.acclFrequency = 0
            self.lightFrequency = 0
