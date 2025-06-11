# Power Bank Controller
MicroPython code to control an Oled Display monitoring Battery Health

**Link to Project: http://recruiters-love-seeing-live-demos.com/**

## How It's Made
**Tech Used:** Python, Thonny, Raspberry Pi Pico

Eight 18650 batteries are wired in parallel to a boost converter charging module. The charging module powers the Pico Board and the OLED Display. To achieve battery health displays a voltage divider is used to safely bring down the voltage towards an ADC pin. The display is programmed to display the reported battery health percentage for the user. 
