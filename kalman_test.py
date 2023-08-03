import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib.widgets import Slider, Button


from kalman_filter import Kalman
from kalman_filter2d import KalmanFilter2D
#from kalman_matrix import KalmanMatrix
from kalman_soc import KalmanMatrix
from wave import Wave
# Parameters for the sawtooth wave
T_wave = 2  # Time period
T_START = 0
T_STOP = 5
N_POINTS = 5000
TIME_STEP = (T_STOP - T_START)/N_POINTS
initial_measure_noise = 10
initial_process_noise = 0.1

# SIGNAL GENERATION
SIGNAL_AMPLITUDE = 10
# Create a time array
t = np.linspace(T_START, T_STOP, N_POINTS, endpoint=False)
# Generate the sawtooth wave
triangle_wave= SIGNAL_AMPLITUDE*signal.sawtooth(2 * np.pi * 1/T_wave * t, 0.5)
sine_wave = SIGNAL_AMPLITUDE*np.sin(2 * np.pi * 1/T_wave * t)



#    # Setting up the initial conditions for the estimator
# Initial guess
init_x = 0
init_x1 = 0
# Variance of the initial guess
init_p = 1
init_p1 = 1
    
    
def slider_update_noise(slider_var):
    plots = axs[0].get_lines()
    std_dev_slider = slider_std_dev.val
    #kalman_filter.measurement_noise = std_dev_slider
    kalman_filterMat.std_meas = std_dev_slider
    noisy_measurements = wave.add_noise(std_dev_slider)
    plots[0].set_ydata(noisy_measurements)
    iterate_and_plot(wave, kalman_filterMat)
    fig.canvas.draw_idle()
    plt.show()

def slider_update_process_noise(slider_var):
    #kalman_filter.process_noise = slider_process_noise.val
    kalman_filterMat.std_acc = slider_process_noise.val
    iterate_and_plot(wave, kalman_filterMat)
    fig.canvas.draw_idle()
    plt.show()
    

def plot_values(axs, *argv):
    assert len(argv) == len(axs)
    #Delete any previous plots
    for a in axs:
        a.cla()
    
    # First plot is for time plots of the signals
    axs[0].set_title('Estimacija stanja na bazi mjerenja: sinusni signal')
    axs[0].plot(t, argv[0][0], "oy",) #Measured value
    axs[0].plot(t, argv[0][1], "b") #Estimated value
    axs[0].plot(t, argv[0][2], "g--") # Actual value
    axs[0].set_ylim(-12, 12)    
    axs[0].grid(True)
    axs[0].legend(["Mjerenje", "Estimirana vrijednost", "Stvarna vrijednost"])
    # Second plot is for the filter internal coefficients
    axs[1].plot(argv[1][0])
    axs[1].plot(argv[1][1])
    #axs[1].plot(argv[1][2])
    axs[1].legend(["vel", "acc"])
    plt.show()



def iterate_and_plot(wave, kalman_filter):
    #Initialize all lists to be used for storing the values to be plotted
    
    filtered_values = [None]*len(wave.signal_noise)
    K1_values = [None]*len(wave.signal_noise)
    K2_values = [None]*len(wave.signal_noise)
    K3_values = [None]*len(wave.signal_noise)
    
    vel = [None]*len(wave.signal_noise)
    acc = [None]*len(wave.signal_noise)
    
    previous_x = 0
    for i, x in enumerate(wave.signal_noise):
        # KALMAN MEASURE
        # KALMAN UPDATE
        
        
        # doprinost = novoizmjerenja vrijednost - prethodna vrijednost.
        #doprinos = wave.waveform[i] - previous_x
        doprinos = 0
        val = kalman_filter.predict(doprinos)
        
        
        
        # Store the values in the list to be plotted
        filtered_values[i] = val
        #K1_values[i] = val.Kn1
        #K2_values[i] = val.Kn2
        #K3_values[i] = val.Kn3
        #vel[i] = val.item(1)
        #acc[i] = val.item(2)
        
        
        # KALMAN PREDICT
        kalman_filter.update(x)
        previous_x = wave.waveform[i]
        
    # Plot the wave    
    plot_values(axs, (wave.signal_noise, filtered_values, wave.waveform), (vel, acc))



# Create an empty canvas for subplots and sliders
fig, axs = plt.subplots(2, 1, figsize=(6, 9))
# Create sliders for mean and standard deviation
plt.subplots_adjust(bottom=0.25)
ax_process_noise = plt.axes([0.15, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_std_dev = plt.axes([0.15, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider_process_noise = Slider(ax_process_noise, 'Process noise', 0, 3, valinit=initial_process_noise)
slider_std_dev = Slider(ax_std_dev, 'Std Dev', 0, 10, valinit=initial_measure_noise)

#Slider callback functions
slider_process_noise.on_changed(slider_update_process_noise)
slider_std_dev.on_changed(slider_update_noise)



kalman_filter = None
if __name__ == "__main__":
    
    wave = Wave(triangle_wave)
    bias = 2.5*(signal.sawtooth(2 * np.pi * 2/T_STOP * t, 0.5) + 1)
    
    #wave.add_bias(bias)
    wave.add_noise(initial_measure_noise)
    
    
    #kalman_filter = Kalman(init_x, init_x1, init_p, init_p1, initial_measure_noise, initial_measure_noise)
    #kalman_filter2d = KalmanFilter2D(TIME_STEP, 0.1, 1.25, 1.25)
    #kalman_filterMat = KalmanMatrix(TIME_STEP, initial_process_noise, initial_measure_noise)
    kalman_filterMat = KalmanMatrix(TIME_STEP, initial_process_noise, initial_measure_noise)
    
    
    #filter_list = [kalman_filter, kalman_filter2d, kalman_filterMat]
    
     
    iterate_and_plot(wave, kalman_filterMat)
        
    
    