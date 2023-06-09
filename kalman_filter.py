'''
This module enables 

'''

class Kalman(object):

    def __init__(self, initial_x, initial_x1, initial_p, initial_p1, initial_q, initial_r):
        self.current_variance_x = initial_p
        self.previous_variance_x  = initial_p

        self.current_variance_x1 = initial_p1
        self.previous_variance_x1 = initial_p1
        
        self.current_estimate_x = initial_x
        self.previous_estimate_x = initial_x

        self.current_estimate_x1 = initial_x1
        self.previous_estimate_x1 = initial_x1

        self.process_noise = initial_q
        self.measurement_noise = initial_r


    def update(self, measured_value):
        '''
        Used to update the estimate based on the new measured data
        '''
        self.Kn = self.previous_variance_x/(self.previous_variance_x + self.measurement_noise) 
        self.current_estimate_x = self.previous_estimate_x + self.Kn*(measured_value - self.previous_estimate_x)
        self.current_variance_x = (1 - self.Kn)*self.previous_variance_x
        
        return self.current_estimate_x

    def predict(self, time_step):
        '''
        Used to make predictions on future future states based on the dynamic model of the system
        '''
        # State extrapolation
        self.previous_estimate_x = self.current_estimate_x + time_step*self.current_estimate_x1
        self.previous_estimate_x1 = self.current_estimate_x1

        # Variance extrapolation
        self.previous_variance_x = self.current_variance_x + self.current_variance_x1*time_step**2
        self.previous_variance_x1 = self.current_variance_x1 + self.process_noise