import pycom
import time
from network import WLAN
from nvstring import NvsExtract
import machine
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
DEVEUI = "deveui"
APPSKEY = "appskey"
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
            machine.reset()
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
            machine.idle()

        print("Connected to WiFi\n")

    def MQTT_Setup(self):
        # Connect to a mqtt server
        self.client = MQTTClient("FiPy", NvsExtract(M_SERVER).retval(), port=int(NvsExtract(M_PORT).retval()))
        self.client.connect()
        print("MQTT Connected")
        self.Sensor_Setup()
        if self.active  == 1:
            # alarm basically used for callbacks to prevent polling
            pub_t1 = Timer.alarm(self.temp_publish, self.tFrequency, arg=1, periodic=True)
            pub_t2= Timer.alarm(self.temp_publish, self.tFrequency, arg=2, periodic=True)
            pub_alt = Timer.alarm(self.alt_publish, self.altFrequency, arg=self.alt_sensor.altitude(), periodic=True)
            pub_accl1 = Timer.alarm(self.accl_publish, self.acclFrequency, arg=1, periodic=True)
            pub_accl2 = Timer.alarm(self.accl_publish, self.acclFrequency, arg=2, periodic=True)
            pub_light = Timer.alarm(self.light_publish, self.lightFrequency, arg=self.light_sensor.light(), periodic=True)

    def temp_publish(self, v):
        if v == 1:
            self.client.publish("tQb/fipy/temperature", str(self.temp_sensor.temperature()))
        if v == 2:
            self.client.publish("tQb/fipy/humidity", str(self.temp_sensor.humidity()))

    def alt_publish(self, v):
        self.client.publish("tQb/fipy/altitude", str(v))

    def accl_publish(self, v):
        if v == 1:
            self.client.publish("tQb/fipy/roll", str(self.accl_sensor.roll()))
        if v == 2:
            self.client.publish("tQb/fipy/pitch", str(self.accl_sensor.pitch()))

    def light_publish(self, v):
        self.client.publish("tQb/fipy/light", str(v))
    # Major LoRa setup, though main setup happens in lorawan library
    def LoRa_Setup(self):
        self.instance = LoraNode(NvsExtract(DEVEUI), NvsExtract(APPSKEY), NvsExtract(NWKSKEY))
        if arg == 0:
            self.Sensor_Setup()
            # instead of polling, we put soft interrupts
            send_t = Timer.alarm(self.lora_send_temp, self.tFrequency, periodic=True)
            send_alt = Timer.alarm(self.lora_send_alt, self.altFrequency, periodic=True)
            send_accl = Timer.alarm(self.lora_send_accl, self.acclFrequency, periodic=True)
            send_light = Timer.alarm(self.lora_send_light, self.lightFrequency, periodic=True)
        else:
            pass
        # connect to a LoRaWAN gateway
    def lora_send_temp(self):
        self.instance.sendData(str(self.temp_sensor.temperature()))
        self.instance.sendData(str(self.temp_sensor.humidity()))

    def lora_send_alt(self):
        # altitude based on pressure
        self.instance.sendData(str(self.alt_sensor.altitude()))

    def lora_send_accl(self):
        # roll and pitch values
        self.instance.sendData(str(self.accl_sensor.pitch()))
        self.instance.sendData(str(self.accl_sensor.roll()))

    def lora_send_light(self):
        # only 400 nm i.e channel 0 or mainly blue spectrum light
        # supposedly detects white light better
        self.instance.sendData(str(self.light_sensor.light()[0]))

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
