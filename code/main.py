from machine import Pin, I2C
import ssd1306
import time
import utime
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
i2c = I2C(0, scl=Pin(5), sda=Pin(4))

# Create display object (128x64 OLED at address 0x3C)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

## Create ADC object on an ADC pin
adc = ADC(Pin(26))	## GPIO 26 on Pico is an ADC0 Pin

percentSymbol = "%"
battery_percent_str = ""

SMA_battery_voltage = 0
battery_percentage = 0
raw = 0
adc_voltage = 0
windowSize = 0
movingAvg = []
previous_battery_voltage = 0
battery_voltage = 0
time_update = 0
BatteryVoltageArr = []        
BatteryMethods = BatteryManager(raw, adc_voltage, SMA_battery_voltage, movingAvg, battery_voltage, battery_percentage, BatteryVoltageArr, windowSize)
OledMethods = OledUI(previous_battery_voltage, battery_percent_str, oled, battery_voltage, battery_percentage, raw, adc_voltage, time, time_update, BatteryVoltageArr, windowSize, SMA_battery_voltage)

delayMS = 500
timeStart = utime.ticks_ms()
while True:
    
    previous_battery_voltage = BatteryMethods.PowerCalculator()
    
#     if (utime.ticks_diff(utime.ticks_ms(), timeStart) >= delayMS):
#         print("Non-Blocking timer works")
#         battery_voltage = BatteryMethods.PowerCalculator()
#         timeStart = utime.ticks_ms()
    time.sleep_ms(4)
#     time.sleep(0.3)							# Add a delay between readings for comparison
    battery_voltage = BatteryMethods.PowerCalculator()

    windowSize = BatteryMethods.SetWindowSize(battery_voltage)

    ## Use SMA to smoothen out the battery percentage
    BatteryMethods.AppendArray(battery_voltage, windowSize)

    SMA_battery_voltage = BatteryMethods.BatteryVoltage_SMA(battery_voltage, windowSize)
    
    battery_percentage = BatteryMethods.SOCtable(SMA_battery_voltage)
     
    battery_percent_str = str(battery_percentage)
    
    movingAvgArrBool = BatteryMethods.Check_movingAvgArr(movingAvg)
    
    OledMethods.OledSignal(previous_battery_voltage, percentSymbol, battery_voltage, battery_percent_str, BatteryVoltageArr, windowSize, SMA_battery_voltage, movingAvgArrBool)
    
    OledMethods.BatteryVoltageUpdater(previous_battery_voltage, battery_voltage)	# Update the lower bounds to avoid an always on state                                                      