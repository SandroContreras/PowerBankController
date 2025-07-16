from machine import Pin, I2C
import ssd1306
import time
from machine import ADC
from PowerBank import BatteryManager, OledUI
## main.py
## Author: Sandro Contreras II
## License: MIT
## Description: Monitors battery voltage and displays battery health via OLED.

## This file controls the Oled display
## Renamed file to "main.py" To boot file on power source

# Initialize I2C
i2c = I2C(0, scl=Pin(5), sda=Pin(4))

# Create display object (128x64 OLED at address 0x3C)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

## Create ADC object on an ADC pin
adc = ADC(Pin(26))	## GPIO 26 on Pico is an ADC0 Pin

percentSymbol = "%"
battery_percent_str = ""

i = 0
SMA = 0
battery_percentage = 0		## Default percentage
raw = 0
adc_voltage = 0
window_average = 0
previous_battery_voltage = 0
battery_voltage = 0

        
BatteryMethods = BatteryManager(raw, adc_voltage, i, SMA, window_average, battery_voltage, battery_percentage)
OledMethods = OledUI(previous_battery_voltage, battery_percent_str, oled, battery_voltage, battery_percentage, raw, adc_voltage)
while True:
    
    previous_battery_voltage = BatteryMethods.PowerCalculator()
    time.sleep(0.5)							# Add a delay between readings for comparison
    battery_voltage = BatteryMethods.PowerCalculator()
    
    battery_percentage = BatteryMethods.SOCtable(battery_voltage)
     
    battery_percent_str = str(battery_percentage)
    
    OledMethods.OledSignal(previous_battery_voltage, percentSymbol, battery_voltage, battery_percent_str)
    time.sleep(5)
    ## Use SMA to smoothen out the battery percentage
    BatteryMethods.AppendArray(battery_voltage)

    battery_voltage = BatteryMethods.BatteryVoltage_SMA(battery_voltage)
    
    OledMethods.variableUpdater(previous_battery_voltage, battery_voltage)	# Update the lower bounds to avoid an always on state