'''
This module enables 

'''

class Kalman(object):

    def __init__(self, initial_x, initial_x1, initial_p, initial_p1, initial_q, initial_r):
        #States
        self.current_estimate_x1 = initial_x
        self.previous_estimate_x1 = initial_x

        self.current_estimate_x2 = initial_x1
        self.previous_estimate_x2 = initial_x1
        

        #Variances
        self.current_variance_x1 = initial_p
        self.previous_variance_x2  = initial_p

        self.current_variance_x1 = initial_p1
        self.previous_variance_x2 = initial_p1
        

        self.process_noise = initial_q
        self.measurement_noise = initial_r


    def update(self, measured_value):
        '''
        Used to update the estimate based on the new measured data
        '''
        self.Kn = self.previous_variance_x2/(self.previous_variance_x2 + self.measurement_noise) 
        self.current_estimate_x1 = self.previous_estimate_x1 + self.Kn*(measured_value - self.previous_estimate_x1)
        self.current_variance_x1 = (1 - self.Kn)*self.previous_variance_x2
        
        return self.current_estimate_x1

    def predict(self, time_step):
        '''
        Used to make predictions on future future states based on the dynamic model of the system
        '''
        # State extrapolation
        self.previous_estimate_x1 = self.current_estimate_x1 + time_step*self.current_estimate_x2
        self.previous_estimate_x2 = self.current_estimate_x2

        # Variance extrapolation
        self.previous_variance_x2 = self.current_variance_x1 + self.current_variance_x1*time_step**2
        self.previous_variance_x2 = self.current_variance_x1 + self.process_noise