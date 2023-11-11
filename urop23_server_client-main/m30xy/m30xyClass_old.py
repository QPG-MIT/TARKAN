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
import tkinter as tk
import os

class m30XY:
    def __init__(self,serial_number,status):
        
        self.serial_number = serial_number
        os.add_dll_directory('C:\\Program Files\\Thorlabs\\Kinesis') # MIGHT HAVE TO CHANGE THIS LINE 
        self.lib : CDLL = cdll.LoadLibrary('Thorlabs.MotionControl.Benchtop.DCServo.dll')

        # Initial position to be defined
        self.x_init = 8000
        self.y_init = 8000

        # Displacement speed for X and Y to be defined
        self.x_step = 10000
        self.y_step = 10000
        self._step = 10000
        self.x_small_step = 25
        self.y_small_step = 25

        # Position
        self.X = self.x_init
        self.Y = self.y_init

        self.status = status

    def build_device(self):
        
        if self.lib.TLI_BuildDeviceList() == 0:
            ret = self.lib.BDC_Open(self.serial_number)
            print(f'BDC_Open Returned {ret}')
            self.lib.BDC_EnableChannel(self.serial_number, 1)
            self.lib.BDC_EnableChannel(self.serial_number, 2)

    def close_device(self):
        self.lib.BDC_Close(self.serial_number)
        print("Device turned off")

    def move_r(self):
        self.X = self.X + self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 1, self.X)
        time.sleep(1)  # 250ms wait time to ensure values are sent to device
        self.lib.BDC_MoveAbsolute(self.serial_number, 1)
        time.sleep(2)
        self.print_position()

    def move_l(self):
        self.X = self.X - self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 1, self.X)
        time.sleep(1)
        self.lib.BDC_MoveAbsolute(self.serial_number, 1)
        time.sleep(2)
        self.print_position()

    def move_t(self):
        self.Y = self.Y + self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 2, self.Y)
        time.sleep(1)  # 250ms wait time to ensure values are sent to device
        self.lib.BDC_MoveAbsolute(self.serial_number, 2)
        time.sleep(2)
        self.print_position()

    def move_b(self):
        self.Y = self.Y - self._step
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 2,self.Y)
        time.sleep(1)
        self.lib.BDC_MoveAbsolute(self.serial_number, 2)
        time.sleep(2)
        self.print_position()

    def move_step_x(self, step):
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 1, step)
        time.sleep(1)

        self.lib.BDC_MoveAbsolute(self.serial_number, 1)
        time.sleep(1)
    
    def move_step_y(self, step):
        self.lib.BDC_SetMoveAbsolutePosition(self.serial_number, 2, step)
        time.sleep(1)

        self.lib.BDC_MoveAbsolute(self.serial_number, 2)
        time.sleep(1)

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

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        self.status = new_status

    def update_reference(self):
        self.x_init = self.X
        self.y_init = self.Y
        self.reference_text["text"] = f"Référence : ({self.x_init}, {self.y_init})"

    def set_position(self, stage_x, stage_y):
        self.X = self.x_init + stage_x
        self.move_step_x(self.X)
        self.Y = self.y_init + stage_y
        self.move_step_y(self.Y)
        self.print_position()
        self.update_label()

    def print_position(self):
        print("(", self.X, ",", self.Y, ")")

    def create_label(self):
        self.label = tk.Label(self.master, text="Localisation actuelle de la voiture : (0, 0)", font=("Arial", 10), bg="#A1002F")
        self.label.pack(pady=10)

    def update_label(self):
        self.label["text"] = f"Localisation actuelle de la voiture : ({self.X}, {self.Y})"
        
    def move_sequence(self,sequence):
        positions = sequence.split(";")
        for pos in positions:
            try:
                x, y = pos.split(",")
                x = int(x)
                y = int(y)
                self.set_position(x, y)
                #TO DO : optimization for the alignement
                time.sleep(1) # Ajouter un court délai pour voir chaque position/optimization
                #TO DO : once optimized, use spectrometer to register in .npy
            except ValueError:
                print("Error: Incorrect format for the coordinates.")

