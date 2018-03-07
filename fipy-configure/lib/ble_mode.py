from network import Bluetooth
import pycom
from nvstring import NvsStore
from machine import reset

class BLE():
# This class initializes the BLE mode in the fipy and also checks
# if the BLE mode param is on or not

    def __init__(self, name, uuid):
        self.ble = Bluetooth()
        self.ble.set_advertisement(name=name, service_uuid=uuid)
        self.setup()

    def connect_cb(self, bt_o):
        # callback for connection
        events = bt_o.events()
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")

    def setup(self):
        # sets up all the services and characteristics
        self.ble.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.connect_cb)
        self.ble.advertise(True)
        # main service switches
        restart_service = self.ble.service(uuid=0x0000, isprimary=True, nbr_chars=1)
        boot_service = self.ble.service(uuid=0xfff0, isprimary=True, nbr_chars=5)
        wifi_service = self.ble.service(uuid=0xfff1, isprimary=True, nbr_chars=2)
        mqtt_service = self.ble.service(uuid=0xfff1a, isprimary=True, nbr_chars=2)
        lora_service = self.ble.service(uuid=0xfff2, isprimary=True, nbr_chars=3)
        lte_service = self.ble.service(uuid=0xfff3, isprimary=True, nbr_chars=1)
        sensor_service = self.ble.service(uuid=0xfff4, isprimary=True, nbr_chars=3)
        # characteristic / service declarations
        self.mode_f = boot_service.characteristic(uuid=0x1000, value=0)
        pycom.nvs_set('mode', 0)
        # generic services to be added to boot service
        self.wifi_f = boot_service.characteristic(uuid=0x2000, value=0)
        pycom.nvs_set('wifi', 0)
        self.mqtt_f = boot_service.characteristic(uuid=0x20001, value=0)
        pycom.nvs_set('mqtt', 0)
        self.lora_f = boot_service.characteristic(uuid=0x2001, value=0)
        pycom.nvs_set('lora', 0)
        self.lte_f = boot_service.characteristic(uuid=0x2002, value=0)
        pycom.nvs_set('lte', 0)

        # restart declaration
        self.restart_f = restart_service.characteristic(uuid=0x0001, value=0)

        # wifi_service chars
        self.wifi_ssid = wifi_service.characteristic(uuid=0x3000, value=0)
        self.wifi_pass = wifi_service.characteristic(uuid=0x3001, value=0)

        # mqtt_service chars
        self.mqtt_server = mqtt_service.characteristic(uuid=0x3000a, value=0)
        self.mqtt_port = mqtt_service.characteristic(uuid=0x3000b, value=0)

        # lora_service chars
        self.lora_appkey = lora_service.characteristic(uuid=0x4000, value=0)
        self.lora_appSkey = lora_service.characteristic(uuid=0x4001, value=0)
        self.lora_nwkSkey = lora_service.characteristic(uuid=0x4002, value=0)

        # sensor_service chars -> light, pressure, humidity, temperature, altitude


        # callbacks to deploy_handler which will use the switch_dict to switch between chars
        mode_f_cb = self.mode_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        wifi_f_cb = self.wifi_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        lora_f_cb = self.lora_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        lte_f_cb = self.lte_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)

        # restart details callback
        restart_f_cb = self.restart_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.restart_handler)

        # wifi details callback
        wifi_cb1 = self.wifi_ssid.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.wifi_handler)
        wifi_cb2 = self.wifi_ssid.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.wifi_handler)

        # mqtt details callback
        mqtt_cb1 = self.mqtt_server.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.mqtt_handler)
        mqtt_cb2 = self.mqtt_port.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.mqtt_handler)

        # lora details callback
        lora_cb1 = self.lora_appkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.lora_handler)
        lora_cb2 = self.lora_appSkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.lora_handler)
        lora_cb3 = self.lora_nwkSkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.lora_handler)

        # sensor details callback

    def deploy_handler(self,chr):
        # handles write and read requests from the client
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value()
            if val[2] == '0':
                self.mode_f.value(val[1])
                NvsStore('mode', val[1])
            elif val[2] == '1':
                self.wifi_f.value(val[1])
                NvsStore('wifi', val[1])
            elif val[2] == '2':
                self.lora_f.value(val[1])
                NvsStore('lora', val[1])
            elif val[2] == '3':
                self.lte_f.value(val[1])
                NvsStore('lte', val[1])
            else:
                pass

        elif events & Bluetooth.CHAR_READ_EVENT:
            return "REJECTED"

    def wifi_handler(self,chr):
        # handles writing the wifi ssid and password
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value()
            if val[0] == '0':
                self.wifi_ssid.value(val[1:])
                NvsStore('ssid', val[1:])
            elif val[0] == '1':
                self.wifi_pass.value(val[1:])
                NvsStore('pass', val[1:])
        elif events & Bluetooth.CHAR_READ_EVENT:
            print("Connected to ssid: " + chr.value())

    def lora_handler(self,chr):
        # handles writing the lora appkey, appSkey and nwkSkey
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value()
            if val[0] == '0':
                self.lora_appkey.value(val[1:])
                NvsStore('appkey', val[1:])
            elif val[0] == '1':
                self.lora_appSkey.value(val[1:])
                NvsStore('appSkey', val[1:])
            elif val[0] == '2':
                self.lora_nwkSkey.value(val[1:])
                NvsStore('nwkSkey', val[1:])
        elif events & Bluetooth.CHAR_READ_EVENT:
            print("Connected to lora appkey: " + self.lora_appkey.value())

    def restart_handler(self,chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            print(chr.value())
            val = chr.value()
            if val == b'1':
                reset() # hard reset resets hardware and software except firmware loaded
            else:
                print("Breach")

    def mqtt_handler(self, chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            if val[0] == '0':
                self.wifi_ssid.value(val[1:])
                NvsStore('server', val[1:])
            elif val[0] == '1':
                self.wifi_pass.value(val[1:])
                NvsStore('port', val[1:])
        elif events & Bluetooth.CHAR_READ_EVENT:
            print("Connected to server: " + self.mqtt_server.value())
