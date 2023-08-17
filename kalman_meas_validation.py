import csv
from kalman_soc import KalmanSoC
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

ground_truth_filename = "unified_20220430_113319_adjusted_time.csv"
power_supply_filename = "output_validation_discharge.csv"



experiment_start = "2022-04-30 11:34:02.094441"

# Initial noise values
measure_noise_global = 0.25
process_noise_global = 0.0001
doprinos_noise_global = 0.005
TIME_STEP = 0 #FIXME



#SoC(Voc_bat) obtained from nominal discharge curve
SOC_FROM_VBAT = [
        (2.33,	        0),
        (2.437931034,	0.093396919),
        (2.495862069,	0.144666178),
        (2.559310345,	0.210139398),
        (2.622758621,	0.328804109),
        (2.719310345,	0.556806065),
        (2.788275862,	0.724710198),
        (2.832413793,	0.821462460),
        (3        ,   1)
]

# Setting up the initial conditions for the estimator
# Initial guess
init_x = 1
# Uncertainty of the initial guess
init_p = 1

kalman_process_noise = process_noise_global
kalman_measure_noise = measure_noise_global
BATTERY_CAPACITY = 12 #Coulomb hours


class Algorithm:
    def __init__(self, init_value):
        self.kalman_filter = KalmanSoC(TIME_STEP, kalman_process_noise, kalman_measure_noise, init_x, init_p)
        self.init_value = init_value
        self.aposteriori1 = init_value
        self.aposteriori2 = init_value
    
    def before_task(self, sleep_charge, sleep_charge_uncert, soc_from_v1, soc_from_v1_uncert):
        # Estimated charge measurements during sleep
        self.kalman_filter.R_proc_uncern = sleep_charge_uncert
        self.kalman_filter.predict(sleep_charge)
        # Voltage measurement before the pulse
        self.kalman_filter.Q_meas_uncern = soc_from_v1_uncert
        self.aposteriori1 = self.kalman_filter.update(soc_from_v1)
        
    def after_task(self, active_charge, active_charge_uncert, soc_from_v2, soc_from_v2_uncert):
        # Estimated charge measurements during active period
        self.kalman_filter.R_proc_uncern = active_charge_uncert
        self.kalman_filter.predict(active_charge)
        # Voltage measurement before the pulse
        self.kalman_filter.Q_meas_uncern = soc_from_v2_uncert
        self.aposteriori1 = self.kalman_filter.update(soc_from_v2)

def get_effective_charge(current, charge, coefs):
    return current*charge


def parse_csv(row):
    current = float(row[0])
    pulse_duration = float(row[1])
    pulse_start = row[2]
    v1 = float(row[3])
    pulse_end = row[4]
    v2 = float(row[5])
    return current, pulse_duration, v1, v2, pulse_start, pulse_end 



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
    return interpolate(v_bat, SOC_FROM_VBAT) #TODO: add SoC estimate from the Voc obtained from the ECM model
    
    
def soc_from_vbat_falling(v_bat):
    #Based on the ECM model this should return the SOC based on the voltage measurement AFTER the task
    return interpolate(v_bat, SOC_FROM_VBAT) #TODO: add SoC estimate from the Voc obtained from the ECM model


def get_charge_from_jls(time_since_start):
    # Open the a file made by Joulescope, search for the index with time specified.
    with open(ground_truth_filename, 'r') as file:
        reader = csv.reader(file)
        for i, row1 in enumerate(reader):
            if i == 0: 
                continue #Skip the first header row
            
            if float(row1[0]) == round(time_since_start):
                return float(row1[4])

        return None

def get_seconds(date1_str, date2_str):
    time_diff = datetime.strptime(date2_str, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(date1_str, "%Y-%m-%d %H:%M:%S.%f")
    return time_diff.total_seconds()
    
if __name__ == "__main__":
    # Initialize the high level algorithm
    soc_algoritm = Algorithm(1)
    
    
    # Read the .csv to see how many rows there is.
    with open(power_supply_filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        num_elements = sum(1 for row in datareader) 
    
    true_charge_values1, true_charge_values2, appriori_values, aposteriori_values,true_time1_values,true_time2_values = [None]*num_elements
        
    # Read the .csv containing the data made by power supply
    with open(power_supply_filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        for i, row in enumerate(datareader):
            # Read a csv row.
            current, duration, V1, V2, date1, date2 = parse_csv(row)
            
            # @ TIME 1
            before_pulse_time = get_seconds(experiment_start, date1)
            # When the MCU wakes up, it has an idea of how much energy it spent in the sleep mode.
            # Difference in SoC due to sleep period
            sleep_charge = 0
            sleep_charge_uncert = 1
            # It can take a battery voltage measurement
            soc_from_v1 = soc_from_vbat_rising(V1)
            soc_from_v1_uncert = 1
            
            soc_algoritm.before_task(sleep_charge, sleep_charge_uncert, soc_from_v1, soc_from_v1_uncert)
            appriori_values[i] = soc_algoritm.aposteriori1
            true_charge_values1[i] = get_charge_from_jls(before_pulse_time)/float(BATTERY_CAPACITY)
            true_time1_values[i] = before_pulse_time
            
            # @ TIME 2
            after_pulse_time = get_seconds(experiment_start, date2)
            # Later, the microcontroler executes a certain task, and spends some of battery state of charge.  
            active_charge = -1 * get_effective_charge(current, duration, 1)/BATTERY_CAPACITY
            active_charge_uncert = 0.01
            
            # Finally,  it measures the voltage again and goes back to sleep. 
            soc_from_v2 = soc_from_vbat_falling(V2)
            soc_from_v2_uncert = 1
            soc_algoritm.after_task(active_charge, active_charge_uncert, soc_from_v2, soc_from_v2_uncert)
            aposteriori_values[i] = soc_algoritm.aposteriori2
            # aprox. Actual charge readings during this time.
            true_charge_values2[i] = get_charge_from_jls(after_pulse_time)/BATTERY_CAPACITY
            true_time2_values = after_pulse_time
        
        
        # After iterating through the csv file, plot all of the values
        # Create an empty canvas for subplots and sliders
        fig, axs = plt.subplots(2, 1, figsize=(18, 9))
        title = plt.suptitle(t='', fontsize = 12)
        axs[0].plot(true_time1_values, appriori_values, "oy") #Estimate before the task
        axs[0].plot(true_time1_values, true_charge_values1, "oy") #Estimate before the task
        
        axs[1].plot(true_time2_values, aposteriori_values) # Estimate after the task
        axs[1].plot(true_time2_values, true_charge_values2) # Estimate after the task
        plt.show()