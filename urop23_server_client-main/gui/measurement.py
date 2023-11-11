import sys, os
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd()) 
import numpy as np

class Measurement():
    def __init__(self, laser, hmp, spect):
        self.laser = laser
        self.hmp = hmp
        self.spect = spect
            
    def sweep_and_save(self, v_start, v_end, step, pause, channels, zero_between_steps='yes'):
        '''
        Sweep the voltage across parallel-connected channels by dividing 'step' into channel number in 'channels'.
        'Pause' parameter is the time duration for which we wait for the hmp to provide stable voltage after changing voltage. 
        This parameter is currently not used but could be added back if desired by uncommenting the code at lines 64 and 65, 
        and changing some of the previous code about OPC.
        '''
        number_of_channels = len(channels)
        num_of_volts = self.hmp.calc_num_of_volts(float(v_start), float(v_end), float(step))
        v_start_channel = float(v_start)/number_of_channels
        v_end_channel = float(v_end)/number_of_channels
        volts = np.linspace(v_start_channel, v_end_channel, num=num_of_volts)
        
        # zero all the channels before starting a sweep and enable output
        print('Zeroing all the channel voltages...')
        for i in range(1, 5):
            self.hmp.set_voltage(i, 0)
        self.hmp.enable_output()
        print('Output enabled.')

        for volt in volts:
            # self.hmp.disable_output()
            # print('Output disabled.')
            for channel in channels:
                if zero_between_steps == 'yes':
                    print('Setting channel {} to 0 V.'.format(channel))
                    self.hmp.set_voltage(channel, 0)
                    print('Pausing until channel {} set to 0 V...'.format(channel))
                    #print('Pausing for 1 sec...')
                    # time.sleep(1) # time to ensure that the channel is actually set to 0
                    wait = self.hmp.wait()
                    while True:
                        if float(wait) == 1:
                            break
                    print('Setting channel {} to {} V.'.format(channel, volt))
                    volt_step = 1
                    while volt_step < volt:
                        self.hmp.set_voltage(channel, volt_step)
                        wait = self.hmp.wait()
                        while True:
                            if float(wait) == 1:
                                break
                        volt_step += 1
                    self.hmp.set_voltage(channel, volt)
                else:
                    self.hmp.set_voltage(channel, volt)
            print('Pausing until all the previous commands have been executed...')
            wait = self.hmp.wait()
            while True:
                if float(wait) == 1:
                    break
            #print('Pausing for {} secs'.format(pause))
            #time.sleep(float(pause)) # time to ensure that all channels are actually set to correct voltage
            # self.hmp.enable_output()
            # print('Output enabled.')
            self.spect.acquire_and_plot_data(self.spect.fig) # spect.data is set to acquisition data we want to save at this point
            self.spect.save(hmp=True) # we save hmp parameters without a label

        # zero all the channels after a sweep and disable output
        print('Zeroing all the channel voltages...')
        for i in range(1, 5):
            self.hmp.set_voltage(i, 0)
        self.hmp.disable_output()
        print('Output disabled.')

    def __is_connected(device): ### currently not called by any code
        if device == None:
            print("Device not connected.")
    
    def get_all_params(self, laser, spect, hmp):
        hmp_params, laser_params, spect_params = None, None, None
        if hmp:
            hmp_params = self.hmp.get_params()
        if laser:
            laser_params = {'laser_wavelength': self.laser.getwavelength(), 'laser_bandwidth': self.laser.getbandwidth(),
                            'laser_power': self.laser.getpower(), 'OD': self.laser.OD.get()}
        if spect:
            spect_params_query = self.spect.get_parameters()
            spect_params = {'spect_grating': spect_params_query[0], 'spect_wavelength': spect_params_query[1], 
                            'spect_exposure': spect_params_query[2]}
        
        params = {'hmp_params': hmp_params, 'laser_params': laser_params, 'spect_params': spect_params}
        return params
