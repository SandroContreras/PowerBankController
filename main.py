from machine import Pin, I2C
import ssd1306
import time
from machine import ADC
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
    ## R1 = 2.2 k ohm, R2 = 47k ohm
    battery_voltage = adc_voltage * 1.05
    
    ## Step 3: Use battery voltage to find Battery Charge Percentage
    
    ## Formula for converting voltage to Battery Health Percentage: Percentage = [(Actual Voltage - Minimum Voltage) / (Maximum Voltage - Minimum Voltage)] * 100
    percentage = (((battery_voltage - 2.5)/(4.2 - 2.5)) * 100)
    percentage_int = int(percentage)
    percentage_str = str(percentage_int)

    print("Floating ADC value: ", raw)
    print("Battery Percentage Value: ", percentage_str, "%")
    print("Previous Battery Voltage: ", previous_battery_voltage)
    print("Current Battery Voltage: ", battery_voltage)
    
    ## Create Power Bank Interaction Signal
    ## The Oled will only display when the charging bank is Charging or Providing Charge
    startTime = time.time()	# Start timing the battery voltage status
    if (previous_battery_voltage < battery_voltage or previous_battery_voltage > battery_voltage):
        
        oled.fill(0)
        oled.text("Battery: ", 0, 0)
    ##oled.text(voltageStr, 65, 0)
        oled.text(percentSymbol, 80, 0)
        oled.text(percentage_str, 65, 0)
        oled.show()
    else:		## If the power bank is idle then power off the oled
        oled.poweroff()
        
    previous_battery_voltage = battery_voltage	## Update the lower bounds to avoid an always on state
    
    time.sleep(5)
    
    endTime = time.time()	# End of battery voltage status
    totalTime = endTime - startTime
    print("Total time of Operation: ", totalTime)