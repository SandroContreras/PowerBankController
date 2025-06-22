from machine import Pin, I2C
import ssd1306
import time
from machine import ADC
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
## Values 0 - 65535 represents voltages between 0V - 3.3V
raw = adc.read_u16()	## Read a Raw analog value in the range 0 - 65535

adc_voltage = (raw * 3.3 / 65535)
    ## Step 2: Use Adc Voltage to find current Battery Voltage
    
    ## Battery Voltage = Adc Voltage * ((R1+R2) / R2)
    ## R1 = 2.2 k ohm, R2 = 47k ohm
previous_battery_voltage = adc_voltage * 1.05

percentSymbol = "%"

BatteryVoltageArr = []
movingAvg = []
windowSize = 12 
i = 0
total = 0
SMA = 0
def BatteryVoltage_SMA():
    print("Function triggered")
    for item in BatteryVoltageArr:
        print(item)
    while i < len(BatteryVoltageArr) - windowSize + 1:	## Append to Array until window size is met
        print("While statement triggered")
        
        window_average = round(sum(BatteryVoltageArr) / windowSize, 2)

        movingAvg.append(battery_voltage)	## Store SMA in SMA array
        print("SMA Battery Voltage:", battery_voltage)
        BatteryVoltageArr.pop(0)

        return battery_voltage

def SOCtable(battery_voltage):
    ## Create State of Charge Table
    if 3.0 <= battery_voltage <= 3.10:
        battery_percentage = 5
        return battery_percentage
    elif 3.10 <= battery_voltage <= 3.20:
        battery_percentage = 7
        return battery_percentage
    elif 3.20 <= battery_voltage <= 3.30:
        battery_percentage = 10
        return battery_percentage
    elif 3.30 <= battery_voltage <= 3.35:
        battery_percentage = 13
        return battery_percentage
    elif 3.35 <= battery_voltage <= 3.40:
        battery_percentage = 15
        return battery_percentage
    elif 3.40 <= battery_voltage <= 3.50:
        battery_percentage = 20
        return battery_percentage
    elif 3.50 <= battery_voltage <= 3.55:
        battery_percentage = 30
        return battery_percentage
    elif 3.55 <= battery_voltage <= 3.60:
        battery_percentage = 40
        return battery_percentage
    elif 3.60 <= battery_voltage <= 3.70:
        battery_percentage = 50
        return battery_percentage
    elif 3.70 <= battery_voltage <= 3.80:
        battery_percentage = 60
        return battery_percentage
    elif 3.80 <= battery_voltage <= 3.90:
        battery_percentage = 70
        return battery_percentage
    elif 3.90 <= battery_voltage <= 4.0:
        battery_percentage = 80
        return battery_percentage
    elif 4.0 <= battery_voltage <= 4.1:
        battery_percentage = 90
        return battery_percentage
    elif 4.1 <= battery_voltage <= 4.2:
        battery_percentage = 100
        return battery_percentage

def OledSignal(previous_battery_voltage, battery_voltage):
    ## Create Power Bank Interaction Signal
    ## The Oled will only display when the charging bank is Charging or Providing Charge
    if (previous_battery_voltage < battery_voltage or previous_battery_voltage > battery_voltage):
        
        oled.fill(0)
        
        oled.text(percentSymbol, 80, 0)
        oled.text(battery_percent_str, 65, 0)
        
        # Create Battery Symbol
        oled.rect(0, 0, 41, 10, 1)
        oled.vline(10, 0, 10, 1)
        oled.vline(20, 0, 10, 1)
        oled.vline(30, 0, 10, 1)
        oled.rect(41, 3, 3, 5, 1)	## Battery Terminal Symbol
        
        oled.show()
    else:		## If the power bank is idle then power off the oled
        oled.poweroff()
        
while True:
    raw = adc.read_u16()	## Read a Raw analog value in the range 0 - 65535
    ## Step 1: Find Adc Voltage
    adc_voltage = (raw * 3.3 / 65535)
    ## Step 2: Use Adc Voltage to find current Battery Voltage
    
    ## Battery Voltage = Adc Voltage * ((R1+R2) / R2)
    ## R1 = 47k ohm, R2 = 100k ohm
    battery_voltage = adc_voltage * 1.47
    
    battery_percentage = 0
    
    ## Use SMA to smoothen out the battery percentage
    BatteryVoltageArr.append(battery_voltage)

    BatteryVoltage_SMA()

    #battery_voltage = BatteryVoltage_SMA()
   
    SOCtable(battery_voltage)
     
    battery_percent_str = str(battery_percentage)
    
    OledSignal(previous_battery_voltage, battery_voltage)
        
    previous_battery_voltage = battery_voltage	## Update the lower bounds to avoid an always on state
    
    time.sleep(0.5)