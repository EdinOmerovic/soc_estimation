import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib.widgets import Slider, Button


from kalman_filter import Kalman


# Parameters for the sawtooth wave
T_wave = 2  # Time period
T_START = 0
T_STOP = 5
N_POINTS = 1000
TIME_STEP = (T_STOP - T_START)/N_POINTS
initial_std_dev = 1
initial_process_noise = 1
noise_mean = 0
signal_mean = 0

class Wave: 
    def __init__(self, waveform):
        self.waveform = waveform
        self.signal_noise = None
        self.signal_bias = None
        
    def add_noise(self, std_dev):
        self.signal_noise = [None]*len(self.waveform)
        if self.signal_bias != None:
            waveform = self.signal_bias
        else:
            waveform = self.waveform
            
        for i, x in enumerate(waveform):
            noise = np.random.normal(noise_mean, std_dev)
            self.signal_noise[i] = x + noise
        return self.signal_noise
    
    def add_bias(self, bias_waveform):
        self.signal_bias = [None]*len(self.waveform)
        for i, x in enumerate(self.waveform):
            bias = bias_waveform[i]
            self.signal_bias[i] = x + bias
        return self.signal_bias


def slider_update_noise(slider_var):
    plots = axs[0].get_lines()
    std_dev_slider = slider_std_dev.val
    kalman_filter.measurement_noise = std_dev_slider
    noisy_measurements = wave.add_noise(std_dev_slider)
    plots[0].set_ydata(noisy_measurements)
    iterate_and_plot(wave, kalman_filter)
    fig.canvas.draw_idle()
    plt.show()

def slider_update_process_noise(slider_var):
    kalman_filter.process_noise = slider_process_noise.val
    iterate_and_plot(wave, kalman_filter)
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
    axs[0].set_ylim(-8, 8)    
    axs[0].grid(True)
    axs[0].legend(["Mjerenje", "Estimirana vrijednost", "Stvarna vrijednost"])
    # Second plot is for the filter internal coefficients
    axs[1].plot(argv[1][0])
    axs[1].plot(argv[1][1])
    axs[1].plot(argv[1][2])
    axs[1].legend(["K1", "K2", "K3"])
    plt.show()



def iterate_and_plot(wave, kalman_filter):
    #Initialize all lists to be used for storing the values to be ploted
    filtered_values = [None]*len(wave.signal_noise)
    K1_values = [None]*len(wave.signal_noise)
    K2_values = [None]*len(wave.signal_noise)
    K3_values = [None]*len(wave.signal_noise)
    
    for i, x in enumerate(wave.signal_noise):
        # KALMAN MEASURE
        # KALMAN UPDATE
        val = kalman_filter.update(x, TIME_STEP)
        # Store the values in the list to be plotted
        filtered_values[i] = val.current_estimate_x1
        K1_values[i] = val.Kn1
        K2_values[i] = val.Kn2
        K3_values[i] = val.Kn3
        # KALMAN PREDICT
        kalman_filter.predict(TIME_STEP)

    # Plot the wave    
    plot_values(axs, (wave.signal_noise, filtered_values, wave.waveform), (K1_values, K2_values, K3_values))



# Create an empty canvas for subplots and sliders
fig, axs = plt.subplots(2, 1, figsize=(6, 9))
# Create sliders for mean and standard deviation
plt.subplots_adjust(bottom=0.25)
ax_process_noise = plt.axes([0.15, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_std_dev = plt.axes([0.15, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider_process_noise = Slider(ax_process_noise, 'Process noise', 0, 3, valinit=initial_process_noise)
slider_std_dev = Slider(ax_std_dev, 'Std Dev', 0, 3, valinit=initial_std_dev)

#Slider callback functions
slider_process_noise.on_changed(slider_update_process_noise)
slider_std_dev.on_changed(slider_update_noise)

# Create a time array
t = np.linspace(T_START, T_STOP, N_POINTS, endpoint=False)
# Generate the sawtooth wave
#triangle_wave= signal.sawtooth(2 * np.pi * 1/T * t, 0.5)
sine_wave = (2*np.sin(2 * np.pi * 1/T_wave * t) + signal_mean)
wave = Wave(sine_wave)

kalman_filter = None
if __name__ == "__main__":
    
    bias = 2.5*(signal.sawtooth(2 * np.pi * 2/T_STOP * t, 0.5) + 1)
    #wave.add_bias(bias)
    wave.add_noise(initial_std_dev)

    # Setting up the initial conditions for the estimator
    # Initial guess
    init_x = 0
    init_x1 = 0
    # Variance of the initial guess
    init_p = 10
    init_p1 = 10
    
    kalman_filter = Kalman(init_x, init_x1, init_p, init_p1, initial_std_dev, initial_std_dev)
    
    iterate_and_plot(wave, kalman_filter)
        
    
    
    

    
