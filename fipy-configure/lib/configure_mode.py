from network import Bluetooth
import pycom
from nvstring import NvsStore, NvsExtract
import machine
import binascii
from network import LoRa


class BLE():
# This class initializes the BLE mode in the fipy and also checks
# if the BLE mode param is on or not

    def __init__(self, name, uuid):
        self.ble = Bluetooth()
        self.ble.set_advertisement(name=name, service_uuid=uuid)
        self.setup()

    def connect_cb(self, bt_o):
        # callback for connection
        print('enter connect_cb\n')
        events = bt_o.events()
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")

    def setup(self):
        # sets up all the services and characteristics
        print("Enter Setup\n")
        self.ble.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.connect_cb)
        self.ble.advertise(True)
        # main service switches
        config_service = self.ble.service(uuid=0xfff0, isprimary=True, nbr_chars=1)
        # main service
        self.message = config_service.characteristic(uuid=0x0001, value=0)
        # nvram declarations
        pycom.nvs_set('id', 0)
        pycom.nvs_set('mode', 0)
        pycom.nvs_set('wifi', 0)
        pycom.nvs_set('mqtt', 0)
        pycom.nvs_set('lora', 0)
        pycom.nvs_set('ssid', 0)
        pycom.nvs_set('pass', 0)
        pycom.nvs_set('server', 0)
        pycom.nvs_set('port', 0)
        pycom.nvs_set('appSkey', 0)
        pycom.nvs_set('nwkSkey', 0)
        pycom.nvs_set('temp_sensor', 0)
        pycom.nvs_set('temp_f', 0)
        pycom.nvs_set('accl_sensor', 0)
        pycom.nvs_set('accl_f', 0)
        pycom.nvs_set('alt_sensor', 0)
        pycom.nvs_set('alt_f', 0)
        pycom.nvs_set('light_sensor', 0)
        pycom.nvs_set('light_f', 0)
        # callbacks to deploy_handler which will use the switch_dict to switch between chars
        msg_cb = self.message.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.msg_handler)
        # restart details callback)

        print("waiting for callback")

    def m_handler(self,chr):
        print("Entered Deploy Handler\n")
        # handles write and read requests from the client
        msg = chr.value().decode('utf-8')
        msg_list = msg.split(";")
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
                NvsStore('id', msg_list[0])
                if msg_list[2] == 1:
                    NvsStore('wifi', msg_list[2])
                    NvsStore('ssid', msg_list[5])
                    NvsStore('pass', msg_list[6])
                else:
                    pycom.nvs_set('wifi', 0)

                if msg_list[3] == 1:
                    NvsStore('mqtt', msg_list[3])
                    NvsStore('server', msg_list[7])
                    NvsStore('port', msg_list[8])
                else:
                    pycom.nvs_set('mqtt', 0)

                if msg_list[4] == 1:
                    NvsStore('lora', msg_list[3])
                    NvsStore('ssid', msg_list[9])
                    NvsStore('pass', msg_list[10])
                else:
                    pycom.nvs_set('mqtt', 0)

                if msg_list[11] != 0:
                    NvsStore('temp_sensor', '1')
                    NvsStore('temp_f', msg_list[11])
                else:
                    pycom.nvs_set('temp_sensor', 0)

                if msg_list[12] != 0:
                    NvsStore('alt_sensor', '1')
                    NvsStore('alt_f', msg_list[12])
                else:
                    pycom.nvs_set('alt_sensor', 0)

                if msg_list[13] != 0:
                    NvsStore('accl_sensor', '1')
                    NvsStore('accl_f', msg_list[13])
                else:
                    pycom.nvs_set('accl_sensor', 0)

                if msg_list[14] != 0:
                    NvsStore('light_sensor', '1')
                    NvsStore('light_f', msg_list[14])
                else:
                    pycom.nvs_set('light_sensor', 0)

                if (int(msg_list[2]) & int(msg_list[3])) | int(msg_list[4]):
                    NvsStore('mode', 0)
                    machine.reset()
                    break

                NvsStore('mode', '1')
                machine.reset()

            if events & Bluetooth.CHAR_READ_EVENT:
                NvsStore('deveui', binascii.hexlify(LoRa().mac()).decode('utf-8'))
                return binascii.hexlify(LoRa().mac()).decode('utf-8')
