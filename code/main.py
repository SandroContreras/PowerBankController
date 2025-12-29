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

percentSymbol = "%"
battery_percent_str = ""

SMA_battery_voltage = 0
previous_battery_percentage = 0
battery_percentage = 0
raw = 0
adc_voltage = 0
windowSize = 0
movingAvg = []
previous_SMA_battery_voltage = 0
battery_voltage = 0
BatteryVoltageArr = []

BatteryMethods = BatteryManager(raw, adc_voltage, SMA_battery_voltage, movingAvg, battery_voltage, battery_percentage, BatteryVoltageArr, windowSize)
OledMethods = OledUI(previous_SMA_battery_voltage, previous_battery_percentage, battery_percent_str, oled, battery_voltage, battery_percentage, raw, adc_voltage, BatteryVoltageArr, windowSize, SMA_battery_voltage)

while True:
    
    previous_battery_voltage = BatteryMethods.PowerCalculator()
    
    time.sleep_ms(200)		# Add a delay between readings for comparison

    battery_voltage = BatteryMethods.PowerCalculator()

    windowSize = BatteryMethods.SetWindowSize(battery_voltage)

    SMA_battery_voltage = BatteryMethods.BatteryVoltage_SMA(battery_voltage, windowSize)		## Use SMA to smoothen out the battery percentage
    
    battery_percentage = BatteryMethods.SOCtable(SMA_battery_voltage)							## battery_percentage is an integer
    battery_percent_str = str(battery_percentage)
    
    movingAvgArrBool = BatteryMethods.Check_movingAvgArr(movingAvg)
    
    OledMethods.OledSignal(previous_SMA_battery_voltage, percentSymbol, battery_voltage, previous_battery_percentage, battery_percent_str, BatteryVoltageArr, windowSize, SMA_battery_voltage, movingAvgArrBool)
    
    previous_SMA_battery_voltage = OledMethods.BatteryVoltageUpdater(previous_SMA_battery_voltage, SMA_battery_voltage)	# Update the lower bounds to avoid an always on state
    
    previous_battery_percentage = battery_percentage