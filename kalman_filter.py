'''
This module enables 

'''

class Kalman(object):

    def __init__(self, initial_x, initial_x1, initial_p, initial_p1, initial_q, initial_r):
        # Noise
        self.process_noise = initial_q
        self.measurement_noise = initial_r
        
        #States
        # First state variable: position
        self.current_estimate_x1 = initial_x
        self.previous_estimate_x1 = initial_x
        # Second state variable: velocity
        self.current_estimate_x2 = initial_x1
        self.previous_estimate_x2 = initial_x1
        # Third state variable: acceleration
        self.current_estimate_x3 = initial_x1
        self.previous_estimate_x3 = initial_x1

        #Variances
        # First state variance: position variance
        self.current_variance_x1 = initial_p
        self.previous_variance_x1  = initial_p
        # Second state variance: velocity variance
        self.current_variance_x2 = initial_p1
        self.previous_variance_x2 = initial_p1

        self.current_variance_x3 = initial_p1
        self.previous_variance_x3 = initial_p1


    '''
    Used to update the estimate based on the new measured data
    '''
    def update(self, measured_value, time_step):
        self.Kn1 = self.previous_variance_x1/(self.previous_variance_x1 + self.measurement_noise) 
        self.Kn2 = self.previous_variance_x2/(self.previous_variance_x2 + self.measurement_noise) 
        self.Kn3 = self.previous_variance_x3/(self.previous_variance_x3 + self.measurement_noise) 
        
        # State update
        self.current_estimate_x1 = self.previous_estimate_x1 + self.Kn3*(measured_value - self.previous_estimate_x1)
        self.current_estimate_x2 = self.previous_estimate_x2 + self.Kn2*(measured_value - self.previous_estimate_x2)
        
        # Variance update
        self.current_variance_x1 = (1 - self.Kn1)*self.previous_variance_x1
        self.current_variance_x2 = (1 - self.Kn2)*self.previous_variance_x2
        self.current_variance_x3 = (1 - self.Kn3)*self.previous_variance_x3
        
        #Make it return all Kalman filter parameters, not just current estimate. 
        return self

    '''
    Used to make predictions on future future states based on the dynamic model of the system
    '''
    def predict(self, time_step):

        # Variance extrapolation
        self.previous_variance_x3 = self.current_variance_x3 + self.process_noise
        self.previous_variance_x2 = self.current_variance_x2 + self.previous_variance_x3*time_step**2 
        self.previous_variance_x1 = self.current_variance_x1 + self.current_variance_x2*time_step**2 + self.previous_variance_x2*(0.5*time_step)**4

        # State extrapolation
        self.previous_estimate_x3 = self.current_estimate_x3
        self.previous_estimate_x2 = self.current_estimate_x2 + time_step*self.previous_estimate_x3 
        self.previous_estimate_x1 = self.current_estimate_x1 + time_step*self.previous_estimate_x2 + 0.5*self.previous_estimate_x3*time_step**2

        
        return self