import digitalio
from board import *
from adafruit_debouncer import Debouncer

# Initialize Display Buttons
btnA_pin = digitalio.DigitalInOut(GP12)
btnA_pin.switch_to_input(pull=digitalio.Pull.UP)

btnB_pin = digitalio.DigitalInOut(GP13)
btnB_pin.switch_to_input(pull=digitalio.Pull.UP)

btnX_pin = digitalio.DigitalInOut(GP14)
btnX_pin.switch_to_input(pull=digitalio.Pull.UP)

btnY_pin = digitalio.DigitalInOut(GP15)
btnY_pin.switch_to_input(pull=digitalio.Pull.UP)

# LATCH SETUP MODE STATE
# When code.py starts, this imports immediately. If you are holding Button A 
# from plugging it in, this latches as True. You can release it afterwards.
SETUP_MODE_LATCHED = not btnA_pin.value

# Wrap them in debouncers for your later UI payload menu
button_A = Debouncer(btnA_pin)
button_B = Debouncer(btnB_pin)
button_X = Debouncer(btnX_pin)
button_Y = Debouncer(btnY_pin)

# Legacy GP22 button — kept for backwards compatibility with monitor_buttons()
button1_pin = digitalio.DigitalInOut(GP22)
button1_pin.pull = digitalio.Pull.UP
button1 = Debouncer(button1_pin)
