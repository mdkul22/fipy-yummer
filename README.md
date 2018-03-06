# fipy-yummer
IoT based plug and play board through BLE

OBJECTIVE
~ This board is mainly designed to act as a highly adaptive IoT board which can
  work in a variety of communication protocols such as WiFi, LoRa, LTE, sigfox

DETAILS
~ The board has two modes: a configure mode and a deploy mode.

CONFIGURE MODE - this mode works on BLE where the pycom board acts as a GATT
server and the mobile acts as a BLE Client getting services and characteristics
of the board.

DEPLOY - this mode will keep checking
