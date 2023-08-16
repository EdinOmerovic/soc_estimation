#TODO: add functionality to modify the initial guess and the initial uncertianity

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib.widgets import Slider, Button, RadioButtons

from wave import Wave
# Kalman filter classes
from kalman_filter import Kalman
from kalman_filter2d import KalmanFilter2D
from kalman_matrix import KalmanMatrix
from kalman_soc import KalmanSoC

# Wave duration and size parameters:
T_START = 0
T_STOP = 5
N_POINTS = 500
TIME_STEP = (T_STOP - T_START)/N_POINTS

# Initial noise values
measure_noise_global = 0.25
process_noise_global = 0.001
doprinos_noise_global = 0.005

# Setting up the initial conditions for the estimator
# Initial guess
init_x = 0
# Uncertainty of the initial guess
init_p = 1

# KALMAN FILTER INIT
#kalman_filter = Kalman(init_x, init_x1, init_p, init_p1, initial_measure_noise, initial_measure_noise)
#kalman_filter2d = KalmanFilter2D(TIME_STEP, 0.1, 1.25, 1.25)
#kalman_filterMat = KalmanMatrix(TIME_STEP, initial_process_noise, initial_measure_noise)
kalman_process_noise = process_noise_global
kalman_measure_noise = measure_noise_global
kalman_filter = KalmanSoC(TIME_STEP, kalman_process_noise, kalman_measure_noise, init_x, init_p)


# SIGNAL GENERATION
T_wave = 2  # Time period
SIGNAL_AMPLITUDE = 0.5
SIGNAL_OFFSET = 0.5
# Create a time array
t = np.linspace(T_START, T_STOP, N_POINTS, endpoint=False)
# Generate the sawtooth wave
triangle_wave= SIGNAL_AMPLITUDE*signal.sawtooth(2 * np.pi * 1/T_wave * t, 0.5) + SIGNAL_OFFSET
sine_wave = SIGNAL_AMPLITUDE*np.sin(2 * np.pi * 1/T_wave * t)

# Wave initialization
wave = Wave(triangle_wave)

#bias = 2.5*(signal.sawtooth(2 * np.pi * 2/T_STOP * t, 0.5) + 1)
bias = [0]*len(wave.waveform)

wave.add_noise(measure_noise_global)
wave.add_bias(bias)


def update_sliders(slider_var):
    # Get slider values and update the global values.
    global measure_noise_global, doprinos_noise_global, process_noise_global, kalman_filter
    measure_noise_global = meas_noise_slider.val
    doprinos_noise_global = cum_noise_slider.val
    process_noise_global = process_noise_slider.val
    
    
    # TODO: add feature to add variable noise. I want noise to be a function of state of charge.  
    noisy_measurements = wave.add_noise(measure_noise_global)
    
    # Get all plots from first subplot
    plots = axs[0].get_lines()    
    plots[0].set_ydata(noisy_measurements)
    
    if radio.value_selected == 'Update volt. meas noise': 
        kalman_filter.Q_meas_uncern = measure_noise_global
    elif radio.value_selected == 'Update charge. meas noise': 
        kalman_filter.R_proc_uncern = process_noise_global
    elif radio.value_selected == 'Both':
        kalman_filter.R_proc_uncern = process_noise_global
        kalman_filter.Q_meas_uncern = measure_noise_global
            
    #kalman_filter = KalmanSoC(TIME_STEP, kalman_process_noise, kalman_measure_noise, init_x, init_p)
    iterate_and_plot(wave, kalman_filter, doprinos_noise_global)
    fig.canvas.draw_idle()
    plt.show()
    
    

def plot_values(axs, *argv):
    assert len(argv) == len(axs)
    #Delete any previous plots
    for a in axs:
        a.cla()
    
    
    # First plot is for time plots of the signals
    axs[0].set_title('Estimation based on measurement')
    axs[0].plot(t, argv[0][0], "oy",) #Measured value
    axs[0].plot(t, argv[0][1], "b") #Estimated value
    axs[0].plot(t, argv[0][2]) # Actual value
    axs[0].plot(t, argv[0][3], "g--") # Actual value
    axs[0].legend(["Noisy measurement", "Estimated value (apriori)", "Estimated value (aposteriori)", "True value"])
    axs[0].set_ylim(-0.60, 1.60)    
    axs[0].grid(True)
    
    # Second plot is for the filter internal coefficients
    axs[1].set_title('Estimation uncertainty')
    axs[1].plot(t, argv[1][0])
    axs[1].plot(t, argv[1][1])
    axs[1].legend(["Kalman gain"])
    title.set_text(f"Actual: meas noise = {measure_noise_global}, process noise = {process_noise_global}, cumulative measure noise = {doprinos_noise_global} \n Kalman values: proc uncern = {kalman_filter.R_proc_uncern}, meas uncern = {kalman_filter.Q_meas_uncern} ")
    plt.show()


def iterate_and_plot(wave, kalman_filter, charge_measurement_noise):
    #Initialize all lists to be used for storing the values to be plotted
    
    filtered_values = [None]*len(wave.signal_noise)
    filtered_values1 = [None]*len(wave.signal_noise)
    K_values = [None]*len(wave.signal_noise)
    K_values1 = [None]*len(wave.signal_noise)
    
    previous_x = wave.waveform[0]
    # Iterate through the input wave:
    for i, x in enumerate(wave.signal_noise):
        
        if i == 0: 
            continue
        
        # The virtual charge measurement emulates the task consumption measured by Joulescope.
        # virtual charge measurement = new wave value - previous wave value + noise.
        charge_measurement = np.random.normal(wave.waveform[i] - previous_x, charge_measurement_noise)
        x_apriori = kalman_filter.predict(charge_measurement)
        
        
        # Store the values in the list to be plotted
        filtered_values[i] = x_apriori
        K_values[i] = kalman_filter.K_gain
        
        # KALMAN PREDICT
        # In this case the x is soc evaluation based on the ECM model and OCV-SOC evaluation.
        kalman_filter.update(x)
        
        x_aposteriori = kalman_filter.update(x)
        filtered_values1[i] = x_aposteriori
        K_values1[i] = kalman_filter.K_gain
        
        
        previous_x = wave.waveform[i]
        
    # Plot the wave    
    plot_values(axs, (wave.signal_noise, filtered_values, filtered_values1, wave.waveform), (K_values, K_values1))



# Create an empty canvas for subplots and sliders
fig, axs = plt.subplots(2, 1, figsize=(18, 9))
title = plt.suptitle(t='', fontsize = 12)

# Create space for sliders 
plt.subplots_adjust(bottom=0.20)
# Create sliders for mean and standard deviation

widget_witdh = 0.65
widget_heigth = 0.02

widget_start_x = 0.15
widget_start_y = 0.03

ax_plot_button =              plt.axes([widget_start_x, widget_start_y + 0*1.5*widget_heigth, widget_witdh - 0.2, widget_heigth], facecolor='lightgoldenrodyellow')
ax_std_dev =                  plt.axes([widget_start_x, widget_start_y + 1*1.5*widget_heigth, widget_witdh, widget_heigth], facecolor='lightgoldenrodyellow')
ax_process_noise =            plt.axes([widget_start_x, widget_start_y + 2*1.5*widget_heigth, widget_witdh, widget_heigth], facecolor='lightgoldenrodyellow')
ax_cumulative_measure_noise = plt.axes([widget_start_x, widget_start_y + 3*1.5*widget_heigth, widget_witdh, widget_heigth], facecolor='lightgoldenrodyellow')
ax_radio =                    plt.axes([widget_start_x + widget_witdh + 0.05, widget_start_y, 0.1, 0.1], facecolor='lightgoldenrodyellow')


replot_button = Button(ax_plot_button, 'Plot')
replot_button = Button(ax_plot_button, 'Plot')
meas_noise_slider =    Slider(ax_std_dev, 'Absolute noise (voltage)', 0, 3, valinit=measure_noise_global)
process_noise_slider = Slider(ax_process_noise, 'Process noise', 0, 3, valinit=process_noise_global)
cum_noise_slider =     Slider(ax_cumulative_measure_noise, 'Differential noise (charge)', 0, 3, valinit=doprinos_noise_global)
radio = RadioButtons(ax_radio, ('No update', 'Update volt. meas noise', 'Update charge. meas noise', 'Both'))


#Slider callback functions
process_noise_slider.on_changed(update_sliders)
meas_noise_slider.on_changed(update_sliders)
cum_noise_slider.on_changed(update_sliders)
replot_button.on_clicked(update_sliders)
#radio.on_clicked(radio_update)
        
    
if __name__ == "__main__":
    iterate_and_plot(wave, kalman_filter, doprinos_noise_global)