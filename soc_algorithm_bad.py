"""
The initial (dump) algorithm implementation with four Kalman filters. 


This disgrace should eventually be deleted!
Left in the repo just for the comparison. 
"""

from wave import interpolate
from battery_parameters import VBAT_FROM_SOC, SOC_FROM_VBAT, ocv_from_vbat
from kalman_soc import KalmanSoC


sleep_charge = 0
sleep_charge_uncert = 0.001
active_charge_uncert = 0.0001
V1_uncert = 0.95
V2_uncert = 1


voltage2_process_uncert = V2_uncert
voltage1_process_uncert = V1_uncert

Q_meas_soc = V1_uncert
R_proc_vbat = active_charge_uncert

class Algorithm:
    def __init__(self, init_value, init_p):
        self.kalman_filter1 = KalmanSoC(sleep_charge_uncert, V1_uncert, init_value, init_p)
        self.kalman_filter2 = KalmanSoC(active_charge_uncert, V2_uncert, init_value, init_p)
        
        self.voltage1_kalman =  KalmanSoC(voltage1_process_uncert, V1_uncert, interpolate(init_value, VBAT_FROM_SOC), init_p)
        self.voltage2_kalman =  KalmanSoC(voltage2_process_uncert, V2_uncert, interpolate(init_value, VBAT_FROM_SOC), init_p)
            
        self.init_value = init_value
        self.aposteriori1 = init_value
        self.aposteriori2 = init_value
    
    def before_task(self, sleep_charge, sleep_charge_uncert, v1, v1_uncert):
        # Estimated charge measurements during sleep
        #self.kalman_filter.R_proc_uncern = sleep_charge_uncert
        #self.kalman_filter.Q_meas_uncern = soc_from_v1_uncert 
        
        new_soc = self.kalman_filter1.predict(sleep_charge)
        # Voltage measurement before the pulse
        
        # self.kalman_filter1.x ti je svakako vracen sa predictom.
        voc_from_soc = interpolate(new_soc , VBAT_FROM_SOC)
        
        self.voltage1_kalman.predict(voc_from_soc - self.voltage1_kalman.x)
        soc_form_vbat = interpolate(self.voltage1_kalman.update(ocv_from_vbat(v1)), SOC_FROM_VBAT)
        
        self.aposteriori1 = self.kalman_filter1.update(soc_form_vbat)
        
        
        
        #self.kalman_filter_vbat.R_proc_uncern = v1_uncert 
        #self.kalman_filter_vbat.Q_meas_uncern = v1_uncert 
        #self.kalman_filter_vbat.R_proc_uncern = R_proc_vbat
        
        # self.kalman_filter_vbat.predict(voc_from_soc - self.kalman_filter_vbat.x)
        
        
        # soc_form_vbat = interpolate(self.kalman_filter_vbat.update(ocv_from_vbat(v1)), SOC_FROM_VBAT)
        
        # self.aposteriori1 = self.kalman_filter_soc.update(soc_form_vbat)
        
        
    def after_task(self, active_charge, active_charge_uncert, v2, v2_uncert):
        # Estimated charge measurements during active period
        #self.kalman_filter.R_proc_uncern = active_charge_uncert
        #self.kalman_filter.Q_meas_uncern = soc_from_v2_uncert
        new_soc = self.kalman_filter2.predict(active_charge)
        
        voc_from_soc = interpolate(new_soc, VBAT_FROM_SOC)
        self.voltage2_kalman.predict(voc_from_soc - self.voltage2_kalman.x)
        
        # od v2 mi bismo trebali dobiti ocv preko modela. 
        soc_from_vbat = interpolate(self.voltage2_kalman.update(ocv_from_vbat(v2)), SOC_FROM_VBAT)
        
        
        # Voltage measurement before the pulse
        self.aposteriori2 = self.kalman_filter2.update(soc_from_vbat)
        
        self.kalman_filter1.x = self.kalman_filter2.x
        #self.kalman_filter2.x = mean([self.aposteriori1, self.aposteriori2])
        
