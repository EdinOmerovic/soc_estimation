import os
import csv
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime


from wave import interpolate
from soc_algorithm import Algorithm
from battery_parameters import SOC_FROM_VBAT, VBAT_FROM_SOC, get_effective_charge, soc_from_vbat_rising, soc_from_vbat_falling, BATTERY_CAPACITY

#TODO: enable running of the tests from cached input data. 

ground_truth_filename = "unified_20220430_113319_adjusted_time.csv"
power_supply_filename = "output_validation_discharge.csv"
ground_truth_cache_filename = "ground_truth_cache.csv"
experiment_start = "2022-04-30 11:34:02.094441"


# Setting up the initial conditions for the estimator

# Initial guess
init_soc = 1
# Uncertainty of the initial guess
init_p = 0.01

sleep_charge = 0
sleep_charge_uncert = 0.0001
V1_uncert = 0.595
active_charge_uncert = 0.0001
V1_uncert = 0.595
V2_uncert = 0.5


gt_count = 0
with open(ground_truth_filename) as fp:
    for (gt_count, _) in enumerate(fp, 1):
        pass
    

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
   
# Experimented with variable uncertainity  
# def voc_uncert(vbat):
#     return 
#     if vbat > 2.7 or (vbat < 2.2 and vbat > 1):
#         return 0.1
#     else: 
#         return 0.5
   
if __name__ == "__main__":    
    # Iterate through the pure SoC-Voc lookup table
    v_bat_plot = np.linspace(SOC_FROM_VBAT[-1][0], SOC_FROM_VBAT[0][0], num=100)
    soc_from_vbat_plot = [interpolate(x, SOC_FROM_VBAT) for i,x in enumerate(v_bat_plot)]
    
    # Create a figure for that an plot it. 
    plt.figure()
    plt.plot(soc_from_vbat_plot, v_bat_plot) #Estimate before the task
    plt.gca().invert_xaxis()
    plt.xlabel("SoC [%]")
    plt.ylabel("OCV [V]")
    plt.title("SOC-OCV curve from battery discharge test")
    
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
        
        
        title = plt.suptitle(t="State of charge estimation using KF", fontsize = 12)
        
        axs[0].plot(true_time1_values, pure_voltage_v1, '0.7') #Estimate before the task
        axs[0].plot(true_time1_values, appriori_values, "b") #Estimate before the task
        #axs[0].plot(true_time1_values, average_values1) #Estimate before the task
        axs[0].plot(true_time1_values, true_charge_values1, "g-") #Estimate before the task
        axs[0].legend(["Voltage 1 eval.", "Before task est.", "True value"])
        axs[0].set_title(f"Voltage-based MSE: {voltage1_mse:.4f} | Kalman filter MSE: {kalman1_mse:.4f}")
        axs[0].set_xlabel("time (s)")
        axs[0].set_ylabel("SoC (%)")
        
        
        axs[1].plot(true_time2_values, pure_voltage_v2, '0.7') # Estimate after the task
        axs[1].plot(true_time2_values, aposteriori_values, "b") # Estimate after the task
        #axs[1].plot(true_time2_values, average_values2) # Estimate after the task
        axs[1].plot(true_time2_values, true_charge_values2, "g-") # Estimate after the task
        axs[1].legend(["Voltage 2 eval.", "After task est.", "True value"])
        axs[1].set_ylabel("SoC (%)")
        axs[1].set_xlabel("time (s)")
        axs[1].set_title(f"Voltage-based MSE: {voltage2_mse:.4f} | Kalman filter MSE: {kalman2_mse:.4f}")
        plt.show()