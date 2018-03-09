from machine import Pin
#import machine
import pycom
#import time
from ble_mode import BLE
from deploy_mode import Deploy


if pycom.nvs_get('mode') == 1:
    launch = Deploy()

else:
    configure = BLE("FiPy", 0xa234567890123456)

#else
    # write the BLE mode initializers
test = False
if test == True:
    x = BLE("FiPy", 0xa234567890123456)
