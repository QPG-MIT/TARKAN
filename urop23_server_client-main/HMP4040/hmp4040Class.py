import pyvisa as visa
import numpy as np
import time

class HMP4040():
    def __init__(self, address):
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(address) 
        #self.set_voltage(1, 1)      
        self.instr.timeout = 5000
        #self.instr.read_termination = '\n'
        #self.instr.write_termination = '\n'
        self.name = self.instr.query('*IDN?')

        print('Connected to HMP4040.')
        if self.is_output_enabled():
            print('Power supply output is on.')
        else:
            print('Power supply output is off.')
        for ch in [1, 2, 3, 4]:
            vval = self.get_voltage(ch)
            ival = self.get_current_limit(ch)
            if self.get_output_state(ch):
                print('Channel %s: %s V set, %s A limit, output ENABLED' % (ch, float(vval), float(ival)))
            else:
                print('Channel %s: %s V set, %s A limit, output DISABLED' % (ch, float(vval), float(ival)))
        self.help()

    def help(self):
        print('''Here are the available functions to call: \n
                 set_voltage(channel, voltage), \n
                 get_voltage(channel), \n
                 set_current_limit(channel, current), \n
                 get_current_limit(channel), \n
                 set_output_state(channel, state), \n
                 get_output_state(channel), \n
                 enable_output(), \n
                 disable_output(), \n
                 is_output_enabled(), \n
                 get_meas_voltage(channel), \n
                 get_meas_current(channel)''')

    def reset(self):
        # reset the instrument
        self.instr.write('*RST')
        
    def __select_channel(self, ch):
        retries = 5
        while retries > 0:   
            self.instr.write('INST OUT%s' % ch)
            inst_select = self.instr.query('INST?')
            if inst_select != 'OUTP%s\n' %ch:
                retries -= 1
            else:
                return
        print('The selected instrument, {}, is not the correct instrument!'.format(inst_select))
        raise

    def set_voltage(self, ch, voltage):
        ''' 
        Set the voltage at the given channel to the given value. 'Voltage' can be float or string.
        '''
        self.__select_channel(ch)
        retries = 5
        while retries > 0:
            self.instr.write('VOLT %s' % voltage)
            volts = self.instr.query('VOLT?')
            if float(volts) == round(float(voltage), 3):
                return
            else:
                retries -= 1
        print('The voltage at channel {} is not {} V, but {} V.'.format(ch, voltage, volts))
    
    def get_voltage(self, ch):
        self.__select_channel(ch)
        return float(self.instr.query('VOLT?'))

    def set_current_limit(self, ch, current):
        ''' 
        Set the current limit at the given channel to the given value. 'Current' can be float or string.
        '''
        self.__select_channel(ch)
        retries = 5
        while retries > 0:
            self.instr.write('CURR %s' % current)
            curr = self.instr.query('CURR?')
            if float(curr) == round(float(current), 3):
                return
            else:
                retries -= 1
        print('The current limit at channel {} is not {} A, but {} A.'.format(ch, current, curr))
    
    def get_current_limit(self, ch):
        self.__select_channel(ch)
        return float(self.instr.query('CURR?'))
    
    def set_output_state(self, ch, state):
        self.__select_channel(ch)
        if state:
            self.instr.write('OUTP:SEL 1')
        else:
            self.instr.write('OUTP:SEL 0')
    
    def get_output_state(self, ch):
        self.__select_channel(ch)
        return bool(float(self.instr.query('OUTP:SEL?')))
    
    def enable_output(self):
        self.instr.write('OUTP:GEN 1')

    def disable_output(self):
        self.instr.write('OUTP:GEN 0')
    
    def is_output_enabled(self):
        return bool(float(self.instr.query('OUTP:GEN?')))

    def get_meas_voltage(self, ch):
        self.__select_channel(ch)
        return float(self.instr.query('MEAS:VOLT?'))

    def get_meas_current(self, ch):
        self.__select_channel(ch)
        return float(self.instr.query('MEAS:CURR?'))
    
    def calc_num_of_volts(self, v_start, v_end, step):
        volt_diff = v_end-v_start+0.001
        if volt_diff >= 0:
            #print('hallulujah', volt_diff, (volt_diff+0.001)//step, volt_diff//step+1, int(volt_diff//step+1))
            #print(step)
            #print(volt_diff/step)
            return int((volt_diff//step)+1)
        else:
            return int(abs((volt_diff//step))+1)
    
    def sweep_single_channel(self, v_start, v_end, step, pause, channel, zero_between_steps):
        '''Sweep the voltage values from v_start to v_end by taking steps of size 'step'.
        'Pause' is the pause time between consecutive steps, channel is the channel at which
        the sweep occurs, and zero_between_steps is a boolean indicating whether the voltage
        will be zero'ed first when taking a step. 
        '''
        num_of_volts = self.__calc_num_of_volts(v_start, v_end, step)
        volts = np.linspace(v_start, v_end, num=num_of_volts)
        for volt in volts:
            if zero_between_steps:
                self.set_voltage(channel, 0)
                time.sleep(0.1) # time to ensure that the channel is actually set to 0
                self.set_voltage(channel, volt)
            else:
                self.set_voltage(channel, volt)
            time.sleep(pause)
    
    def get_params(self):
        '''
        Get all the current parameters of the HMP. 
        '''
        ch1_voltage = self.get_voltage(1)
        ch2_voltage = self.get_voltage(2)
        ch3_voltage = self.get_voltage(3)
        ch4_voltage = self.get_voltage(4)
        ch1_state = self.get_output_state(1)
        ch2_state = self.get_output_state(2)
        ch3_state = self.get_output_state(3)
        ch4_state = self.get_output_state(4)
        output_enabled = self.is_output_enabled()
        ch1_cur_limit = self.get_current_limit(1)
        ch2_cur_limit = self.get_current_limit(2)
        ch3_cur_limit = self.get_current_limit(3)
        ch4_cur_limit = self.get_current_limit(4)

        voltages = [ch1_voltage, ch2_voltage, ch3_voltage, ch4_voltage]
        states = [ch1_state, ch2_state, ch3_state, ch4_state]
        tot_voltage = 0
        for i in range(len(states)):
            if states[i]:
                tot_voltage += voltages[i]

        params = {'ch1_voltage': ch1_voltage, 'ch2_voltage': ch2_voltage, 'ch3_voltage': ch3_voltage, 'ch4_voltage': ch4_voltage,
                  'ch1_state': ch1_state, 'ch2_state': ch2_state, 'ch3_state': ch3_state, 'ch4_state': ch4_state, 'output_enabled': output_enabled,
                  'tot_voltage': tot_voltage, 'ch1_cur_limit': ch1_cur_limit, 'ch2_cur_limit': ch2_cur_limit, 'ch3_cur_limit': ch3_cur_limit, 
                  'ch4_cur_limit': ch4_cur_limit}
        return params

    def wait(self):
        '''
        Wait until all the previous commands have been exevuted.
        '''
        return self.instr.query('*OPC?')
        
#if __name__ == '__main__':
 #   h = HMP4040(address='ASRL4::INSTR')    