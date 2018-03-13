import pycom
import time
from network import WLAN
from nvstring import NvsExtract
from machine import reset, idle
from mqtt import MQTTClient
from SI7006A20 import SI7006A20
from MPL3115A2 import MPL3115A2
from LIS2HH12 import LIS2HH12
from LTR329ALS01 import LTR329ALS01
from machine import Timer
from lorawan import LoraNode
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
        self.sensactive = 0

    def boot_up(self):
        # start the deploy mode setup by doing all the checks
        if NvsExtract(WIFI_S).retval() == '1':
            self.WiFi_Setup()

        if NvsExtract(MQTT_S).retval() == '1':
            self.MQTT_Setup()

        if NvsExtract(LORA_S).retval() == '1':
            self.LoRa_Setup()
            self.lora_send(self.sensactive)

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
        if self.active  == 1:
            # alarm basically used for callbacks to prevent polling
            pub_t = Timer.alarm(self.mqtt_publish, self.tFrequency, periodic=True)

    def t_publish(self, freq):
        self.client.publish("temperature", self.temp_sensor.temperature())
        self.client.publish("humidity", self.temp_sensor.humidity())


    def LoRa_Setup(self):
        self.instance = LoraNode(NvsExtract('appKey'), NvsExtract('appSkey'), NvsExtract('nwkSkey'))
        if arg == 0:
            self.Sensor_Setup()
            send_t = Timer.alarm(self.lora_send_temp, self.tFrequency, periodic=True)
            send_alt = Timer.alarm(self.lora_send_alt, self.altFrequency, periodic=True)
            send_accl = Timer.alarm(self.lora_send_accl, self.acclFrequency, periodic=True)
            send_light = Timer.alarm(self.lora_send_light, self.lightFrequency, periodic=True)
        else:
            pass
        # connect to a LoRaWAN gateway
    def lora_send_temp(self):
        self.instance.sendData(str(self.temp_sensor.temperature))
        self.instance.sendData(str(self.temp_sensor.humidity))

    def lora_send_alt(self):
        self.instance.sendData(str(self.alt_sensor.temperature))

    def lora_send_accl(self):
        self.instance.sendData(str(self.accl_sensor.temperature))
        self.instance.sendData(str(self.accl_sensor.humidity))

    def lora_send_light(self):
        self.instance.sendData(str(self.light_sensor.temperature))

    def Sensor_Setup(self):
        self.sensactive = 1
        # Using Pysense board currently, so we will employ those sensors
        if NvsExtract(TEMP) == '1':
            self.tFrequency = int(NvsExtract(TEMP_F))
            self.temp_sensor = SI7006A20()
            self.active = 1
        if NvsExtract(ALT) == '1':
            self.altFrequency = int(NvsExtract(ALT_F))
            self.alt_sensor = MPL3115A2()
            self.active = 1
        if NvsExtract(ACCL) == '1':
            self.acclFrequency = int(NvsExtract(ACCL_F))
            self.accl_sensor = LIS2HH12()
            self.active = 1
        if NvsExtract(LIGHT) == '1':
            self.lightFrequency = int(NvsExtract(LIGHT_F))
            self.light_sensor = LTR329ALS01()
            self.active = 1
        else:
            self.tFrequency = 0
            self.altFrequency = 0
            self.acclFrequency = 0
            self.lightFrequency = 0
            self.active = 0
