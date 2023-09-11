# Experimental measurements 

All of the measurements are done on a experimental setup discussed in the master thesis.

The measurements presented here are done in room temperature using the Seiko MS614SE battery. 



Folder `battery_model` contains battery voltage and current waveform from discharge pulses. These measurements are in .jls format and can be used for determining the battery internal parameters using curve fitting. 

Folder `validation` contains measurements of discharge validation which consist of charging and discharging the battery with pulses of random current intensity but constant charge. There are two type of data:

1.  Continual measurements form Joulescope which acts an integrator and serves for establishing the baseline
2. Information about pulses current intensity and duration. Also there are two voltage measurements before and after the pulse.

The continual measurements form the Joulescope act as a baseline while the measurements form the power supply (pulse generator) are feed in to the proposed algorithm to compare against the baseline.  



- [ ] Document this better!