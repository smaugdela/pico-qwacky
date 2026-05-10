# License : GPLv2.0
# copyright (c) 2023 Dave Bailey (dbisu, @daveisu)
# Modified for Pimoroni Pico Display buttons

import board
import digitalio
import storage
import os

# 1. Temporarily init Buttons A (Setup) and B (Storage)
btnA = digitalio.DigitalInOut(board.GP12)
btnA.switch_to_input(pull=digitalio.Pull.UP)
btnA_pressed = not btnA.value # True if pressed to GND

btnB = digitalio.DigitalInOut(board.GP13)
btnB.switch_to_input(pull=digitalio.Pull.UP)
btnB_pressed = not btnB.value # True if pressed to GND

# 2. IMPORTANT: Free the pins so code.py and your display UI can use them!
btnA.deinit()
btnB.deinit()

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

# 3. Determine Storage Status based on button presses
enable_storage = False

if btnA_pressed:
    print("Setup & Storage mode forced via display button.")
    enable_storage = True
elif btnB_pressed:
    print("Storage mode forced via display button.")
    enable_storage = True
else:
    # Standard logic if no buttons are held
    if board.board_id in ('raspberry_pi_pico', 'raspberry_pi_pico2'):
        enable_storage = True
    elif board.board_id in ('raspberry_pi_pico_w', 'raspberry_pi_pico2_w'):
        enable_storage = False

    if exfil_enabled and not loot_exists:
        enable_storage = False

if not enable_storage:
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    print("USB drive enabled")
