import re
import itertools
import csv
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from statistics import mean 

import os

from kalman_soc import KalmanSoC

ground_truth_filename = "unified_20220430_113319_adjusted_time.csv"
power_supply_filename = "output_validation_discharge.csv"
ground_truth_cache_filename = "ground_truth_cache.csv"


experiment_start = "2022-04-30 11:34:02.094441"


sleep_charge = 0
sleep_charge_uncert = 0.1


active_charge_uncert = 0.0001

voltage1_process_uncert = 0.15
voltage2_process_uncert = 0.05
V1_uncert = 0.15
V2_uncert = 0.15

#SoC(Voc_bat) obtained from nominal discharge curve
SOC_FROM_VBAT = [(1.7, 0),
                 (2, 0.1),
                 (2.2, 0.13),
                 (2.3, 0.165),
                 (2.4, 0.276 + 0.1),
                 (2.6, 0.8),
                 (2.7, 0.929134),
                 (2.8, 0.976378),
                 (3, 1),
]





SOC_FROM_VBAT = [
    (2.0986206896551725, 0),
    (2.1, 0.0021227684030324934),
    (2.2117241379310344, 0.020963560772805145),
    (2.363448275862069, 0.053416483247737734),
    (2.4379310344827587, 0.09339691856199561),
    (2.4958620689655175, 0.14466617754952305),
    (2.5593103448275865, 0.21013939838591333),
    (2.6227586206896554, 0.3288041085840059),
    (2.7193103448275866, 0.55680606505258),
    (2.788275862068966, 0.7847101980924431),
    (2.832413793103449, 0.9614624602592321),
    (2.8600000000000003, 0.9771631205673759),
    (2.898620689655173, 0.99006603081438),
    (2.9648275862068973, 0.994556126192223),
    (3.1, 1)
]



SOC_FROM_VBAT1 = [
        (2.3,	        0),
        (2.437931034,	0.093396919),
        (2.495862069,	0.144666178),
        (2.559310345,	0.210139398),
        (2.622758621,	0.328804109),
        (2.719310345,	0.556806065),
        (2.788275862,	0.724710198),
        (2.832413793,	0.821462460),
        (3        ,   1)
]

VBAT_FROM_SOC = [(val[1], val[0]) for val in SOC_FROM_VBAT]

# Setting up the initial conditions for the estimator
# Initial guess
init_soc = 1

# Uncertainty of the initial guess
init_p = 0.01

BATTERY_CAPACITY = 12 #Coulomb hours

gt_count = 0
with open(ground_truth_filename) as fp:
    for (gt_count, _) in enumerate(fp, 1):
        pass
    
    
    
#Linear interpolation
def interpolate(x, array):
    if x < array[0][0]: return array[0][1]
    if x > array[-1][0]: return array[-1][1]
    for i, val in enumerate(array):
        if val[0] == x: return val[1] 
        elif val[0] > x:
            (x1, y1) = array[i - 1]
            (x2, y2) = array[i]
            y = (x*(y1 - y2) + x1*y2 - x2*y1)/(x1 - x2)
            return y
    return None

def soc_from_vbat_rising(v_bat):
    #Based on the ECM model this should return the SOC based on the voltage measurement BEFORE the task
    return interpolate(v_bat+0.25, SOC_FROM_VBAT)#TODO: add SoC estimate from the Voc obtained from the ECM model
    
    
def soc_from_vbat_falling(v_bat):
    #Based on the ECM model this should return the SOC based on the voltage measurement AFTER the task
    return interpolate(v_bat+0.25, SOC_FROM_VBAT) #TODO: add SoC estimate from the Voc obtained from the ECM model

def get_effective_charge(current, charge, coefs):
    return current*charge

def ocv_from_vbat(vbat):
    return vbat + 0.25

class Algorithm:
    def __init__(self, init_value, init_p):
        self.kalman_filter1 = KalmanSoC(sleep_charge_uncert, V1_uncert, init_value, init_p)
        self.kalman_filter2 = KalmanSoC(active_charge_uncert, V2_uncert, init_value, init_p)
        
        self.voltage1_kalman =  KalmanSoC(voltage1_process_uncert, V1_uncert, interpolate(init_value, VBAT_FROM_SOC), init_p)
        self.voltage2_kalman =  KalmanSoC(voltage2_process_uncert, V2_uncert, interpolate(init_value, VBAT_FROM_SOC), init_p)
        
        self.init_value = init_value
        self.aposteriori1 = init_value
        self.aposteriori2 = init_value
    
    def before_task(self, sleep_charge, sleep_charge_uncert, v1, v1_uncert):
        # Estimated charge measurements during sleep
        #self.kalman_filter.R_proc_uncern = sleep_charge_uncert
        #self.kalman_filter.Q_meas_uncern = soc_from_v1_uncert 
        self.kalman_filter1.x = self.kalman_filter2.x
        new_soc = self.kalman_filter1.predict(sleep_charge)
        # Voltage measurement before the pulse
        
        # self.kalman_filter1.x ti je svakako vracen sa predictom.
        voc_from_soc = interpolate(new_soc , VBAT_FROM_SOC)
        
        self.voltage1_kalman.predict(voc_from_soc - self.voltage1_kalman.x)
        soc_form_vbat = interpolate(self.voltage1_kalman.update(ocv_from_vbat(v1)), SOC_FROM_VBAT)
        
        self.aposteriori1 = self.kalman_filter1.update(soc_form_vbat + (self.kalman_filter2.x - self.kalman_filter1.x))
        
    def after_task(self, active_charge, active_charge_uncert, v2, v2_uncert):
        # Estimated charge measurements during active period
        #self.kalman_filter.R_proc_uncern = active_charge_uncert
        #self.kalman_filter.Q_meas_uncern = soc_from_v2_uncert
        new_soc = self.kalman_filter2.predict(active_charge)
        
        voc_from_soc = interpolate(new_soc, VBAT_FROM_SOC)
        self.voltage2_kalman.predict(voc_from_soc - self.voltage2_kalman.x)
        
        # od v2 mi bismo trebali dobiti ocv preko modela. 
        soc_from_vbat = interpolate(self.voltage2_kalman.update(ocv_from_vbat(v2)), SOC_FROM_VBAT)
        
        
        # Voltage measurement before the pulse
        self.aposteriori2 = self.kalman_filter2.update(mean([soc_from_vbat, self.kalman_filter1.x]))
        #self.kalman_filter2.x = mean([self.aposteriori1, self.aposteriori2])





def parse_csv(row):
    current = float(row[0])
    pulse_duration = float(row[1])
    pulse_start = row[2]
    v1 = float(row[3])
    pulse_end = row[4]
    v2 = float(row[5])
    return current, pulse_duration, v1, v2, pulse_start, pulse_end 



def write_to_chache(ground_truth_cache_filename, row):
    # Make a file which is used for cacheint values. 
    # Create a chache file if it doesn't exist
    with open(ground_truth_cache_filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)
        

# The problem with this search is that it can't find an element sometimes. 
def try_reading_cache(time_since_start):
    if os.path.exists(ground_truth_cache_filename):         
        with open(ground_truth_cache_filename, 'r') as cache_file:
            start = 0   # First row in the .csv
            end = cache_file.seek(0,2) # Last row in the .csv
            cache_file.seek(0)
            
            while start <= end:
                mid = (start + end) // 2
                
                cache_file.seek(mid)
                cache_file.readline()
                
                line = cache_file.readline()
                if line == '':
                    break
                row1 = line.strip().split(",")
                
                index = float(row1[0])
                target_index = round(round(2*time_since_start)/2, 1)
                
                if index == target_index:
                    # Return the cached value. 
                    return float(row1[4])
                elif index < target_index:
                    start = cache_file.tell()
                else:
                    end = mid - 1
    return None
    
'''
    Obtain the accumulated charge in a certain time measured by Joulescope (ground truth) 
'''
def get_charge_from_jls(time_since_start):
    # TRY READING IN CACHE: 
    # cached_value = try_reading_cache(time_since_start)
    # if cached_value != None:
    #     return cached_value
    
    # NOTHING FOUND IN THE CACHE, GOING THROUGH THE WHOLE .csv file
    row1 = None
    with open(ground_truth_filename, 'r') as file:
        start = 0
        end = file.seek(0, 2)
        file.seek(0)
        
        while start <= end:
            mid = (start + end) // 2
            file.seek(mid)
            file.readline()
            
            line = file.readline() # Read the next full line
            row1 = line.strip().split(",") # Assuming CSV is comma-delimited
            
            index = float(row1[0])
            target_index = round(round(2*time_since_start)/2, 1) 
            
            if index == target_index:
                #print("Nasao i ubacio")
                #write_to_chache(ground_truth_cache_filename, [float(x) for x in row1])
                return float(row1[4])
            elif index < round(time_since_start):
                start = file.tell()
            else:
                end = mid - 1
    
    # The binary search haven't found that element. Giving our final best bet. 
    return float(row1[4])

def get_seconds(date1_str, date2_str):
    time_diff = datetime.strptime(date2_str, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(date1_str, "%Y-%m-%d %H:%M:%S.%f")
    return time_diff.total_seconds()
   
if __name__ == "__main__":    
    # Iterate through the pure SoC-Voc lookup table
    v_bat_plot = np.linspace(SOC_FROM_VBAT[0][0], SOC_FROM_VBAT[-1][0], num=100)
    soc_from_vbat_plot = [interpolate(x, SOC_FROM_VBAT) for i,x in enumerate(v_bat_plot)]
    # Create a figure for that an plot it. 
    plt.figure()
    plt.plot(soc_from_vbat_plot[::-1], v_bat_plot) #Estimate before the task
    
    # Initialize the high level algorithm
    soc_algoritm = Algorithm(init_soc, init_p)
    
    
    # Read the .csv to see how many rows there is.
    with open(power_supply_filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        num_elements = sum(1 for row in datareader) 
    
    true_charge_values1 = [None]*num_elements
    true_charge_values2 = [None]*num_elements
    appriori_values = [None]*num_elements
    aposteriori_values = [None]*num_elements
    pure_voltage_v1 = [None]*num_elements
    pure_voltage_v2 = [None]*num_elements
    true_time1_values = [None]*num_elements
    true_time2_values = [None]*num_elements
    average_values = [None]*num_elements
        
    # Read the .csv containing the data made by power supply
    with open(power_supply_filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        for i, row in enumerate(datareader):
            # Read a csv row.
            current, duration, V1, V2, date1, date2 = parse_csv(row)
            
            # @ TIME 1
            time_before_pulse = get_seconds(experiment_start, date1)
            # When the MCU wakes up, it has an idea of how much energy it spent in the sleep mode.
            # Difference in SoC due to sleep period
            
            soc_algoritm.before_task(sleep_charge, sleep_charge_uncert, V1, V1_uncert)
            
            
            appriori_values[i] = soc_algoritm.aposteriori1
            true_charge_values1[i] = 1 - get_charge_from_jls(time_before_pulse)/float(BATTERY_CAPACITY)
            true_time1_values[i] = time_before_pulse
            pure_voltage_v1[i] = soc_from_vbat_rising(V1) 
            
            # @ TIME 2
            time_after_pulse = get_seconds(experiment_start, date2)
            # Later, the microcontroler executes a certain task, and spends some of battery state of charge.  
            active_charge = get_effective_charge(current, duration, 1)/float(BATTERY_CAPACITY)

            soc_algoritm.after_task(active_charge, active_charge_uncert, V2, V2_uncert)
            
            
            aposteriori_values[i] = soc_algoritm.aposteriori2
            pure_voltage_v2[i] = soc_from_vbat_falling(V2)
            true_charge_values2[i] = 1 - get_charge_from_jls(time_after_pulse)/BATTERY_CAPACITY
            true_time2_values[i] = time_after_pulse
            
            print(f"{appriori_values[i]}, {true_charge_values1[i]}, {true_time1_values[i]}| {aposteriori_values[i]},{true_charge_values2[i]},{true_time2_values[i]}")
        
        # After iterating through the csv file, plot all of the values
        # Create an empty canvas for subplots and sliders
        fig, axs = plt.subplots(2, 1, figsize=(18, 9))
        
        kalman1_mse = sum((100*(x1-x2))**2 for x1, x2 in zip(true_charge_values1, appriori_values))/num_elements
        voltage1_mse = sum((100*(x1-x2))**2 for x1, x2 in zip(true_charge_values1, pure_voltage_v1))/num_elements
        
        kalman2_mse = sum((100*(x1-x2))**2 for x1, x2 in zip(true_charge_values1, aposteriori_values))/num_elements
        voltage2_mse = sum((100*(x1-x2))**2 for x1, x2 in zip(true_charge_values1, pure_voltage_v2))/num_elements
        
        
        title = plt.suptitle(t=f"Voltage-based MSE: {voltage1_mse} | Kalman filter MSE: {kalman2_mse} \n Voltage-based MSE: {voltage2_mse} | Kalman filter MSE: {kalman2_mse}", fontsize = 12)
        
        axs[0].plot(true_time1_values, pure_voltage_v1, '0.7') #Estimate before the task
        axs[0].plot(true_time1_values, appriori_values, "b") #Estimate before the task
        #axs[0].plot(true_time1_values, average_values1) #Estimate before the task
        axs[0].plot(true_time1_values, true_charge_values1, "g-") #Estimate before the task
        
        axs[1].plot(true_time2_values, pure_voltage_v2, '0.7') # Estimate after the task
        axs[1].plot(true_time2_values, aposteriori_values, "b") # Estimate after the task
        #axs[1].plot(true_time2_values, average_values2) # Estimate after the task
        axs[1].plot(true_time2_values, true_charge_values2, "g-") # Estimate after the task
        plt.show()