# Test to check bluetooth app controls GATT server or not
from network import Bluetooth

bluetooth = Bluetooth()
bluetooth.set_advertisement(name='FiPy1', service_uuid=b'1234567890123456')

def conn_cb (bt_o):
    events = bt_o.events()
    if  events & Bluetooth.CLIENT_CONNECTED:
        print("Client connected")
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print("Client disconnected")

bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)

bluetooth.advertise(True)

srv1 = bluetooth.service(uuid=b'1234567890123456', isprimary=True)

chr1 = srv1.characteristic(uuid=b'ab34567890123456', value=5)

char1_read_counter = 0
def char1_cb_handler(chr):
    global char1_read_counter
    char1_read_counter += 1

    events = chr.events()
    if  events & Bluetooth.CHAR_WRITE_EVENT:
        if chr.value() == '1':
            pycom.heartbeat(False)
            pycom.rglbled(0x110000)
    else:
        if char1_read_counter < 3:
            print('Read request on char 1')
        else:
            return 'ABC DEF'

char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)
