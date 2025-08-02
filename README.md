# Power Bank Controller
MicroPython code to control an Oled Display monitoring Battery Health

**Link to Project: http://future-live-demo.com/**

## How It's Made
**Tech Used:** MicroPython, Raspberry Pi Pico, SSD1306 OLED Display

Eight 18650 batteries are wired in parallel to a boost converter charging module. The charging module powers the Pico Board and the OLED Display. To achieve battery health displays a voltage divider is used to safely bring down the voltage towards an ADC pin. The display is programmed to display the reported battery health percentage for the user. 

## Optimizations
I will talk about how wiring schemes were improved and practical design ideas

## Lessons Learned
This was my first time soldering. I quickly learned the soldering process through soldering the Battery Case Holders to the Charging Module. This project has taught me to appreciate the use of Solder Flux for creating superior solder and for desoldering. 

## Data Flow
I will include a Diagram of how Pico and OLED displays battery Health with ADC pin 26

## Circuit Diagram
A Circuit Diagram will be included soon.

## Included Modules
- 'bisect.py' - From the Python Standard Library (CPython 3.13)
- Source: https://github.com/python/cpython
- License: Python Software Foundation License (PSF)
