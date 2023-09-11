from wave import interpolate
from battery_parameters import VBAT_FROM_SOC, SOC_FROM_VBAT, ocv_from_vbat
from kalman_soc import KalmanSoC


class Algorithm:
    def __init__(self, init_value, init_p, sleep_charge_uncert = 0.001, active_charge_uncert = 0.0001, V1_uncert = 0.95, V2_uncert = 1, voltage_proc=0.0001):
        self.sleep_charge_uncert = sleep_charge_uncert
        self.active_charge_uncert = active_charge_uncert
        self.V1_uncert = V1_uncert
        self.V2_uncert = V2_uncert
        self.voltage_proces_uncer = voltage_proc
        # Kalman filters: 
        self.kalman_filter_soc = KalmanSoC(max(self.sleep_charge_uncert, self.active_charge_uncert), max(self.V1_uncert, self.V2_uncert), init_value, init_p)
        self.kalman_filter_vbat = KalmanSoC(self.voltage_proces_uncer, max(self.V1_uncert, self.V2_uncert), interpolate(init_value, VBAT_FROM_SOC), init_p)
        
        self.init_value = init_value
        self.aposteriori1 = init_value
        self.aposteriori2 = init_value
        
    def before_task(self, sleep_charge, sleep_charge_uncert, v1, v1_uncert):
        # Estimated charge measurements during sleep 
        self.kalman_filter_soc.R_proc_uncern = sleep_charge_uncert
        self.kalman_filter_soc.Q_meas_uncern = v1_uncert
        self.kalman_filter_vbat.Q_meas_uncern = v1_uncert 
        self.kalman_filter_vbat.R_proc_uncern = self.voltage_proces_uncer
        
        # Estimation based on the sleep_charge measurement, CONTROL UPDATE step. 
        new_soc = self.kalman_filter_soc.predict(sleep_charge)
        # Expected Voc from the soc
        voc_from_soc = interpolate(new_soc , VBAT_FROM_SOC)
        # Integration of the Voc value in the voltage Kalman filter in the CONTROL UPDATE step. 
        self.kalman_filter_vbat.predict(voc_from_soc - self.kalman_filter_vbat.x)
        # Return the newly obtained SoC based on the values from the Voc kalman filter and new voltage measurements. 
        soc_form_vbat = interpolate(self.kalman_filter_vbat.update(ocv_from_vbat(v1)), SOC_FROM_VBAT)
        # Integrate the new SoC in the SoC Kalman filter in the MEASUREMENT UPDATE step. 
        self.aposteriori1 = self.kalman_filter_soc.update(soc_form_vbat)
        
        
        
    def after_task(self, active_charge, active_charge_uncert, v2, v2_uncert):
        # Estimated charge measurements during active period
        self.kalman_filter_soc.R_proc_uncern = active_charge_uncert
        self.kalman_filter_soc.Q_meas_uncern = v2_uncert
        self.kalman_filter_vbat.Q_meas_uncern = v2_uncert
        self.kalman_filter_vbat.R_proc_uncern = self.voltage_proces_uncer 
        
        # Estimation based on the active_charge measurement, CONTROL UPDATE step of the SoC Kalman filter. 
        new_soc = self.kalman_filter_soc.predict(active_charge)
        # Expected Voc from the current SoC. 
        voc_from_soc = interpolate(new_soc, VBAT_FROM_SOC)
        # Integrate the Voc value in the Kalman filter in the CONTROL UPDATE step.
        self.kalman_filter_vbat.predict(voc_from_soc - self.kalman_filter_vbat.x)
        
        # Get the SoC value from the integration of the V2 measurement in the voltage Kalman filter. 
        # The ocv_from_bat is obtained from the battery model, and pulse parameters. 
        soc_from_vbat = interpolate(self.kalman_filter_vbat.update(ocv_from_vbat(v2)), SOC_FROM_VBAT)
        
        # Integration of the estimated SoC value in the SoC Kalman filter and saving the final value. 
        self.aposteriori2 = self.kalman_filter_soc.update(soc_from_vbat)

