from network import Bluetooth
import pycom


class BLE()
""" This class initializes the BLE mode in the fipy and also checks
    if the BLE mode param is on or not """"

    def __init__(self, name, uuid):

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
        boot_service = self.ble.service(uuid=b'1234567890123456', isprimary=True, nbr_chars=5)
        wifi_service = self.ble.service(uuid=b'a234567890123456', isprimary=True, nbr_chars=2)
        lora_service = self.ble.service(uuid=b'b234567890123456', isprimary=True, nbr_chars=3)
        lte_service = self.ble.service(uuid=b'c234567890123456', isprimary=True, nbr_chars=2)
        # characteristic / service declarations
        deploy_f = boot_serv.characteristic(uuid=b'1000', value=0)
        pycom.nvs_set('mode', 0)
        # generic services
        wifi_f = boot_service.characteristic(uuid=b'2000', value=0)
        pycom.nvs_set('wifi', 0)
        lora_f = boot_service.characteristic(uuid=b'2001', value=0)
        pycom.nvs_set('lora', 0)
        lte_f = boot_service.characteristic(uuid=b'2002', value=0)
        pycom.nvs_set('lte', 0)
        # wifi_service chars
        wifi_ssid = wifi_service.characteristic(uuid=b'3000', value=0)
        pycom.nvs_set('wifi_ssid', 0)
        wifi_pass = wifi_service.characteristic(uuid=b'3001', vaue=0)
        pycom.nvs_set('wifi_pass', 0)
        # lora_service chars
        lora_appkey = lora_service.characteristic(uuid=b'4000', value=0)
        pycom.nvs_set('appkey', 0)
        lora_appSkey = lora_service.characteristic(uuid=b'4001', value=0)
        pycom.nvs_set('appSkey', 0)
        lora_nwkSkey = lora_service.characteristic(uuid=b'4002', value=0)
        pycom.nvs_set('nwkSkey', 0)
        # lte_service chars


        deploy_f_cb = deploy_f.callback(trigger=self.ble.CHAR_WRITE_EVENT | self.ble.CHAR_READ_EVENT, handler=deploy_cb_handler)



    def char_cb_handler(chr):
        # handles write and read requests from the client
        events = chr.events()
        if events & self.ble.CHAR_WRITE_EVENT:
            print("Value written is {}".format(chr.value()))

        elif events & self.ble.CHAR_READ_EVENT:
            print("Read requested")
