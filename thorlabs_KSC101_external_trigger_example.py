import numpy as np
import thorlabs_KSC101
import ni_PCIe_6738

'''Test the shutter's ability to follow external triggers'''
ao = ni_PCIe_6738.DAQ(num_channels=1, rate=1e6, verbose=False)
shutter = thorlabs_KSC101.Controller(
    'COM18', mode='trigger', verbose=True, very_verbose=False)

triggers = 5
transit_time_ms  = 10 # how much time to open/close the shutter? 10ms?
exposure_time_ms = 10 # how much time to be fully open? 10ms?

transit_px  = max(ao.s2p(1e-3 * transit_time_ms), 1)
exposure_px = max(ao.s2p(1e-3 * exposure_time_ms), 1)
period_px = 2*transit_px + exposure_px # open/close + expose

voltage_series = []
for i in range(triggers):
    volt_period = np.zeros((period_px, ao.num_channels), 'float64')
    # -> set external trigger 'active high' or 'active low' using the GUI
    # -> the default is 'active high'
    volt_period[transit_px + exposure_px:, 0] = 5 # rising edge starts 'open'
    voltage_series.append(volt_period)
voltages = np.concatenate(voltage_series, axis=0)

shutter.set_state('open', block=False)
# can the shutter keep up?
for i in range(2):
    ao.play_voltages(voltages, block=True) # race condition!

time_s = ao.p2s(voltages.shape[0])
tps = triggers /  time_s
print('\n -> Tiggers per second = %02f'%tps) # (forced by ao play)

shutter.close()
ao.close()
