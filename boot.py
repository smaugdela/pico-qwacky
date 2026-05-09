# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support

from board import *
import board
import digitalio
import storage
import os

def is_exfil_enabled(payload_path="payload.dd"):
    try:
        with open(payload_path, "r") as f:
            for line in f:
                if "$_EXFIL_MODE_ENABLED" in line and "TRUE" in line.upper():
                    return True
    except OSError:
        pass
    return False

exfil_enabled = is_exfil_enabled()
loot_exists = "loot.bin" in os.listdir("/")
noStorage = False
noStoragePin = digitalio.DigitalInOut(GP3)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = noStoragePin.value

# check GP0 for setup mode -> This is redundant with duckyinpython.py & pins.py
progStatusPin = digitalio.DigitalInOut(GP0)
progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
progStatus = not progStatusPin.value

### DISABLING ATTACK MODE (i.e SETUP MODE ONLY, FOR DEV) ###
progStatus = True
print("boot.py option forces SETUP mode, for dev purposes. Edit boot.py to make ATTACK possible.")
### END OF DISABLING ATTACK MODE ###

# If setup mode is active, we want USB drive enabled
if progStatus:
    print("SETUP mode enabled, skipping rest of boot and enabling USB drive.")
else:
    # If GP3 is not connected, it will default to being pulled high (True)
    # If GP3 is connected to GND, it will be low (False)

    # Pico:
    #   GP3 not connected == USB visible
    #   GP3 connected to GND == USB not visible

    # Pico W:
    #   GP3 not connected == USB NOT visible
    #   GP3 connected to GND == USB visible

    if exfil_enabled:
        if not loot_exists:
            storage.disable_usb_drive()
    if(board.board_id == 'raspberry_pi_pico' or board.board_id == 'raspberry_pi_pico2'):
        # On Pi Pico, default to USB visible
        noStorage = not noStorageStatus
    elif(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
        # on Pi Pico W, default to USB hidden by default
        # so webapp can access storage
        noStorage = noStorageStatus

if(noStorage == True):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    # normal boot
    print("USB drive enabled")
