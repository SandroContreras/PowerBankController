from machine import Pin, I2C
import ssd1306
import time
import bisect
from machine import ADC

## Create ADC object on an ADC pin
adc = ADC(Pin(26))	## GPIO 26 on Pico is an ADC0 Pin
class BatteryManager:
    def __init__(self, raw, adc_voltage, i, SMA, window_average, battery_voltage, battery_percentage):
        self.raw = raw
        self.adc_voltage = adc_voltage
        self.movingAvg = []
        self.windowSize = 60
        self.i = i
        self.SMA = SMA
        self.window_average = window_average
        self.BatteryVoltageArr = []
        self.battery_voltage = battery_voltage
        self.battery_percentage = battery_percentage
        
    def AppendArray(self, element):
        self.BatteryVoltageArr.append(element)
    
    def PowerCalculator(self):						## Values 0 - 65535 represents voltages between 0V - 3.3V
        self.raw = adc.read_u16()					## Read a Raw analog value in the range 0 - 65535

        self.adc_voltage = (self.raw * 3.3 / 65535)		## Step 1: Find Adc Voltage

        self.battery_voltage = self.adc_voltage * 1.47 	## Battery Voltage = Adc Voltage * ((R1+R2) / R2)
        #print("Calculated Battery Voltage: ", self.battery_voltage)
        return self.battery_voltage					## R1 = 47k ohm, R2 = 100k ohm
    
    def SetWindowSize(self, battery_voltage):		## Lithium batteries don't charge linearly
        if self.battery_voltage < 3.9:				## Reduce greater noise before 3.9 V with large SMA window
            self.windowSize = 60
            
        else:										## Less Noise beyond 3.9V so reduce SMA window
            self.windowSize = 12
            
        return self.windowSize
    
    def BatteryVoltage_SMA(self, battery_voltage):
        self.SetWindowSize(self.battery_voltage)
#         for item in self.BatteryVoltageArr:
#             print("Voltages in Battery Voltage Array: ", item)
        while self.i < len(self.BatteryVoltageArr) - self.windowSize + 1:	## Append to Array until window size is met
            
            self.window_average = round(sum(self.BatteryVoltageArr) / self.windowSize, 2)
            self.battery_voltage = self.window_average	## battery_voltage = SMA of Battery Voltages
            
            self.movingAvg.append(self.battery_voltage)	## Store SMA in SMA array
            #print("SMA Battery Voltage:", self.battery_voltage)
            self.BatteryVoltageArr.pop(0)

        return self.battery_voltage
    
    def SOCtable(self, battery_voltage):

        VoltageRange = [3.0, 3.1, 3.2, 3.3, 3.35, 3.4, 3.55, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2]
        Percentage = [5, 7, 10, 13, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        Index =  bisect.bisect_left(VoltageRange, battery_voltage)
        return Percentage[Index]

    def GetPowerDifference(self, previous_battery_voltage, battery_voltage):
        self.Difference = previous_battery_voltage - battery_voltage
        return self.Difference
    
    def CheckPowerThreshold(self, previous_battery_voltage, battery_voltage):
        self.GetPowerDifference(previous_battery_voltage, battery_voltage)
        if (self.Difference > 0.01):		## If Power Difference > 0.01 V, then it's no longer just a power flickering
            return True
        else:
            return False					## If Power Difference < 0.01 V, then it's just power flickering

class OledUI(BatteryManager):		## Inherit the variables from BatteryManager Class
    def __init__(self, previous_battery_voltage, battery_percent_str, oled, battery_voltage, battery_percentage, raw, adc_voltage, time, time_update):
        dummy_raw = 0
        dummy_i = 0
        dummy_SMA = 0
        dummy_window_average = 0
        dummy_adc_voltage = 0
        
        super().__init__(dummy_raw, dummy_adc_voltage, dummy_i, dummy_SMA, dummy_window_average, battery_voltage, battery_percentage)		## I only need variables: battery_voltage, battery_percentage from parent class
        self.oled = oled
        self.percentSymbol = "%"
        self.time = 500
        self.time_update = 0
        
    def variableUpdater(self, previous_battery_voltage, battery_voltage):
        self.previous_battery_voltage = self.battery_voltage
    
    def OledSignal(self, previous_battery_voltage, percentSymbol, battery_voltage, battery_percent_str):
        #self.GetPowerDifference()
        self.GetPowerDifference(previous_battery_voltage, battery_voltage)
        DifferenceBool = self.CheckPowerThreshold(previous_battery_voltage, battery_voltage)
        
    ## Create Power Bank Interaction Signal
    ## The Oled will only display when the charging bank is Charging or Providing Charge
        if ((previous_battery_voltage < battery_voltage or previous_battery_voltage > battery_voltage) and DifferenceBool):
        
            self.oled.fill(0)
            self.oled.text("Sandro's", 30, 30, 1)		## Signature
            self.oled.text("Power Bank", 20, 40, 1)

            if (battery_voltage >= 3.20):
                print("battery_percent_str value: ", battery_percent_str)
                ## Display Battery Percentage for Double Digit Value
                self.oled.text(self.percentSymbol, 65, 0)
                self.oled.text(battery_percent_str, 50, 0)
            else:
                ## Shift Percent Symbol inwards towards the Single Digit Value
                self.oled.text(self.percentSymbol, 121, 4)
                self.oled.text(battery_percent_str, 110, 4)
            
            ## The Charging symbol will only appear if the Bank is Charging
            if (previous_battery_voltage < battery_voltage):
                ## Create Charging Symbol
                self.oled.vline(85, 0, 16, 1)
                self.oled.hline(85, 6, 8, 1)	## Create horizontal line at halfway point at charging symbol
#                 self.oled.line(92, 6, 85, 15, 1)		## Implement Line if Sharper Look is Perferred
                self.oled.hline(78, 9, 8, 1)	## Create horizontal line at halfway point at charging symbol
#                 self.oled.line(85, 0, 77, 9, 1)		## Implement Line if Sharper Look is Perferred
                ## Inner Symbol Fillings
                self.oled.fill_rect(82, 6, 5, 4, 1)
                self.oled.fill_rect(85, 6, 4, 4, 1)
                self.oled.fill_rect(83, 2, 2, 4, 1)
                self.oled.fill_rect(79, 7, 12, 2, 1)
                self.oled.fill_rect(85, 8, 4, 4, 1)
                self.oled.fill_rect(89, 9, 1, 1, 1)
                self.oled.fill_rect(86, 12, 1, 3, 1)
                self.oled.fill_rect(81, 4, 3, 3, 1)
                
            # Create Battery Symbol
            self.oled.rect(0, 0, 41, 10, 1)
            self.oled.vline(10, 0, 10, 1)
            self.oled.vline(20, 0, 10, 1)
            self.oled.vline(30, 0, 10, 1)
            self.oled.rect(41, 3, 3, 5, 1)	## Battery Terminal Symbol
        
            ## Create if statements to dicate which inner battery quadrants to fill in depending on battery health levels
            if (3.0 <= battery_voltage <= 3.55):
                print("Filling up 1st quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
            elif (3.55 <= battery_voltage <= 3.70):
                print("Filling up 2nd quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
                self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
            elif (3.70 <= battery_voltage <= 4.0):
                print("Filling up 3rd quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
                self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
                self.oled.fill_rect(22, 1, 8, 8, 1)		## Fill the 3rd quadrant
            elif (4.0 <= battery_voltage <= 4.2):
                print("Filling up 4th quadrant of battery symbol")
                self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
                self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
                self.oled.fill_rect(22, 1, 8, 8, 1)		## Fill the 3rd quadrant
                self.oled.fill_rect(32, 1, 8, 8, 1)		## Fill the last quadrant
            
            self.oled.show()
        elif (battery_percent_str == battery_percent_str):		## If the power bank is idle then power off the oled
            print("Triggering Power Stagnation Condition")
            #self.oled.poweroff()
            self.oled.fill(0)
            self.oled.show()