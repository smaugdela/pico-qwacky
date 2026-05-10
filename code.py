# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Modified for Pimoroni Pico Display Menu UI

import supervisor
import os
import pwmio
import time
import digitalio
import asyncio
import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from fourwire import FourWire
from adafruit_st7789 import ST7789

from duckyinpython import *
import pins # Imports our latched button states

if board.board_id in ('raspberry_pi_pico_w', 'raspberry_pi_pico2_w'):
    import wifi
    from webapp import *

# Allow host recognition
time.sleep(.5)

# --- DISPLAY INITIALIZATION ---
displayio.release_displays()

spi = busio.SPI(board.GP18, board.GP19)
display_bus = FourWire(spi, command=board.GP16, chip_select=board.GP17)

display = ST7789(
    display_bus,
    rotation=270,
    width=240,
    height=135,
    rowstart=40,
    colstart=53,
    backlight_pin=board.GP20,
)
display.brightness = 0.8

# --- MENU UI CLASS ---
class PayloadMenu:
    def __init__(self, display):
        self.group = displayio.Group()
        display.root_group = self.group
        
        # Colors
        bg_color = 0x000000
        text_color = 0x00FF00
        action_color = 0xFF00FF
        
        # Background
        color_bitmap = displayio.Bitmap(display.width, display.height, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = bg_color
        self.group.append(displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0))
        
        # Labels (Using anchor points to easily snap to corners)
        self.lbl_title = label.Label(terminalio.FONT, text="", color=text_color, scale=2)
        self.lbl_title.anchor_point = (0.5, 0.5)
        self.lbl_title.anchored_position = (120, 67)
        
        # Mapping: B = Top Left, A = Top Right, Y = Bottom Left, X = Bottom Right
        self.lbl_tl = label.Label(terminalio.FONT, text="", color=action_color, scale=2)
        self.lbl_tl.anchor_point = (0, 0)
        self.lbl_tl.anchored_position = (5, 5)
        
        self.lbl_tr = label.Label(terminalio.FONT, text="", color=action_color, scale=2)
        self.lbl_tr.anchor_point = (1, 0)
        self.lbl_tr.anchored_position = (235, 5)
        
        self.lbl_bl = label.Label(terminalio.FONT, text="", color=action_color, scale=2)
        self.lbl_bl.anchor_point = (0, 1)
        self.lbl_bl.anchored_position = (5, 130)
        
        self.lbl_br = label.Label(terminalio.FONT, text="", color=action_color, scale=2)
        self.lbl_br.anchor_point = (1, 1)
        self.lbl_br.anchored_position = (235, 130)
        
        for lbl in [self.lbl_title, self.lbl_tl, self.lbl_tr, self.lbl_bl, self.lbl_br]:
            self.group.append(lbl)

    def show(self, title, tl, tr, bl, br):
        self.lbl_title.text = title
        self.lbl_tl.text = tl
        self.lbl_tr.text = tr
        self.lbl_bl.text = bl
        self.lbl_br.text = br

# --- WIFI & SYSTEM SETUP ---
def startWiFi():
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets missing!")
        raise
    wifi.radio.start_ap(secrets['ssid'], secrets['password'])
    print(repr(wifi.radio.ipv4_address_ap), 80)

supervisor.runtime.autoreload = True # Dev mode

if board.board_id in ('raspberry_pi_pico', 'raspberry_pi_pico2'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif board.board_id in ('raspberry_pi_pico_w', 'raspberry_pi_pico2_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()

# --- ASYNC MENU STATE MACHINE ---
async def interactive_payload_selector():
    menu = PayloadMenu(display)
    state = 0
    choices = ["", "", ""] # [OS, KB, TYPE]
    
    while True:
        # Update physical buttons via debouncer from pins.py
        pins.button_A.update()
        pins.button_B.update()
        pins.button_X.update()
        pins.button_Y.update()
        
        if state == 0:
            menu.show("Select OS", "Win", "Mac", "Lin", "")
            if pins.button_A.fell: choices[0] = "win"; state = 1    # Top-Left
            elif pins.button_X.fell: choices[0] = "mac"; state = 1  # Top-Right
            elif pins.button_B.fell: choices[0] = "lin"; state = 1  # Bottom-Right
            
        elif state == 1:
            menu.show("Keyboard", "US", "FR", "", "Back")
            if pins.button_A.fell: choices[1] = "us"; state = 2     # Top-Left
            elif pins.button_X.fell: choices[1] = "fr"; state = 2   # Top-Right
            elif pins.button_Y.fell: state = 0                      # Bottom-Left (Back)

        elif state == 2:
            menu.show("Payload", "Prank", "RAT", "Exfil", "Back")
            if pins.button_A.fell: choices[2] = "prank"; state = 3  # Top-Left
            elif pins.button_X.fell: choices[2] = "rat"; state = 3  # Top-Right
            elif pins.button_B.fell: choices[2] = "exfil"; state = 3 # Bottom-Right
            elif pins.button_Y.fell: state = 1                      # Bottom-Left (Back)
            
        elif state == 3:
            payload_name = f"{choices[0]}-{choices[1]}-{choices[2]}.dd"
            menu.show(payload_name, "", "", "YES", "NO")
            if pins.button_B.fell: # Confirm
                menu.show("Running...", "", "", "", "")
                return payload_name
            elif pins.button_Y.fell: # Cancel/Back
                state = 2
                
        # Yield time to system / other async tasks
        await asyncio.sleep(0.05)

# --- MAIN EXECUTION LOGIC ---
async def run_payload_on_startup():
    progStatus = getProgrammingStatus()
    print("progStatus", progStatus)
    
    if not progStatus:
        while True:
            if "loot.bin" in os.listdir("/"):
                print("loot.bin exists, skipping payload execution.")
            else:
                print("Starting Payload UI Wizard...")
                payload = await interactive_payload_selector()
                await asyncio.sleep(0.1)
                print(f"Running: {payload}")
                
                # Check if file actually exists before running
                if payload in os.listdir("/"):
                    await runScript(payload)
                else:
                    PayloadMenu(display).show("Not Found!", "", "", "", "")
                    await asyncio.sleep(1.5)
    else:
        print("Setup Mode Active. Bypassing Payload.")
        PayloadMenu(display).show("Setup Mode", "", "", "", "")

async def main_loop():
    global led
    payload_task = asyncio.create_task(run_payload_on_startup())
    led_task = asyncio.create_task(monitor_led_changes())
    
    if board.board_id in ('raspberry_pi_pico_w', 'raspberry_pi_pico2_w'):
        pico_led_task = asyncio.create_task(blink_pico_w_led(led))
        startWiFi()
        webservice_task = asyncio.create_task(startWebService())
        await asyncio.gather(pico_led_task, webservice_task, payload_task, led_task)
    else:
        pico_led_task = asyncio.create_task(blink_pico_led(led))
        await asyncio.gather(pico_led_task, payload_task, led_task)

### DUCKY ENTRYPOINT ###
asyncio.run(main_loop())
