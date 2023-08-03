import numpy as np

class Wave: 
    def __init__(self, waveform):
        self.signal_gain = 1
        self.signal_mean = 0
        self.noise_mean = 0
        
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
            noise = np.random.normal(self.noise_mean, std_dev)
            self.signal_noise[i] = x + noise
        return self.signal_noise
    
    def add_bias(self, bias_waveform):
        self.signal_bias = [None]*len(self.waveform)
        for i, x in enumerate(self.waveform):
            bias = bias_waveform[i]
            self.signal_bias[i] = x + bias
        return self.signal_bias