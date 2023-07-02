from kalman_filter import Kalman

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Parameters for the sawtooth wave
T = 0.5   # Time period
T_START = 0
T_STOP = 5
N_POINTS = 100000


if __name__ == "__main__":
    # Generate the sawtooth wave
    t = np.linspace(T_START, T_STOP, N_POINTS, endpoint=False)  # Time array
    #wave = signal.sawtooth(2 * np.pi * 1/T * t, 0.5)
    wave = np.sin(2 * np.pi * 1/T * t)

    mean = 0
    std_dev = 1  # Standard deviation
    noise = np.random.normal(mean, std_dev, size=wave.shape) 


    signal = wave + noise
    init_x = 0
    init_x1 = 0
    init_p = 10
    init_p1 = 10
    init_q = 0.00001
    init_r = 1
    kalman_filter = Kalman(init_x, init_x1, init_p, init_p1, init_q, init_r)
    filtered_values = []
    TIME_STEP = (T_STOP - T_START)/N_POINTS
    for x in signal:
        val = kalman_filter.update(x)
        filtered_values.append(val)
        kalman_filter.predict(TIME_STEP)

    # Plot the wave
    plt.figure(figsize=(8,6))
    plt.title('Sawtooth wave')
    plt.plot(t, signal)
    plt.plot(t, wave)
    plt.plot(t, filtered_values)
    plt.ylim(-3, 3)
    plt.grid(True)
    plt.show()
