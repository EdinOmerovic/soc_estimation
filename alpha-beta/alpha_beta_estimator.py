ALPHA = 1
BETA = 1
INITIAL_SOC = 1

def SoCvOCV_curve(open_circuit_voltage):
    SoC = 0
    return SoC



def getValues():
    pass


def SoC_from_V1(v1, t_sleep):
    SoCvOCV_curve(OCV_est(v1, t_sleep))

#Na osnovu prethodne vrijednosti napona V2_{n-1}, dužine sna (i osvijetljenosti)
# predvidi koji je to open circuit napon baterije. 
def OCV_est(v1, t_sleep, lux_value):
    #Pretpostavljamo da se uređaj nije praznio dok je spavao. 
    #Pretpostavljamo da se uređaj mogao samo puniti.
    #Količina ulaznog naboja je funkcija vremena provedenog u san i estimirane vrijednosti prosječne osvijetljenosti unutar nekog vremenskog intervala



if __name__ == "__main__":
    T_sleep, V1, Q_act, V2, Lux_values = getValues()

    SoC_prev = INITIAL_SOC
    while True: 
        # Step 1: Input - measured values

        # Step 2: Update
        # Estimate the current state using the State Update equation
        # State extrapolation Equation
        SOC_est = SOC_est_prev + t_sleep*I_sleep

        # Pretpostavljamo da je jedna vrijednost konstantna. Ta vrijednost je izvod vrijednosti koje estimiramo.
        # U primjeru sa interneta ta vrijednost je brzina, u našem primjeru ta vrijednost bi trebala biti struja spavanja.

        # State update equation
        SOC = SOC_prev_actual + ALPHA*(SOC_est - SOC_prev_actual) 

        # Output: koristiš ovu vrijednost

        # Step 3: Predict
        # Koristi jednačine dinamičkog modela
        # State update equation
        SOC_future =  
