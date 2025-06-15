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

while True:
    raw = adc.read_u16()	## Read a Raw analog value in the range 0 - 65535
    ## Step 1: Find Adc Voltage
    adc_voltage = (raw * 3.3 / 65535)
    ## Step 2: Use Adc Voltage to find current Battery Voltage
    
    ## Battery Voltage = Adc Voltage * ((R1+R2) / R2)
    ## R1 = 47k ohm, R2 = 10k ohm
    battery_voltage = adc_voltage * 1.47
    
    ## Step 3: Use battery voltage to find Battery Charge Percentage
    
    ## Formula for converting voltage to Battery Health Percentage: Percentage = [(Actual Voltage - Minimum Voltage) / (Maximum Voltage - Minimum Voltage)] * 100
        ## Save this code for future Fuel Guage Chips
    #percentage = (((battery_voltage - 2.5)/(4.2 - 2.5)) * 100)
    #percentage_int = int(percentage)
    #percentage_str = str(percentage_int)
    
    battery_percentage = 95
    
    ## Create State of Charge Table
    if 3.0 <= battery_voltage <= 3.10:
        battery_percentage = 5
    elif 3.10 <= battery_voltage <= 3.20:
        battery_percentage = 7
    elif 3.20 <= battery_voltage <= 3.30:
        battery_percentage = 10
    elif 3.30 <= battery_voltage <= 3.35:
        battery_percentage = 13
    elif 3.35 <= battery_voltage <= 3.40:
        battery_percentage = 15
    elif 3.40 <= battery_voltage <= 3.50:
        battery_percentage = 20
    elif 3.50 <= battery_voltage <= 3.55:
        battery_percentage = 30
    elif 3.55 <= battery_voltage <= 3.60:
        battery_percentage = 40
    elif 3.60 <= battery_voltage <= 3.70:
        battery_percentage = 50
    elif 3.70 <= battery_voltage <= 3.80:
        battery_percentage = 60
    elif 3.80 <= battery_voltage <= 3.90:
        battery_percentage = 70
    elif 3.90 <= battery_voltage <= 4.0:
        battery_percentage = 80
    elif 4.0 <= battery_voltage <= 4.1:
        battery_percentage = 90
    elif 4.1 <= battery_voltage <= 4.2:
        battery_percentage = 100
    
    battery_percent_str = str(battery_percentage)
    
    ## Create Power Bank Interaction Signal
    ## The Oled will only display when the charging bank is Charging or Providing Charge
    #startTime = time.time()	# Start timing the battery voltage status
    if (previous_battery_voltage < battery_voltage or previous_battery_voltage > battery_voltage):
        
        oled.fill(0)
        oled.text("Battery: ", 0, 0)
        oled.text(percentSymbol, 80, 0)
        oled.text(battery_percent_str, 65, 0)
        #oled.text(percentage_str, 65, 0)
        
        oled.show()
    else:		## If the power bank is idle then power off the oled
        oled.poweroff()
        
    previous_battery_voltage = battery_voltage	## Update the lower bounds to avoid an always on state
    
    time.sleep(5)
    
   # endTime = time.time()	# End of battery voltage status
   # totalTime = endTime - startTime
   # print("Total time of Operation: ", totalTime)