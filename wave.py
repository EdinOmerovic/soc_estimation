import numpy as np

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


class Wave: 
    def __init__(self, waveform):
        self.signal_gain = 1
        self.signal_mean = 0
        self.noise_mean = 0
        
        self.waveform = waveform
        self.signal_noise = [None]*len(self.waveform)
        self.signal_bias = [None]*len(self.waveform)
        
        
    def add_noise(self, std_dev): 
        for i, x in enumerate(self.waveform):
            # std_dev can be a function of a waveform. 
            self.signal_noise[i] = np.random.normal(x + self.noise_mean, std_dev)
        return self.signal_noise
    
    def add_bias(self, bias_waveform):
        if self.signal_noise[0] != None:
            waveform = self.signal_noise
        else:
            waveform = self.waveform
            
        for i, x in enumerate(waveform):
            bias = bias_waveform[i]
            self.signal_bias[i] = x + bias
        return self.signal_bias