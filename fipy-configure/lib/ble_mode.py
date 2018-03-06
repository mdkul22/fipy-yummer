from network import Bluetooth
import pycom
from nvstring import NvsStore

class BLE():
""" This class initializes the BLE mode in the fipy and also checks
    if the BLE mode param is on or not """"

    def __init__(self, name, uuid):
        C_BOOT_MODE = "mode"
        # on/off switches
        C_WIFI = "wifi"
        C_LORA = "lora"
        C_LTE = "LTE"
        # wifi strings
        C_SSID = "ssid"
        C_PASS = "password"
        # lora strings
        C_APPKEY = "appkey"
        C_APPSKEY = "appSkey"
        C_NWKSKEY = "nwkSkey"
        # dicts are used for handle multiple buttons under one callback
        self.switch_dict = {C_BOOT_MODE:"0", C_WIFI:"0", C_LORA:"0", C_LTE= "0"}
        self.wifi_dict = {C_SSID:"0", C_PASS = "0"}
        self.lora_dict = {C_APPKEY:"0", C_APPSKEY="0", C_NWKSKEY="0"}
        self.ble = Bluetooth()

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
        boot_service = self.ble.service(uuid='fff0', isprimary=True, nbr_chars=4)
        wifi_service = self.ble.service(uuid='fff1', isprimary=True, nbr_chars=2)
        lora_service = self.ble.service(uuid='fff2', isprimary=True, nbr_chars=3)
        lte_service = self.ble.service(uuid='fff3', isprimary=True, nbr_chars=1)
        # characteristic / service declarations
        mode_f = boot_serv.characteristic(uuid=b'1000', value=0)
        pycom.nvs_set('mode', 0)
        # generic services
        wifi_f = wifi_service.characteristic(uuid=b'2000', value=0)
        pycom.nvs_set('wifi', 0)
        lora_f = boot_service.characteristic(uuid=b'2001', value=0)
        pycom.nvs_set('lora', 0)
        lte_f = boot_service.characteristic(uuid=b'2002', value=0)
        pycom.nvs_set('lte', 0)
        # wifi_service chars
        wifi_ssid = wifi_service.characteristic(uuid=b'3000', value=0)
        wifi_pass = wifi_service.characteristic(uuid=b'3001', vaue=0)

        # lora_service chars
        lora_appkey = lora_service.characteristic(uuid=b'4000', value=0)
        lora_appSkey = lora_service.characteristic(uuid=b'4001', value=0)
        lora_nwkSkey = lora_service.characteristic(uuid=b'4002', value=0)

        # callbacks to deploy_handler which will use the switch_dict to switch between chars
        mode_f_cb = mode_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)
        wifi_f_cb = wifi_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)
        lora_f_cb = lora_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)
        lite_f_cb = lte_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=deploy_handler)

    def deploy_handler(chr):
        # handles write and read requests from the client
        events = chr.events()
        if events & self.ble.CHAR_WRITE_EVENT:
            print("Value written is {}".format(chr.value()))

        elif events & self.ble.CHAR_READ_EVENT:
            print("Read requested")

    def wifi_handler(chr):
        # handles writing the wifi ssid and password
        events = chr.events()
        if events & self.ble.CHAR_WRITE_EVENT:

    def lora_handler(chr):
