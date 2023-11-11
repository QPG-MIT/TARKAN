# coding: utf-8
"""
m30xy.py
========
THIS EXAMPLE CURRENTLY DOESN'T FUNCTION CORRECTLY:
It can read the moves correctly,

An example showing the usage of a Thorlabs M30XY stage.

The stage is based off of Brushed DC motors, and so uses the BDC101 C API
controls. This example will import these functions using ctypes, connect
to the device, and then make moves.2
"""
import os
import time
from ctypes import *  # This is generally bad practice, but done here for brevity
from ctypes import CDLL
# import pyperclip

class StageXY:
    def __init__(self, serial_number, measurement, optimization):
        self.measurement = measurement
        self.optimization = optimization

        self.serial_number = serial_number
        os.add_dll_directory(r"C:\\Program Files\\Thorlabs\\Kinesis")
        self.lib : CDLL = cdll.LoadLibrary("Thorlabs.MotionControl.Benchtop.DCServo.dll")

        # Initial position to be defined
        #self.x_init, self.y_init = self.get_position()

        # Displacement speed for X and Y to be defined
        self.x_step = 10000
        self.y_step = 10000
        self._step = 10000
        self.x_small_step = 25
        self.y_small_step = 25
        self.MIN_STEP_SIZE = 25
        self.x_init, self.y_init = 0, 0

        # Position
        self.X = self.x_init
        self.Y = self.y_init

        #self.get_velocity(1)

    # Used to connect and instantiate the device 
    def build_device(self):
        if self.lib.TLI_BuildDeviceList() == 0:
            # Make the connection
            ret = self.lib.BDC_Open(self.serial_number)
            print(f'BDC_Open Returned {ret}')
            # Start polling at a 200ms interval
            self.lib.BDC_StartPolling(self.serial_number, 1, c_int(200))
            self.lib.BDC_StartPolling(self.serial_number, 2, c_int(200))
            # Enable channels to move
            self.lib.BDC_EnableChannel(self.serial_number, 1) 
            self.lib.BDC_EnableChannel(self.serial_number, 2)
            # Home the device on channels 1 and 2
            self.lib.BDC_Home(self.serial_number, 1)
            time.sleep(40)
            self.lib.BDC_Home(self.serial_number, 2)
            time.sleep(45)
            self.get_position()

    # Close the connection of the device
    def close_device(self):
        self.lib.BDC_Close(self.serial_number)
        print("Device turned off")

    # Move to the right by X
    def move_r(self):
        self.X = self.X + self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 1, self.X)
        time.sleep(0.5)  # 250ms wait time to ensure values are sent to device
        self.lib.BDC_MoveAbsolute(self.serial_number, 1)
        time.sleep(1)
        self.get_position()

    # Move to the left by X
    def move_l(self):
        self.X = self.X - self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 1, self.X)
        time.sleep(0.5)
        self.lib.BDC_MoveAbsolute(self.serial_number, 1)
        time.sleep(1)
        self.get_position()

    # Move to the top by Y
    def move_t(self):
        self.Y = self.Y + self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 2, self.Y)
        time.sleep(0.5)  # 250ms wait time to ensure values are sent to device
        self.lib.BDC_MoveAbsolute(self.serial_number, 2)
        time.sleep(1)
        self.get_position()

    # Move to the bottom by Y
    def move_b(self):
        self.Y = self.Y - self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 2,self.Y)
        time.sleep(0.5)
        self.lib.BDC_MoveAbsolute(self.serial_number, 2)
        time.sleep(1)
        self.get_position()

    # Move on the X direction by step
    def move_step_x(self, step):
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 1, step)
        time.sleep(1)

        self.lib.BDC_MoveAbsolute(self.serial_number, 1)
        time.sleep(1)

    # Move on the Y direction by step
    def move_step_y(self, step):
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 2, step)
        time.sleep(1)

        self.lib.BDC_MoveAbsolute(self.serial_number, 2)
        time.sleep(1)

    # Print position of the device
    def get_position(self):

        # Print the New Positions:
        self.lib.BDC_RequestPosition(self.serial_number, 1)
        self.lib.BDC_RequestPosition(self.serial_number, 2)
        time.sleep(0.2)

        x_pos_dev = self.lib.BDC_GetPosition(self.serial_number, 1)
        y_pos_dev = self.lib.BDC_GetPosition(self.serial_number, 2)
        print(f'(X,Y) : {x_pos_dev}, {y_pos_dev}')

        return [x_pos_dev,y_pos_dev]
    
    def update_step(self, new_step):
        self._step = new_step
        print("The step is {}".format(self._step))

    # def get_status(self):
    #     return self.status

    # def set_status(self, new_status):
    #     self.status = new_status

    def update_reference(self):
        self.x_init = self.X
        self.y_init = self.Y
        self.reference_text["text"] = f"Référence : ({self.x_init}, {self.y_init})"

    def set_position(self, stage_x, stage_y):
        self.X = self.x_init + stage_x
        self.move_step_x(self.X)
        self.Y = self.y_init + stage_y
        self.move_step_y(self.Y)
        self.get_position()

    def move_sequence(self, sequence, relative=True):
        '''
        Move to the specified devices in the sequence and make optimization, then acquire data and save.
        If 'relative' is True, the coordinates in the 'sequence' are treated as relative coordinates to the
        current location of the device. If False, they are absolute coordinates with respect to the reference
        of the stages, which is the (0, 0) point the stage stops at after initialization. 
        '''
        positions = sequence.get().split(";")
        processed_pos = []
        # First, we try to process all the positions before taking any data to ensure they
        # are all in the correct format.
        if relative:
            reference = self.get_position()
            x_reference, y_reference = reference[0], reference[1]
        else:
            x_reference, y_reference = 0, 0
        for pos in positions:
            try:
                label, x, y = pos.split(",")
                x = int(x) + x_reference
                y = int(y) + y_reference
                processed_pos.append((label, x, y))
            except ValueError:
                print("Error: Incorrect format for the label and/or coordinates.")
        for (label, x, y) in processed_pos:
            label = label.strip()
            self.set_position(x, y)
            self.optimization.optimize_single_device() # optimize location
            # time.sleep(3)  # Add a short delay to see each position/optimization
            fig = self.measurement.spect.fig
            # make a single acquisition and save
            self.measurement.spect.acquire_and_plot_data(fig) 
            self.measurement.spect.save(hmp=False, label=label)
            self.get_position()

    # Should give the velocity while moving but IDK
    def get_velocity(self, channel):
        acceleration = c_int()
        velocity = c_int()
        self.lib.BDC_RequestVelParams(self.serial_number,channel)
        time.sleep(0.2)
        self.lib.BDC_GetVelParams(self.serial_number, channel, byref(acceleration), byref(velocity))
        print("The velocity of the stage : {}".format(velocity.value))

    def generate_device_sequence(self, start_label, start_x, start_y, num_devices_per_col, x_increment, y_increment):
        '''
        Generate device list in the form of label_1, x_1, y_1; label_2, x_2, y_2;... where x and y are absolute positions.
        Generates first the devices in the given start column, then moves to the next column.
        Columns are ordered from left to right, starting from 1.
        'start_label' is a list of numbers, where entry at index i corresponds to the start label of device at column i+1.
        'num_devices_per_column' is a list of numbers, where entry at index i corresponds to number of devices at column i+1. 
        '''
        num_cols = len(num_devices_per_col)
        device_list = []
        for col in range(num_cols):
            first_label = start_label[col]
            x_coord = start_x + col*x_increment
            num_devices_this_col = num_devices_per_col[col]
            for row in range(num_devices_this_col):
                label = first_label + row
                y_coord = start_y + row*y_increment
                device_list.append(f"{label},{x_coord},{y_coord}")

        result = ';'.join(device_list)
        # pyperclip.copy(result)
        return result
    
    def gen_mes_seq(self):
        '''
        Process the inputs from the entry widget into the appropriate data types and feed into sequence generation & measurement.
        num_devoces_per_
        '''
        start_label = self.optimization.start_label.get().split(',')
        try:
            start_label = [int(num.strip()) for num in start_label] # extract the numeric labels
        except Exception as err:
            print('Check your labels and ensure that they are all numbers separated by commas!')
            raise err
        try: 
            start_x = int(self.optimization.start_x.get())
            start_y = int(self.optimization.start_y.get())
        except Exception as err:
            print('Check your starting x and y and ensure that they are both one numerical value!')
            raise err
        try:
            x_increment = int(self.optimization.x_increment.get())
            y_increment = int(self.optimization.y_increment.get())
        except Exception as err:
            print('Check your x and y increments and ensure that they are both one numerical value!')
            raise err
        try: 
            num_devices_per_col = self.optimization.num_devices_per_col.get().split(',')
            num_devices_per_col = [int(num.strip()) for num in num_devices_per_col]
        except Exception as err:
            print('Check your number of devices per column and ensure they are all numbers separated by commas!')
            raise err
        sequence = self.generate_device_sequence(start_label, start_x, start_y, num_devices_per_col, x_increment, y_increment)
        print('This is the obtained sequence: ', sequence)
        self.move_sequence(sequence, self.optimization.rel_coord.get())
        
#if __name__ == '__main__':
 #   stage = StageXY(1, 1, 1, 1)
  #  print(stage.generate_device_sequence([20, 4], 10, 20, [5, 4], 5, 20))

