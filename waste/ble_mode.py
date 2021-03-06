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
        boot_service = self.ble.service(uuid=0xfff0, isprimary=True, nbr_chars=5)
        wifi_service = self.ble.service(uuid=0xfff1, isprimary=True, nbr_chars=2)
        mqtt_service = self.ble.service(uuid=0xfff2, isprimary=True, nbr_chars=2)
        lora_service = self.ble.service(uuid=0xfff3, isprimary=True, nbr_chars=3)
        restart_service = self.ble.service(uuid=0xfff4, isprimary=True, nbr_chars=1)
        #lte_service = self.ble.service(uuid=0xfff3, isprimary=True, nbr_chars=1)
        misc_service = self.ble.service(uuid=0xfff5, isprimary=True, nbr_chars=4)

        # characteristic / service declarations
        self.id_f = boot_service.characteristic(uuid=0x01, value=0)
        pycom.nvs_set('id', 0)
        self.mode_f = boot_service.characteristic(uuid=0x02, value=0)
        pycom.nvs_set('mode', 0)
        # generic services to be added to boot service
        self.wifi_f = boot_service.characteristic(uuid=0x03, value=0)
        pycom.nvs_set('wifi', 0)
        self.mqtt_f = boot_service.characteristic(uuid=0x04, value=0)
        pycom.nvs_set('mqtt', 0)
        self.lora_f = boot_service.characteristic(uuid=0x05, value=0)
        pycom.nvs_set('lora', 0)
        #self.lte_f = boot_service.characteristic(uuid=0x2002, value=0)
        #pycom.nvs_set('lte', 0)

        # restart declaration
        self.restart_f = restart_service.characteristic(uuid=0x01, value=0)

        # wifi_service chars
        self.wifi_ssid = wifi_service.characteristic(uuid=0x01, value=0)
        self.wifi_pass = wifi_service.characteristic(uuid=0x02, value=0)

        # mqtt_service chars
        self.mqtt_server = mqtt_service.characteristic(uuid=0x03, value=0)
        self.mqtt_port = mqtt_service.characteristic(uuid=0x04, value=0)

        # lora_service chars
        self.lora_deveui = lora_service.characteristic(uuid=0x01, value=0)
        self.lora_appSkey = lora_service.characteristic(uuid=0x02, value=0)
        self.lora_nwkSkey = lora_service.characteristic(uuid=0x03, value=0)

        # sensor_service chars -> light, pressure, humidity, temperature, altitude
        self.temp_sensor = misc_service.characteristic(uuid=0x01, value=0)
        self.alt_sensor = misc_service.characteristic(uuid=0x03, value=0)
        self.accl_sensor = misc_service.characteristic(uuid=0x05, value=0)
        self.light_sensor = misc_service.characteristic(uuid=0x07, value=0)

        # callbacks to deploy_handler which will use the switch_dict to switch between chars
        id_f_cb = self.id_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        mode_f_cb = self.mode_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        wifi_f_cb = self.wifi_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        mqtt_f_cb = self.mqtt_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        lora_f_cb = self.lora_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)
        #lte_f_cb = self.lte_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.deploy_handler)

        # restart details callback
        restart_f_cb = self.restart_f.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.restart_handler)

        # wifi details callback
        wifi_cb1 = self.wifi_ssid.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.wifi_handler)
        wifi_cb2 = self.wifi_pass.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.wifi_handler)
        print("Enter callback mqtt\n")
        # mqtt details callback
        mqtt_cb1 = self.mqtt_server.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.mqtt_handler)
        mqtt_cb2 = self.mqtt_port.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.mqtt_handler)

        # lora details callback
        lora_cb1 = self.lora_deveui.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.lora_handler)
        lora_cb2 = self.lora_appSkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.lora_handler)
        lora_cb3 = self.lora_nwkSkey.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.lora_handler)

        # sensor details callback
        temp_sensor_cb = self.temp_sensor.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.sensor_handler)
        alt_sensor_cb = self.alt_sensor.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.sensor_handler)
        accl_sensor_cb = self.accl_sensor.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.sensor_handler)
        light_sensor_cb = self.light_sensor.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.sensor_handler)
        print("setup done/n")

    def deploy_handler(self,chr):
        print("Entered Deploy Handler\n")
        # handles write and read requests from the client
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value().decode('utf-8')
            print(val[0])
            print(val)
            if val[0] == '0':
                self.id_f.value(val[1:])
                NvsStore('id', val[1:])
            if val[0] == '1':
                self.mode_f.value(val[1])
                NvsStore('mode', val[1])
            elif val[0] == '2':
                self.wifi_f.value(val[1])
                NvsStore('wifi', val[1])
            elif val[0] == '3':
                self.mqtt_f.value(val[1])
                NvsStore('mqtt', val[1])
            elif val[0] == '4':
                self.lora_f.value(val[1])
                NvsStore('lora', val[1])
            else:
                pass
        elif events & Bluetooth.CHAR_READ_EVENT:
            return "REJECTED"

    def wifi_handler(self,chr):
        print("Wifi Handler\n")
        # handles writing the wifi ssid and password
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value().decode("utf-8")
            print(val)
            if val[0] == '0':
                self.wifi_ssid.value(val[1:])
                x = val[1:]
                NvsStore('ssid', x)
                print(NvsExtract('ssid').retval())
            elif val[0] == '1':
                self.wifi_pass.value(val[1:])
                NvsStore('pass', val[1:])
                print(NvsExtract('pass').retval())
        elif events & Bluetooth.CHAR_READ_EVENT:
            try:
                print("Connected to ssid: " + x)
            except NameError:
                print("not declared yet")
        print("exit")

    def lora_handler(self,chr):
        # handles writing the lora deveui, appSkey and nwkSkey
        events = chr.events()
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value().decode('utf-8')
            if val[0] == '0':
                NvsStore('deveui', binascii.hexlify(LoRa().mac()).decode('utf-8'))
            elif val[0] == '1':
                self.lora_appSkey.value(val[1:])
                NvsStore('appSkey', val[1:])
            elif val[0] == '2':
                self.lora_nwkSkey.value(val[1:])
                NvsStore('nwkSkey', val[1:])
        elif events & Bluetooth.CHAR_READ_EVENT:
            return binascii.hexlify(LoRa().mac()).decode('utf-8')

    def restart_handler(self,chr):
        events = chr.events()
        print("restart handler\n")
        if events & Bluetooth.CHAR_WRITE_EVENT:
            val = chr.value().decode("utf-8")
            if val == b'1':
                machine.reset() # hard reset resets hardware and software except firmware loaded
            else:
                print("Breach")

    def mqtt_handler(self, chr):
        print("MQTT handler")
        events = chr.events()
        val = chr.value().decode("utf-8")
        if events & Bluetooth.CHAR_WRITE_EVENT:
            if val[0] == '0':
                self.wifi_ssid.value(val[1:])
                NvsStore('server', val[1:])
            elif val[0] == '1':
                self.wifi_pass.value(val[1:])
                NvsStore('port', val[1:])
        elif events & Bluetooth.CHAR_READ_EVENT:
            print("Connected to server: " + str(self.mqtt_server.value()))

    def sensor_handler(self, chr):
        print("Sensor handler")
        events = chr.events()
        val = chr.value().decode("utf-8")
        if events & Bluetooth.CHAR_WRITE_EVENT:
            if val[0] == '0':
                self.temp_sensor.value(val[1])
                NvsStore('tempsensor', val[1])
                NvsStore('temp_f', val[2:])
            elif val[0] == '1':
                self.alt_sensor.value(val[1])
                NvsStore('altsensor', val[1])
                NvsStore('alt_f', val[2:])
            elif val[0] == '2':
                self.accl_sensor.value(val[1])
                NvsStore('acclsensor', val[1])
                NvsStore('accl_f', val[2:])
            elif val[0] == '3':
                self.light_sensor.value(val[1])
                NvsStore('lightsensor', val[1])
                NvsStore('light_f', val[2:])
        else:
            pass # for now
