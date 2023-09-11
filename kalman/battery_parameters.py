from wave import interpolate


# SOC_FROM_VBAT = [
# (1.8,	0),
# (2.1,	0.032122768),
# (2.211724138,	0.050963561),
# (2.495862069,	0.194666178),
# (2.58,	0.261),
# (2.622758621,	0.378),
# (2.798275862,	0.724710198),
# (2.832413793,	0.85),
# (3,	1)
# ]



# #SoC(Voc_bat) obtained from nominal discharge curve
# SOC_FROM_VBAT = [(1.7, 0),
#                  (2, 0.1),
#                  (2.2, 0.13),
#                  (2.3, 0.165),
#                  (2.4, 0.276 + 0.1),
#                  (2.6, 0.8),
#                  (2.7, 0.929134),
#                  (2.8, 0.976378),
#                  (3, 1),
# ]

# SOC_FROM_VBAT = [
#         (1.8, 0),
#         (2.0986206896551725, 0.0001 + 0.03),
#         (2.1, 0.0021227684030324934 + 0.03),
#         (2.2117241379310344, 0.020963560772805145 + 0.03),
#         (2.437931034,	0.100000000 + 0.03),
#         (2.495862069,	0.144666178),
#         (2.559310345,	0.210139398),
#         (2.622758621,	0.328804109),
#         (2.719310345,	0.556806065),
#         (2.788275862,	0.724710198),
#         (2.832413793,	0.821462460),
#         (3        ,   1)
# ]

# SOC_FROM_VBAT = [
#     (1.8,	0),
#     (2.09862069,	0.0301),
#     (2.1,	0.032122768),
#     (2.211724138,	0.050963561),
#     (2.495862069,	0.144666178),
#     (2.58,	0.210139398),
#     (2.622758621,	0.328804109),
#     (2.788275862,	0.724710198),
#     (2.832413793,	0.82146246),
#     (3,	1)
# ]


SOC_FROM_VBAT = [
    (1.8,	0),
    (2.1,	0.032122768),
    (2.211724138,	0.050963561),
    (2.495862069,	0.194666178),
    (2.58,	0.261),
    (2.622758621,	0.378),
    (2.798275862,	0.724710198),
    (2.832413793,	0.85),
    (3,	1)
]

VBAT_FROM_SOC = [(val[1], val[0]) for val in SOC_FROM_VBAT]

NOMINAL_CURRENT = 100e-6
P_CONF = 1.15
COLUMBIC_EFF = 0.7
BATTERY_CAPACITY = 12 #Coulomb hours

def soc_from_vbat_rising(v_bat):
    #Based on the ECM model this should return the SOC based on the voltage measurement BEFORE the task
    return interpolate(v_bat+0.25, SOC_FROM_VBAT)#TODO: add SoC estimate from the Voc obtained from the ECM model
    
    
def soc_from_vbat_falling(v_bat):
    #Based on the ECM model this should return the SOC based on the voltage measurement AFTER the task
    return interpolate(v_bat+0.25, SOC_FROM_VBAT) #TODO: add SoC estimate from the Voc obtained from the ECM model

def ocv_from_vbat(vbat):
    return vbat + 0.25

def get_effective_charge(current, duration, coefs):
    # Effective charge is ony employed when we're discharging the battery. 
    if current < 0:
        current = abs(current)
        return -1*(current*(current/NOMINAL_CURRENT)**(P_CONF-1))*duration
    return current*duration*COLUMBIC_EFF

