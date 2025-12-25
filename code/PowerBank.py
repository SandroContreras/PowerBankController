## PowerBank.py
## Author: Sandro Contreras II
## License: MIT
## Description: This file contains the PowerBank class, which handles battery monitoring
##				and OLED display logic.
## Notes:
## - Includes modular methods for power evaluation using voltage divider math
##	 and a Simple Moving Average (SMA) for smoothing. 
## - Designed to be utilized by main.py as a backend.
from machine import Pin, I2C
import ssd1306
import bisect
from machine import ADC

## Create ADC object on an ADC pin
adc = ADC(Pin(26))	## GPIO 26 on Pico is an ADC0 Pin
class BatteryManager:
    def __init__(self, raw, adc_voltage, SMA_battery_voltage, movingAvg, battery_voltage, battery_percentage, BatteryVoltageArr, windowSize):
        self.raw = raw
        self.adc_voltage = adc_voltage
        self.movingAvg = []
        self.windowSize = windowSize
        self.SMA_battery_voltage = SMA_battery_voltage
        self.BatteryVoltageArr = BatteryVoltageArr
        self.battery_voltage = battery_voltage
        self.battery_percentage = battery_percentage
        
    def AppendArray(self, element, windowSize):
        print("Using Append Array")
        print("window Size in Append Array: ", self.windowSize)
        if len(self.BatteryVoltageArr) < self.windowSize:
            self.BatteryVoltageArr.append(element)
    
    def PowerCalculator(self):						## Values 0 - 65535 represents voltages between 0V - 3.3V
        self.raw = adc.read_u16()					## Read a Raw analog value in the range 0 - 65535
        self.adc_voltage = (self.raw * 3.3 / 65535)		## Find Adc Voltage
        self.battery_voltage = self.adc_voltage * 1.47 	## Battery Voltage = Adc Voltage * ((R1+R2) / R2)

        return self.battery_voltage					## R1 = 47k ohm, R2 = 100k ohm
    
    def SetWindowSize(self, battery_voltage):		## Lithium batteries don't charge linearly
        if self.battery_voltage >= 3.92:				## Reduce greater noise before 3.9 V with large SMA window
            self.windowSize = 12
        else:										## Less Noise beyond 3.9V so reduce SMA window
            self.windowSize = 60
            
        return self.windowSize
    
    def BatteryVoltage_SMA(self, battery_voltage, windowSize):

        if (len(self.BatteryVoltageArr) < self.windowSize):
            self.BatteryVoltageArr.append(self.battery_voltage)
        elif len(self.BatteryVoltageArr) == self.windowSize:		## If length of moving data meets the Window Size, then perform SMA
            self.BatteryVoltageArr.pop(0)
            self.BatteryVoltageArr.append(self.battery_voltage)
            self.SMA_battery_voltage = (sum(self.BatteryVoltageArr) / len(self.BatteryVoltageArr))
            
            if (len(self.movingAvg) < 60):	## Handle previous memory crash by limiting Moving Average Array size
                self.movingAvg.append(self.SMA_battery_voltage)
            else:
                self.movingAvg.pop(0)
            
        return self.SMA_battery_voltage
    
    def SOCtable(self, SMA_battery_voltage):
        VoltageRange = [3.0, 3.1, 3.2, 3.3, 3.35, 3.4, 3.55, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.15, 4.2]
        Percentage = [5, 7, 10, 13, 15, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
        Index =  bisect.bisect_right(VoltageRange, self.SMA_battery_voltage) - 1
        return Percentage[Index]
        
    def Check_movingAvgArr(self, movingAvg):
        if (len(self.movingAvg) >= 1):
            return True
        else: return False


class OledUI(BatteryManager):		## Inherit the variables from BatteryManager Class
    def __init__(self, previous_battery_voltage, previous_battery_percent_str, battery_percent_str, oled, battery_voltage, battery_percentage, raw, adc_voltage, BatteryVoltageArr, windowSize, SMA_battery_voltage):
        dummy_raw = 0
        dummy_window_average = 0
        dummy_adc_voltage = 0
         
        super().__init__(dummy_raw, dummy_adc_voltage, dummy_window_average, battery_voltage, battery_percentage, BatteryVoltageArr, windowSize, SMA_battery_voltage)		## I only need variables: battery_voltage, battery_percentage from parent class
        self.oled = oled
        self.percentSymbol = "%"
        
    def BatteryVoltageUpdater(self, previous_SMA_battery_voltage, SMA_battery_voltage):
        previous_SMA_battery_voltage = SMA_battery_voltage
        return previous_SMA_battery_voltage
        
    def DrawBatteryPercentage(self, SMA_battery_voltage, percentSymbol, battery_percent_str):
        
        if (SMA_battery_voltage < 3.2):
            ## Shift Percent Symbol inwards towards the Single Digit Value
            self.oled.text(self.percentSymbol, 65, 4)
            self.oled.text(battery_percent_str, 35, 4)
        elif (SMA_battery_voltage < 4.1):
            ## Display Battery Percentage for Double Digit Value
            self.oled.text(self.percentSymbol, 65, 0)
            self.oled.text(battery_percent_str, 50, 0)
        elif (SMA_battery_voltage >= 4.17):	## Triple digit value display
            self.oled.text(self.percentSymbol, 80, 0)
            self.oled.text(battery_percent_str, 70, 0)
        
    def DrawChargingSymbol(self, previous_SMA_battery_voltage, SMA_battery_voltage):
        print("previous_SMA_battery_voltage = " + str(previous_SMA_battery_voltage))
        print("SMA_battery_voltage = " + str(SMA_battery_voltage))
        
        VoltageChangeRate = SMA_battery_voltage - previous_SMA_battery_voltage
        print("VoltageChangeRate = " + str(VoltageChangeRate))
        
        if (VoltageChangeRate != 0 and VoltageChangeRate > 0.0003):		## The Charging symbol will only appear if the Bank is Charging
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
    
    def FillBatteryQuadrants(self, SMA_battery_voltage):
        print("self.SMA Battery Voltage in Battery Quads: ", SMA_battery_voltage)
        if (3.0 <= SMA_battery_voltage <= 3.55):
            self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
        elif (3.55 <= SMA_battery_voltage <= 3.70):
            self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
            self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
        elif (3.70 <= SMA_battery_voltage <= 4.0):
            self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
            self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
            self.oled.fill_rect(22, 1, 8, 8, 1)		## Fill the 3rd quadrant
        elif (4.0 <= SMA_battery_voltage <= 4.2):
            self.oled.fill_rect(1, 1, 9, 8, 1)		## Fill the 1st quadrant
            self.oled.fill_rect(12, 1, 8, 8, 1)		## Fill the 2nd quadrant
            self.oled.fill_rect(22, 1, 8, 8, 1)		## Fill the 3rd quadrant
            self.oled.fill_rect(32, 1, 8, 8, 1)		## Fill the last quadrant
    
    def BootMSG(self, BatteryVoltageArr):
        print("Inside Boot Message")
        self.oled.fill(0)
        self.oled.text("BatteryArr: " + (str(len(BatteryVoltageArr))), 0, 30, 1)			## Debugging Purposes
#         self.oled.text("WindowSize: " + (str(self.SetWindowSize(self.battery_voltage))), 0, 40, 1)
#         self.oled.text("Booting", 34, 30, 1)		## Boot MSG
#         self.oled.text("PowerCell...", 25, 40, 1)
        self.oled.show()
    
    ## ADD LOGIC THAT ONLY ALLOWS SCREEN UPDATES ONCE WINDOW SIZE EQUALS 60 OR 12
    def OledSignal(self, previous_SMA_battery_voltage, percentSymbol, battery_voltage, previous_battery_percent_str, battery_percent_str, BatteryVoltageArr, windowSize, SMA_battery_voltage, movingAvgArrBool):
        
        print("Length of Battery Voltage Array: ", len(BatteryVoltageArr))
        if (len(BatteryVoltageArr)) < (windowSize):
            self.BootMSG(BatteryVoltageArr)
            
        else:	## if battery_voltage arr == 59 or 11
            print("Exiting Boot Message")
            
            ## Create Power Bank Interaction Signal
            ## The Oled will only display when the charging bank is Charging or Providing Charge
            print("moving Average Array Bool: " + str(movingAvgArrBool))

            if movingAvgArrBool:		## If SMA occured at least once, and the battery difference is beyond flickers
                if (previous_battery_percent_str != battery_percent_str):
                
                    self.oled.fill(0)
                    self.oled.text("Sandro's", 30, 30, 1)		## Signature
                    self.oled.text("Power Bank", 20, 40, 1)
                    
                    self.DrawBatteryPercentage(SMA_battery_voltage, percentSymbol, battery_percent_str)
                    self.DrawChargingSymbol(previous_SMA_battery_voltage, SMA_battery_voltage)
                        
                    # Create Battery Symbol
                    self.oled.rect(0, 0, 41, 10, 1)
                    self.oled.vline(10, 0, 10, 1)
                    self.oled.vline(20, 0, 10, 1)
                    self.oled.vline(30, 0, 10, 1)
                    self.oled.rect(41, 3, 3, 5, 1)	## Battery Terminal Symbol
                
                    self.FillBatteryQuadrants(SMA_battery_voltage)
                    
                    self.oled.show()
