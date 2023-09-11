'''
Simple 1D implementation of Kalman filter used for combining the voltage based state of charge estimation and charge.

TODO: add the ability to modify the variances during the execution. 
'''

import numpy as np

class KalmanSoC():
    def __init__(self, init_proc_uncern, init_meas_uncern, init_x, init_uncern, dt=0):
        self.dt = dt
        n = len(init_x)
        self.init_x = np.matrix(init_x).reshape(n, 1)
        self.init_uncern = np.matrix(init_uncern)
        # State transition matrix determines how the state is going to evolve in time (by itself).
        # In our case we use constant unit matrix because we suppose that the state won't change by itself if not provoked.
        self.A = np.matrix(np.eye(n)) 
        
        # Input matrix determines how the input will change the state. 
        # In our case the input is measured charge and it matches the state of charge units so it's also unit matrix. 
        self.B = np.matrix(np.eye(n))
        
        # Measurement matrix transforms the measurement (in our case state voltage evaluation of state of charge) to match the state.
        # In this example the measurement also matches the state.
        self.C = np.matrix(np.eye(n))  
        
        # Process uncertainty
        self.R_proc_uncern = np.matrix(init_proc_uncern)  
        
        # Measurement uncertainty
        self.Q_meas_uncern = np.matrix(init_meas_uncern)
        
        # Initial state uncertainty. The uncertainty of the initial guess.
        self.P = self.init_uncern  
        # Initial state estimation
        self.x = self.init_x
        # Kalman gain
        self.K_gain = np.matrix(np.eye(n))
         
    def predict(self, sys_input):
        """ Control update step. """
        sys_input = np.matrix(sys_input).reshape(len(sys_input), 1)
        # Update the state based on previous state and input:
        self.x = np.dot(self.A, self.x)  + np.dot(self.B, sys_input)
        # Calculate error covariance
        # P= A*P*A' + R
        self.P = np.dot(np.dot(self.A, self.P), self.A.T) + self.R_proc_uncern
        return self.x
    
    def update(self, z):
        """ Measurement update step """
        # S = C*P*C'+Q
        S = np.dot(np.dot(self.C, self.P), self.C.T) + self.Q_meas_uncern
        
        # Calculate the Kalman Gain
        # K = P * C' * inv(S)
        self.K_gain = np.dot(np.dot(self.P, self.C.T), np.linalg.inv(S))
        
        # Integrate the measurement into the a posterior state x:
        self.x = self.x + self.K_gain*(z - self.C*self.x)
        
        # Update the covariance matrix:
        I = np.eye(self.C.shape[1])
        self.P = (I - self.K_gain *self.C)*self.P
        
        return self.x
    
    def reset(self):
        ''' Resetting the internal parameters '''
        self.P = self.init_uncern  
        # Initial state estimation
        self.x = self.init_x
        # Kalman gain
        self.K_gain = np.matrix(np.eye(n))