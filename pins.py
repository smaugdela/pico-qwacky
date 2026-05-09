import digitalio
from digitalio import DigitalInOut, Pull
from board import *
from adafruit_debouncer import Debouncer

#init button
button1_pin = DigitalInOut(GP22) # defaults to input
button1_pin.pull = Pull.UP      # turn on internal pull-up resistor
button1 =  Debouncer(button1_pin)


# payload1 = GPIO12 to GND
# payload2 = GPIO13 to GND
# payload3 = GPIO14 to GND
# payload4 = GPIO15 to GND

#init payload selection switch
payload1Pin = digitalio.DigitalInOut(GP12)
payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
payload2Pin = digitalio.DigitalInOut(GP13)
payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
payload3Pin = digitalio.DigitalInOut(GP14)
payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
payload4Pin = digitalio.DigitalInOut(GP15)
payload4Pin.switch_to_input(pull=digitalio.Pull.UP)

# check GP0 for setup mode
progStatusPin = digitalio.DigitalInOut(GP0)
progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
