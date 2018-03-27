from machine import Pin, reset
import pycom
from configure_mode import BLE
from deploy_mode import Deploy
from nvstring import NvsExtract

def reset_state(arg):
    pycom.nvs_erase_all()
    reset()

reset = Pin('P14', mode=Pin.IN, pull=Pin.PULL_UP, alt=-1)
reset.callback(trigger=Pin.IRQ_FALLING, handler=reset_state, arg=None)
pycom.heartbeat(False)

if NvsExtract('mode').retval() == '1':
    print("begin deploy\n")
    pycom.rgbled(0x000055)
    launch = Deploy()

else:
    print("begin BLE\n")
    pycom.rgbled(0x005500)
    configure = BLE("BLEE", 0xa234567890123456)

#else
    # write the BLE mode initializers
test = False
if test == True:
    x = BLE("BLEE", 0xa234567890123456)
