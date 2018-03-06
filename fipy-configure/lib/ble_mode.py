from network import Bluetooth
import pycom
from nvstring import NvsStore
from machine import reset

class BLE():
""" This class initializes the BLE mode in the fipy and also checks
    if the BLE mode param is on or not """"

    def __init__(self, name, uuid):
        self.ble = Bluetooth()
        self.setup()

    def connect_cb(self, bt_o):
        # callback for connection
        events = bt_0.events()
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")

    def setup(self):
        # sets up all the services and characteristics
        self.ble.set_advertisement(name='tQb IoT', service_uuid=b'1234567890123456')
        self.ble.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, hander=self.conn_cb)
        self.ble.advertise(True)
        # main service switches
        restart_service = self.ble.service(uuid='0000', isprimary=True, nr_chars=1)
        boot_service = self.ble.service(uuid='fff0', isprimary=True, nbr_chars=4)
        wifi_service = self.ble.service(uuid='fff1', isprimary=True, nbr_chars=2)
        lora_service = self.ble.service(uuid='fff2', isprimary=True, nbr_chars=3)
        lte_service = self.ble.service(uuid='fff3', isprimary=True, nbr_chars=1)
        # characteristic / service declarations
        self.mode_f = boot_serv.characteristic(uuid=b'1000', value=0)
        pycom.nvs_set('mode', 0)
        # generic services
        self.wifi_f = wifi_service.characteristic(uuid=b'2000', value=0)
        pycom.nvs_set('wifi', 0)
        self.lora_f = boot_service.characteristic(uuid=b'2001', value=0)
        pycom.nvs_set('lora', 0)
        self.lte_f = boot_service.characteristic(uuid=b'2002', value=0)
        pycom.nvs_set('lte', 0)
        # restart declaration
        self.restart_f = restart_service.characteristic(uuid=b'0001', value=0)
        # wifi_service chars
        self.wifi_ssid = wifi_service.characteristic(uuid=b'3000', value=0)
        self.wifi_pass = wifi_service.characteristic(uuid=b'3001', vaue=0)
        # lora_service chars
        self.lora_appkey = lora_service.characteristic(uuid=b'4000', value=0)
        self.lora_appSkey = lora_service.characteristic(uuid=b'4001', value=0)
        self.lora_nwkSkey = lora_service.characteristic(uuid=b'4002', value=0)
        # callbacks to deploy_handler which will use the switch_dict to switch between chars
        mode_f_cb = self.mode_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)
        wifi_f_cb = self.wifi_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)
        lora_f_cb = self.lora_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)
        lte_f_cb = self.lte_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)
        # restart details callback
        restart_f_cb = self.restart_handler(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=restart_handler)
        # wifi details callback
        wifi_cb1 = self.wifi_ssid.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=wifi_handler)
        wifi_cb2 = self.wifi_ssid.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=wifi_handler)
        # lora details callback
        lora_cb1 = self.lora_appkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=lora_handler)
        lora_cb2 = self.lora_appSkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=lora_handler)
        lora_cb3 = self.lora_nwkSkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=lora_handler)

    def deploy_handler(chr):
        # handles write and read requests from the client
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value()
            if val[0] == "0":
                self.mode_f.value(val[1])
                NvsStore('mode', val[1])
            elif val[0] == "1":
                self.wifi_f.value(val[1])
                NvsStore('wifi', val[1])
            elif val[0] == "2":
                self.lora_f.value(val[1])
                NvsStore('lora', val[1])
            elif val[0] == "3":
                self.lte_f.value(val[1])
                NvsStore('lte', val[1])
            else:
                pass

        elif events & Bluetooth.CHAR_READ_EVENT:
            return "REJECTED"

    def wifi_handler(chr):
        # handles writing the wifi ssid and password
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value()
            if val[0] == "0":
                self.wifi_ssid.value(val[1:])
                NvsStore('ssid', val[1:])
            elif val[0] == "1":
                self.wifi_pass.value(val[1:])
                NvsStore('pass', val[1:])
        elif events & Bluetooth.CHAR_READ_EVENT:
            print("Connected to ssid: " + chr.value())

    def lora_handler(chr):
        # handles writing the lora appkey, appSkey and nwkSkey
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value()
            if val[0] == "0":
                self.lora_appkey.value(val[1:])
                NvsStore('appkey', val[1:])
            elif val[0] == "1":
                self.lora_appSkey.value(val[1:])
                NvsStore('appSkey', val[1:])
            elif val[0] == '2':
                self.lora_nwkSkey.value(val[1:])
                NvsStore('nwkSkey', val[1:])
        elif events & Bluetooth.CHAR_READ_EVENT:
            print("Connected to lora appkey: " + self.lora_appkey.value())

    def restart_handler(chr):
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value()
            if val == "1":
                reset() # hard reset resets hardware and software except firmware loaded
            else:
                print("Breach")
