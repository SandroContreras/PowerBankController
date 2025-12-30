from machine import Pin, I2C
import ssd1306
import time
import bisect
from machine import ADC
from PowerBank import BatteryManager, OledUI
## main.py
## Author: Sandro Contreras II
## License: MIT
## Description: Monitors battery voltage and displays battery health
##				using an OlED screen through modular method calls.
## Notes:
## - Named file "main.py" to follow MicroPython auto-run feature
## - This library (ssd1306.py) was manually downloaded from:
##   https://gist.github.com/cwyark/d7f2becd84b0b69b05a83315bf84c467
##   Not included in repo due to license uncertainty.
time.sleep(0.3)		## Allow for Boot time

# Initialize I2C
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
# print(i2c.scan())

# Create display object (128x64 OLED at address 0x3C)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

## Create ADC object on an ADC pin
adc = ADC(Pin(26))	## GPIO 26 on Pico is an ADC0 Pin

battery_percent_str = ""
previous_battery_percentage = 0

BatteryMethods = BatteryManager(adc)
OledMethods = OledUI(oled)

while True:
    
    previous_battery_voltage = BatteryMethods.PowerCalculator()
    
    time.sleep_ms(200)		# Add a delay between readings for comparison

    BatteryMethods.PowerCalculator()

    BatteryMethods.SetWindowSize()

    BatteryMethods.BatteryVoltage_SMA()		## Use SMA to smoothen out the battery percentage
    
    battery_percentage = BatteryMethods.SOCtable()							## battery_percentage is an integer
    battery_percent_str = str(battery_percentage)
    
    BatteryMethods.Check_movingAvgArr()
    
    OledMethods.OledSignal(BatteryMethods, previous_battery_percentage, battery_percent_str)
    
    previous_SMA_battery_voltage = OledMethods.BatteryVoltageUpdater(BatteryMethods)	# Update the lower bounds to avoid an always on state
    
    previous_battery_percentage = battery_percentage