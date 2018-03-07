#from machine import Pin
#import machine
#import pycom
#import time
from ble_mode import BLE
#import deploy_mode


#def btn_irq():
    # on pressing the btn, the irq switches mode BLE(0) and goes into the mode
#    pycom.nvs_set('mode', 0)
#    machine.reset()

#btn = Pin('P14', mode=Pin.IN, pull=Pin.PULL_DOWN, alt=-1)
#irq = btn.irq(trigger=Pin.IRQ_RISING, handler=btn_irq())


#if pycom.nvs_get('mode') == 1:
    # write the deploy class object and launch

#else
    # write the BLE mode initializers
test = False
if test == True:
    x = BLE("FiPy", 0xa234567890123456)
