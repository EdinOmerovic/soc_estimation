import numpy as np

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