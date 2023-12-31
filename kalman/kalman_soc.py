'''
Simple 1D implementation of Kalman filter used for combining the voltage based state of charge estimation and charge.

TODO: add the ability to modify the variances during the execution. 
'''

import numpy as np

class KalmanSoC():
    def __init__(self, init_proc_uncern, init_meas_uncern, init_x, init_uncern, dt=0):
        self.dt = dt     
        self.init_x = init_x
        self.init_uncern = init_uncern
        # State transition matrix determines how the state is going to evolve in time (by itself).
        self.A = 1 # In our case we use constant unit matrix because we suppose that the state won't change by itself if not provoked. 
        #self.A = np.matrix([[1, self.dt, 0.5*self.dt**2],
        #                    [0, 1, self.dt],
        #                   [0, 0, 1]])
        
        # Input matrix determines how the input will change the state. 
        # In our case the input is measured charge and it matches the state of charge units so it's also unit matrix. 
        self.B = 1
        #self.B = np.matrix([[(self.dt**2)/2], [self.dt]]) 
        
        # Measurement matrix transforms the measurement (in our case state voltage evaluation of state of charge) to match the state.
        self.C = 1 # In this example the measurement also matches the state. 
        
        # Process uncertainty
        self.R_proc_uncern = init_proc_uncern  
        #self.R = (self.std_acc**2) * np.matrix([[(self.dt**4)/4, (self.dt**3)/2, (self.dt**2)/2],
        #                                      [(self.dt**3)/2, self.dt**2, self.dt],
        #                                     [(self.dt**2)/2, self.dt, 1]])
        
        # Measurement uncertainty
        self.Q_meas_uncern = init_meas_uncern 
        
        # Initial state uncertainty. The uncertainty of the initial guess.
        self.P = init_uncern  
        # Initial state estimation
        self.x = init_x
        # Kalman gain
        self.K_gain = 1
         
    def predict(self, sys_input):
        """ Control update step. """
        # Update the state based on previous state and input:
        self.x = self.A * self.x + self.B * sys_input
        # Calculate error covariance
        # P= A*P*A' + R
        self.P = self.A * self.P * self.A + self.R_proc_uncern
        return self.x
    
    def update(self, z):
        """ Measurement update step """
        # S = H*P*H'+R
        S = self.C*self.P*self.C + self.Q_meas_uncern
        
        # Calculate the Kalman Gain
        # K = P * H'* inv(S)
        self.K_gain = (self.P*self.C) / S
        
        self.x = self.x + self.K_gain*(z - self.C*self.x)
        #I = np.eye(self.C.shape[1])
        self.P = (1 - self.K_gain *self.C)*self.P
        
        return self.x
    
    def reset(self):
        self.P = self.init_uncern  
        # Initial state estimation
        self.x = self.init_x
        # Kalman gain
        self.K_gain = 1