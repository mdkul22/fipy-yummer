from machine import Pin
#import machine
import pycom
#import time
from ble_mode import BLE
from deploy_mode import Deploy
from nvstring import NvsExtract

if NvsExtract('mode').retval() == '1':
    print("begin deploy\n")
    launch = Deploy()

else:
    print("begin BLE\n")
    configure = BLE("FiPy", 0xa234567890123456)

#else
    # write the BLE mode initializers
test = False
if test == True:
    x = BLE("FiPy", 0xa234567890123456)
