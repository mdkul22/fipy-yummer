import pycom
import json
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
from network import LoRa
import binascii
import struct
import socket
# all variables
# switches
ID = "id"
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
NWKSKEY = "nwkskey"
# SENSORS
TEMP = "temp_sensor"
ALT = "alt_sensor"
ACCL = "accl_sensor"
LIGHT = "light_sensor"
# freqs
TEMP_F = "temp_f"
ALT_F = "alt_f"
ACCL_F = "accl_f"
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
        self.id = NvsExtract(ID).retval()
        self.client = MQTTClient(self.id, NvsExtract(M_SERVER).retval(), port=int(NvsExtract(M_PORT).retval()))
        self.client.connect()
        print("MQTT Connected")
        self.Sensor_Setup()
        if self.active  == 1:
            # alarm basically used for callbacks to prevent polling
            print("alarm")
            pub_t1 = Timer.Alarm(self.temp_publish, float(self.tFrequency), arg=1, periodic=True)
            time.sleep(0.1)
            pub_t2= Timer.Alarm(self.temp_publish, float(self.tFrequency), arg=2, periodic=True)
            time.sleep(0.1)
            pub_alt = Timer.Alarm(self.alt_publish, float(self.altFrequency), arg=self.alt_sensor.altitude(), periodic=True)
            time.sleep(0.1)
            pub_accl1 = Timer.Alarm(self.accl_publish, float(self.acclFrequency), arg=1, periodic=True)
            time.sleep(0.1)
            pub_accl2 = Timer.Alarm(self.accl_publish, float(self.acclFrequency), arg=2, periodic=True)
            time.sleep(0.1)
            pub_light = Timer.Alarm(self.light_publish, float(self.lightFrequency), arg=self.light_sensor.light(), periodic=True)

    def temp_publish(self, v):
        if v == 1:
            print(self.temp_sensor.temperature())
            self.client.publish(self.id+"/temperature", str(self.temp_sensor.temperature()))
        if v == 2:
            self.client.publish(self.id+"/humidity", str(self.temp_sensor.humidity()))

    def alt_publish(self, v):
        print(v)
        self.client.publish(self.id+"/altitude", str(v))

    def accl_publish(self, v):
        if v == 1:
            self.client.publish(self.id+"/roll", str(self.accl_sensor.roll()))
        if v == 2:
            self.client.publish(self.id+"/pitch", str(self.accl_sensor.pitch()))

    def light_publish(self, v):
        self.client.publish(self.id+"/light", str(v))
    # Major LoRa setup, though main setup happens in lorawan library
    def LoRa_Setup(self):
        lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
        DevUi = binascii.hexlify(LoRa().mac())
        dev_addr = struct.unpack(">l", binascii.unhexlify('90 53 07 24'.replace(' ','')))[0]
        print(NvsExtract(NWKSKEY).retval())
        print("2B7E151628AED2A6ABF7158809CF4F3C")
        nwk_swkey = binascii.unhexlify(NvsExtract(NWKSKEY).retval())
        app_swkey = binascii.unhexlify(NvsExtract(APPSKEY).retval())
        lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
        print("Done")
        # create a LoRa socket
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

        # set the LoRaWAN data rate
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
        self.s.bind(5)
        # make the socket non-blocking
        self.s.setblocking(True)
        self.Sensor_Setup()
        # instead of polling, we put soft interrupts
        send_t = Timer.Alarm(self.lora_send_temp, float(self.tFrequency)*20.0, periodic=True)
#        time.sleep(2)
#        send_alt = Timer.Alarm(self.lora_send_alt, float(self.altFrequency)*30.0, periodic=True)
#        time.sleep(2)
#        send_accl = Timer.Alarm(self.lora_send_accl, float(self.acclFrequency)*25.0, periodic=True)
#        time.sleep(2)
#        send_light = Timer.Alarm(self.lora_send_light, float(self.lightFrequency)*25.0, periodic=True)
        print("Done")
        # connect to a LoRaWAN gateway

    def lora_send_temp(self, arg):
        print("sent temp")
        x = self.temp_sensor.temperature()
        y = self.temp_sensor.humidity()
        dict = {"temp": x, "humidity": y}
        msg = json.dumps(dict)
        self.s.send(msg)

    def lora_send_alt(self, arg):
        # altitude based on pressure
        print("sent alt")
        self.s.send(msg)

    def lora_send_accl(self, arg):
        # roll and pitch values
        print("sent accl")
        self.s.send(msg)

    def lora_send_light(self, arg):
        # only 400 nm i.e channel 0 or mainly blue spectrum light
        # supposedly detects white light better
        print("sent light")
        self.s.send(msg)

    def Sensor_Setup(self):
        # Using Pysense board currently, so we will employ those sensors
        if NvsExtract(TEMP).retval() == '1':
            print("Enter Temp")
            self.tFrequency = int(NvsExtract(TEMP_F).retval())
            self.temp_sensor = SI7006A20()
            self.active = 1
        if NvsExtract(ALT).retval() == '1':
            self.altFrequency = int(NvsExtract(ALT_F).retval())
            self.alt_sensor = MPL3115A2()
            self.active = 1
        if NvsExtract(ACCL).retval() == '1':
            self.acclFrequency = int(NvsExtract(ACCL_F).retval())
            self.accl_sensor = LIS2HH12()
            self.active = 1
        if NvsExtract(LIGHT).retval() == '1':
            self.lightFrequency = int(NvsExtract(LIGHT_F).retval())
            self.light_sensor = LTR329ALS01()
            self.active = 1
        else:
            self.tFrequency = 0
            self.altFrequency = 0
            self.acclFrequency = 0
            self.lightFrequency = 0
            self.active = 0
        print("self active is " + str(self.active))
