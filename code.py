# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support


### ducky imports
import supervisor
import os
import pwmio
import time
import digitalio
from board import *
import board
from duckyinpython import *
if(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
    import wifi
    from webapp import *

# display imports
# import board
# from board import *
import busio
import displayio
import terminalio
from adafruit_display_text import label
from fourwire import FourWire

from adafruit_st7789 import ST7789


# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

def startWiFi():
    import ipaddress
    # Get wifi details and more from a secrets.py file
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    print("Connect wifi")
    #wifi.radio.connect(secrets['ssid'],secrets['password'])
    wifi.radio.start_ap(secrets['ssid'],secrets['password'])

    HOST = repr(wifi.radio.ipv4_address_ap)
    PORT = 80        # Port to listen on
    print(HOST,PORT)

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()

# Attack mode
# supervisor.runtime.autoreload = False
# Dev mode
supervisor.runtime.autoreload = True

if(board.board_id == 'raspberry_pi_pico' or board.board_id == 'raspberry_pi_pico2'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()

async def run_payload_on_startup():
    progStatus = False
    progStatus = getProgrammingStatus()
    print("progStatus", progStatus)
    if(progStatus == False):
        print("Finding payload")
        if "loot.bin" in os.listdir("/"):
            print("loot.bin exists, skipping payload execution.")
        else:
            payload = selectPayload()
            await asyncio.sleep(0.1)
            print("Running")
            await runScript(payload)
    else:
        print("Done")


led_state = False


async def main_loop():
    global led,button1

    button_task = asyncio.create_task(monitor_buttons(button1))
    payload_task = asyncio.create_task(run_payload_on_startup())
    led_task = asyncio.create_task(monitor_led_changes())
    if(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
        pico_led_task = asyncio.create_task(blink_pico_w_led(led))
        print("Starting Wifi")
        startWiFi()
        print("Starting Web Service")
        webservice_task = asyncio.create_task(startWebService())
        await asyncio.gather(pico_led_task, button_task, webservice_task, payload_task, led_task)
    else:
        pico_led_task = asyncio.create_task(blink_pico_led(led))
        await asyncio.gather(pico_led_task, button_task, payload_task, led_task )


### PIM DISPLAY ENTRYPOINT ###
"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text.
"""

# First set some parameters used for shapes and text
BORDER = 20
FONTSCALE = 2
BACKGROUND_COLOR = 0x00FF00  # Bright Green
FOREGROUND_COLOR = 0xAA0088  # Purple
TEXT_COLOR = 0xFFFF00

# Release any resources currently in use for the displays
displayio.release_displays()

tft_cs = board.GP17
tft_dc = board.GP16
spi_mosi = board.GP19
spi_clk = board.GP18
spi = busio.SPI(spi_clk, spi_mosi)
backlight = board.GP20

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)

display = ST7789(
    display_bus,
    rotation=270,
    width=240,
    height=135,
    rowstart=40,
    colstart=53,
    backlight_pin=backlight,
)

# Set the backlight
display.brightness = 0.8

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BACKGROUND_COLOR

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(display.width - BORDER * 2, display.height - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = FOREGROUND_COLOR
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER)
splash.append(inner_sprite)

# Draw a label
text = "Hello Night City!"
text_area = label.Label(terminalio.FONT, text=text, color=TEXT_COLOR)
text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(
    scale=FONTSCALE,
    x=display.width // 2 - text_width // 2,
    y=display.height // 2,
)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# while True:
#     pass
### END OF PIM DISPLAY ENTRYPOINT ###


### DUCKY ENTRYPOINT ###
asyncio.run(main_loop())
### END OF DUCKY ENTRYPOINT ###