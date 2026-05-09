# pico-qwacky

My own pico-ducky, with a pimoroni display-and-4-buttons hat...

## Installation

First check [DUCKY_INSTALL.md](DUCKY_INSTALL.md) to install the rubber ducky logic on a raspberry pico.

To ensure proper display functionnality, go to [circuitpython libraries bundle](https://circuitpython.org/libraries), download and decompress it, and import the following libs inside the lib folder of your CIRCUITPY board:
adafruit_st7789.mp
adafruit_rgb_display/
adafruit_display_text/
... (Any other library containing ST7789 drivers with your needed functionnalities).

Then replace *.py (not the lib folder, only the root ones) with the ones of this repo.
