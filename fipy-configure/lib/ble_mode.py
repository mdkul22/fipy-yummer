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

        #
        deploy_f = boot_serv.characteristic(uuid=b'a234567890123456', value=0)
        pycom.nvs_set('mode', 0)
        
        deploy_f_cb = deploy_f.callback(trigger=self.ble.CHAR_WRITE_EVENT | self.ble.CHAR_READ_EVENT, handler=deploy_cb_handler)


    def char_cb_handler(chr):
        # handles write and read requests from the client
        events = chr.events()
        if events & self.ble.CHAR_WRITE_EVENT:
            print("Value written is {}".format(chr.value()))

        else:
            print("Read requested")

    def
