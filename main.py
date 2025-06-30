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

percentSymbol = "%"
battery_percent_str = ""

BatteryVoltageArr = []
movingAvg = []
windowSize = 12 
i = 0
SMA = 0
battery_percentage = 0		## Default percentage
raw = 0
adc_voltage = 0
window_average = 0
previous_battery_voltage = 0
battery_voltage = 0
class BatteryManager:
    def __init__(self, raw, adc_voltage, movingAvg, windowSize, i, SMA, window_average, BatteryVoltageArr, battery_voltage, battery_percentage):
        self.raw = raw
        self.adc_voltage = adc_voltage
        self.movingAvg = movingAvg
        self.windowSize = windowSize
        self.i = i
        self.SMA = SMA
        self.window_average = window_average
        self.BatteryVoltageArr = BatteryVoltageArr
        self.battery_voltage = battery_voltage
        self.battery_percentage = battery_percentage
        
    def PowerCalculator(self):						## Values 0 - 65535 represents voltages between 0V - 3.3V
        self.raw = adc.read_u16()					## Read a Raw analog value in the range 0 - 65535

        self.adc_voltage = (raw * 3.3 / 65535)		## Step 1: Find Adc Voltage

        self.battery_voltage = self.adc_voltage * 1.47 	## Battery Voltage = Adc Voltage * ((R1+R2) / R2)
        return self.battery_voltage					## R1 = 47k ohm, R2 = 100k ohm

#     def	BatteryVoltageArrAppender(self.battery_voltage):
#         self.BatteryVoltageArr.append(self.battery_voltage)

    def BatteryVoltage_SMA(self, battery_voltage):
        print("Function triggered")
        for item in BatteryVoltageArr:
            print(item)
        while i < len(BatteryVoltageArr) - windowSize + 1:	## Append to Array until window size is met
            print("While statement triggered")
            
            window_average = round(sum(BatteryVoltageArr) / windowSize, 2)
            battery_voltage = window_average	## battery_voltage = SMA of Battery Voltages
            
            movingAvg.append(battery_voltage)	## Store SMA in SMA array
            print("SMA Battery Voltage:", battery_voltage)
            BatteryVoltageArr.pop(0)

        return battery_voltage
    
    @staticmethod
    def SOCtable(battery_voltage):
    ## Create State of Charge Table
    ######################################  TURN THIS INTO A BISECT + LOOKUP LIST FOR OPTIMIZATION ###########################################################################
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
            self.battery_percentage = 90
            return battery_percentage
        elif 4.1 <= battery_voltage <= 4.2:
            battery_percentage = 100
            return battery_percentage

class OledUI(BatteryManager):		## Inherit the variables from BatteryManager Class
    def __init__(self, previous_battery_voltage, battery_percent_str, oled):
        super().__init__(raw, adc_voltage, movingAvg, windowSize, i, SMA, window_average, BatteryVoltageArr, battery_voltage, battery_percentage)
        self.battery_percent_str = battery_percent_str
        self.oled = oled
        self.previous_battery_voltage = previous_battery_voltage
    
    def variableUpdater(self, previous_battery_voltage, battery_voltage):
        self.previous_battery_voltage = self.battery_voltage
    
    def OledSignal(self, previous_battery_voltage, percentSymbol, battery_voltage):
    ## Create Power Bank Interaction Signal
    ## The Oled will only display when the charging bank is Charging or Providing Charge
        if (self.previous_battery_voltage < self.battery_voltage or self.previous_battery_voltage > self.battery_voltage):
        
            self.oled.fill(0)
            self.oled.text("Sandro's", 30, 30, 1)		## Signature
            self.oled.text("Power Bank", 20, 40, 1)

            if (self.battery_voltage >= 3.20):
                ## Display Battery Percentage for Double Digit Value
                self.oled.text(self.percentSymbol, 86, 4)
                self.oled.text(self.battery_percent_str, 70, 4)
            else:
                ## Shift Percent Symbol inwards towards the Single Digit Value
                self.oled.text(self.percentSymbol, 78, 4)
                self.oled.text(self.battery_percent_str, 70, 4)
        
            print("Previous Battery Voltage: ", self.previous_battery_voltage)
            print("Current Battery Voltage: ", self.battery_voltage)
        
            ## The Charging symbol will only appear if the Bank is Charging
            if (self.previous_battery_voltage < self.battery_voltage):
                ## Create Charging Symbol
                self.oled.vline(55, 0, 16, 1)
                self.oled.hline(55, 6, 8, 1)	## Create horizontal line at halfway point at charging symbol
                self.oled.line(62, 6, 55, 15, 1)
                self.oled.hline(48, 9, 8, 1)	## Create horizontal line at halfway point at charging symbol
                self.oled.line(55, 0, 47, 9, 1)
                ## Inner Symbol Fillings
                self.oled.fill_rect(52, 6, 5, 4, 1)
                self.oled.fill_rect(55, 6, 4, 4, 1)
                self.oled.fill_rect(53, 2, 2, 4, 1)
                self.oled.fill_rect(49, 7, 12, 2, 1)
                self.oled.fill_rect(55, 8, 4, 4, 1)
                self.oled.fill_rect(59, 9, 1, 1, 1)
                self.oled.fill_rect(56, 12, 1, 3, 1)
                self.oled.fill_rect(51, 4, 3, 3, 1)
                
            # Create Battery Symbol
            self.oled.rect(0, 0, 41, 10, 1)
            self.oled.vline(10, 0, 10, 1)
            self.oled.vline(20, 0, 10, 1)
            self.oled.vline(30, 0, 10, 1)
            self.oled.rect(41, 3, 3, 5, 1)	## Battery Terminal Symbol
        
            ## Create if statements to dicate which inner battery quadrants to fill in depending on battery health levels
            if (3.0 <= self.battery_voltage <= 3.55):
                print("Filling up 1st quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
            elif (3.55 <= self.battery_voltage <= 3.70):
                print("Filling up 2nd quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
                self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
            elif (3.70 <= self.battery_voltage <= 4.0):
                print("Filling up 3rd quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
                self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
                self.oled.fill_rect(22, 1, 8, 8, 1)		## Fill the 3rd quadrant
            elif (4.0 <= self.battery_voltage <= 4.2):
                print("Filling up 4th quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
                self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
                self.oled.fill_rect(22, 1, 8, 8, 1)		## Fill the 3rd quadrant
                self.oled.fill_rect(32, 1, 8, 8, 1)		## Fill the last quadrant
            
            self.oled.show()
        else:		## If the power bank is idle then power off the oled
            self.oled.poweroff()
        
BatteryMethods = BatteryManager(raw, adc_voltage, movingAvg, windowSize, i, SMA, window_average, BatteryVoltageArr, battery_voltage, battery_percentage)
OledMethods = OledUI(previous_battery_voltage, battery_percent_str, oled)
while True:
    
    previous_battery_voltage = BatteryMethods.PowerCalculator()
    time.sleep(0.5)							# Add a delay between readings for comparison
    battery_voltage = BatteryMethods.PowerCalculator()
    
    ## Use SMA to smoothen out the battery percentage
    BatteryVoltageArr.append(battery_voltage)

    battery_voltage = BatteryMethods.BatteryVoltage_SMA(battery_voltage)
   
    battery_percentage = BatteryMethods.SOCtable(battery_voltage)
     
    battery_percent_str = str(battery_percentage)
    
    OledMethods.OledSignal(previous_battery_voltage, percentSymbol, battery_voltage)
    
    previous_battery_voltage = battery_voltage	## Update the lower bounds to avoid an always on state