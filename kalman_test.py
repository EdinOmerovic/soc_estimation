import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib.widgets import Slider, Button
from matplotlib import animation, rc

from wave import Wave
# Kalman filter classes
from kalman_filter import Kalman
from kalman_filter2d import KalmanFilter2D
from kalman_matrix import KalmanMatrix
from kalman_soc import KalmanSoC

# Wave parameters:
T_START = 0
T_STOP = 5
N_POINTS = 500
TIME_STEP = (T_STOP - T_START)/N_POINTS

initial_measure_noise = 2
initial_process_noise = 0.01
initial_doprinos_noise = 0.05
doprinos_noise = initial_doprinos_noise
# SIGNAL GENERATION
T_wave = 2  # Time period
SIGNAL_AMPLITUDE = 10
# Create a time array
t = np.linspace(T_START, T_STOP, N_POINTS, endpoint=False)
# Generate the sawtooth wave
triangle_wave= SIGNAL_AMPLITUDE*signal.sawtooth(2 * np.pi * 1/T_wave * t, 0.5)
sine_wave = SIGNAL_AMPLITUDE*np.sin(2 * np.pi * 1/T_wave * t)
# Wave initialization
wave = Wave(triangle_wave)
bias = 2.5*(signal.sawtooth(2 * np.pi * 2/T_STOP * t, 0.5) + 1)
wave.add_noise(initial_measure_noise)
#wave.add_bias(bias)


def slider_update_noise(slider_var):
    # Get slider values:
    std_dev_slider = slider_std_dev.val
    doprinos_noise = cumulative_measure_noise.val
    #kalman_filter.measurement_noise = std_dev_slider
    kalman_filter.Q = std_dev_slider
    noisy_measurements = wave.add_noise(std_dev_slider)
    
    # Get all plots from first subplot
    plots = axs[0].get_lines()    
    plots[0].set_ydata(noisy_measurements)
    
    iterate_and_plot(wave, kalman_filter, doprinos_noise)
    fig.canvas.draw_idle()
    plt.show()

def slider_update_process_noise(slider_var):
    #kalman_filter.process_noise = slider_process_noise.val
    kalman_filter.P = slider_process_noise.val
    iterate_and_plot(wave, kalman_filter, doprinos_noise)
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
    axs[0].plot(t, argv[0][2], "g--") # Actual value
    axs[0].set_ylim(-12, 12)    
    axs[0].grid(True)
    axs[0].legend(["Noisy measurement", "Estimated value", "True value"])
    
    # Second plot is for the filter internal coefficients
    axs[1].plot(argv[1][0])
    axs[1].legend(["Kalman gain"])
    title.set_text(f"meas noise = {kalman_filter.Q}, process noise = {kalman_filter.std_acc}, cumulative measure noise = {doprinos_noise}")
    plt.show()


def iterate_and_plot(wave, kalman_filter, doprinos_noise):
    #Initialize all lists to be used for storing the values to be plotted
    
    filtered_values = [None]*len(wave.signal_noise)
    K_values = [None]*len(wave.signal_noise)
    
    previous_x = 0
    # Iterate through the input wave:
    for i, x in enumerate(wave.signal_noise):
        # doprinost = novoizmjerenja vrijednost - prethodna vrijednost.
        doprinos = np.random.normal(wave.waveform[i] - previous_x, doprinos_noise)
        val = kalman_filter.predict(doprinos)
        # Store the values in the list to be plotted
        filtered_values[i] = val
        K_values[i] = kalman_filter.K
        
        # KALMAN PREDICT
        kalman_filter.update(x)
        previous_x = wave.waveform[i]
        
    # Plot the wave    
    plot_values(axs, (wave.signal_noise, filtered_values, wave.waveform), (K_values))



# Create an empty canvas for subplots and sliders
fig, axs = plt.subplots(2, 1, figsize=(6, 9))
# Create sliders for mean and standard deviation
plt.subplots_adjust(bottom=0.25)
ax_cumulative_measure_noise = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_process_noise = plt.axes([0.15, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_std_dev = plt.axes([0.15, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
title = plt.suptitle(t='', fontsize = 20)

slider_process_noise = Slider(ax_process_noise, 'Process noise', 0, 3, valinit=initial_process_noise)
slider_std_dev = Slider(ax_std_dev, 'Std Dev', 0, 10, valinit=initial_measure_noise)
cumulative_measure_noise = Slider(ax_cumulative_measure_noise, 'Cumulative noise', 0, 3, valinit=initial_doprinos_noise)


#Slider callback functions
slider_process_noise.on_changed(slider_update_process_noise)
slider_std_dev.on_changed(slider_update_noise)
cumulative_measure_noise.on_changed(slider_update_noise)



kalman_filter = None
if __name__ == "__main__":
    # Setting up the initial conditions for the estimator
    # Initial guess
    init_x = 0
    init_x1 = 0
    # Variance of the initial guess
    init_p = 1
    init_p1 = 1
    
    #kalman_filter = Kalman(init_x, init_x1, init_p, init_p1, initial_measure_noise, initial_measure_noise)
    #kalman_filter2d = KalmanFilter2D(TIME_STEP, 0.1, 1.25, 1.25)
    #kalman_filterMat = KalmanMatrix(TIME_STEP, initial_process_noise, initial_measure_noise)
    kalman_filter = KalmanSoC(TIME_STEP, initial_process_noise, initial_measure_noise)
    
    iterate_and_plot(wave, kalman_filter, initial_doprinos_noise)
        
    
    