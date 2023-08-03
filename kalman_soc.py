import numpy as np

class KalmanMatrix():
    def __init__(self, dt, std_acc, std_meas):
        self.dt = dt
        #self.u = u
        self.std_acc = std_acc
        #self.A = np.matrix([[1, self.dt, 0.5*self.dt**2],
        #                    [0, 1, self.dt],
        #                   [0, 0, 1]])
        
        self.A = 1
        
        #self.B = np.matrix([[(self.dt**2)/2], [self.dt]]) 
        self.B = 1
        #self.H = np.matrix([[1,0,0]])
        self.C = 1 #Pomaze mapiranju Stanja sa mjerenjem 
        
        #self.R = (self.std_acc**2) * np.matrix([[(self.dt**4)/4, (self.dt**3)/2, (self.dt**2)/2],
        #                                      [(self.dt**3)/2, self.dt**2, self.dt],
        #                                     [(self.dt**2)/2, self.dt, 1]])
        
        self.R = self.std_acc # Nesigurnost procesa 
        
        self.Q = std_meas # Nesigurnost mjerenja
        
        self.P = self.std_acc #Vjerodostojnost inicijalne pretpostavke. Može biti drugačija
        
        self.x = 0
        
        
    def predict(self, sys_input):
        # Ref :Eq.(9) and Eq.(10)
        # Update time state
        self.x = self.A *self.x + self.B*sys_input
        # Calculate error covariance
        # P= A*P*A' + R
        self.P = self.A *self.P* self.A + self.R
        return self.x
    
    def update(self, z):
        # Ref :Eq.(11) , Eq.(11) and Eq.(13)
        # S = H*P*H'+R
        S = self.C*self.P*self.C + self.Q
        # Calculate the Kalman Gain
        # K = P * H'* inv(H*P*H'+R)
        K = (self.P*self.C) / S  # Eq.(11)
        self.x = self.x + K*(z - self.C*self.x)  # Eq.(12)
        #I = np.eye(self.C.shape[1])
        self.P = (1 - K *self.C)*self.P  # Eq.(13)