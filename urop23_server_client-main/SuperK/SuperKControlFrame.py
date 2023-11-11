import tkinter as tk
from tkinter import ttk
from SuperK.utility import *
from SuperK.superkClass import superk

class SuperKControlFrame(tk.Frame):
    def __init__(self, master, serial_number):
        super().__init__(master, bg="white")
        self.superk = superk(serial_number)
        self.create_widgets()
        self.laser_status = self.superk.emission()
        # self.change_button_color()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=2)  # Customize the "TButton" style
        style.configure("white.TButton", background="white")  # Define the "white.TButton" style

        label = tk.Label(self, text="SuperK", font=("Arial", 10, "bold"), bg="white")
        label.grid(row=0,column=0)

        self.button = tk.Button(self, text="OFF", command=self.change_button_color, bg="red")
        self.button.grid(row=1,column=1)
        
        wavelength_label = tk.Label(self, text="Wavelength [nm] :", font=("Arial", 10), bg="white")
        self.wavelength_entry = tk.Entry(self)
        self.wavelength_display = tk.Label(self, text="{} [nm]".format(self.superk.getwavelength()),font=("Arial", 12), bg="white")

        wavelength_label.grid(row=2, column=0, pady=10)
        self.wavelength_entry.grid(row=2, column=1,pady=10)
        self.wavelength_display.grid(row=2,column=2,pady=10)

        bandwidth_label = tk.Label(self, text="Bandwidth [nm] :", font=("Arial", 10), bg="white")
        self.bandwidth_entry = tk.Entry(self)
        self.bandwidth_display = tk.Label(self, text="{} [nm]".format(self.superk.getbandwidth()),font=("Arial", 12), bg="white")

        bandwidth_label.grid(row=3, column=0, pady=10)
        self.bandwidth_entry.grid(row=3, column=1,pady=10)
        self.bandwidth_display.grid(row=3,column=2,pady=10)

        power_label = tk.Label(self, text="Power [%] :", font=("Arial", 10), bg="white")
        self.power_entry = tk.Entry(self)
        self.power_display = tk.Label(self, text="{} [%]".format(self.superk.getpower()),font=("Arial", 12), bg="white")

        power_label.grid(row=4, column=0, pady=10)
        self.power_entry.grid(row=4, column=1,pady=10)
        self.power_display.grid(row=4,column=2,pady=10)

        OD_label = tk.Label(self, text="OD :", font=("Arial", 10), bg="white")
        self.OD_entry = tk.Entry(self, textvariable=self.superk.OD)
        self.OD_display = tk.Label(self, text="{}".format(self.superk.OD.get()),font=("Arial", 12), bg="white")

        OD_label.grid(row=5, column=0, pady=10)
        self.OD_entry.grid(row=5, column=1, pady=10)
        self.OD_display.grid(row=5, column=2, pady=10)

        button_parameter = ttk.Button(self, text="OK", command=self.update_parameters, style=("TButton", "white.TButton"))
        button_parameter.grid(row=7,column=1,pady=10)

    def update_parameters(self):
        self.update_wavelength()
        self.update_bandwidth()
        self.update_power()

    def update_wavelength(self):
        new_wavelength = self.wavelength_entry.get()
        if new_wavelength != self.wavelength_display["text"] and self.is_wavelength_valid(new_wavelength) :
            self.wavelength_display.config(text=f"{new_wavelength} [nm]")
            self.superk.setwavelength(new_wavelength)

    def update_bandwidth(self):
        new_bandwith = self.bandwidth_entry.get()
        if new_bandwith != self.bandwidth_display["text"] and self.is_bandwidth_valid(new_bandwith) :
            self.bandwidth_display.config(text=f"{new_bandwith} [nm]")
            self.superk.setbandwidth(new_bandwith)

    def update_power(self):
        new_power = self.power_entry.get()
        if new_power != self.power_display["text"] and self.is_power_valid(new_power) :
            self.power_display.config(text=f"{new_power} [%]")
            self.superk.setpower(new_power)

    def is_wavelength_valid(self,wavelength):
        try:
            wavelength = float(wavelength)
            if 450 <= wavelength <= 2400:
                return True
            else:
                return False
        except ValueError:
            print("Error : the enetered wavelengh is invalid.")
            return False

    def is_bandwidth_valid(self,bandwidth):
        try:
            bandwidth = float(bandwidth)
            if 1 <= bandwidth <= 200:
                return True
            else:
                return False
        except ValueError:
            print("Error : the enetered bandwidth is invalid.")
            return False

    def is_power_valid(self,power):
        try:
            power = float(power)
            if 1 <= power <= 95:
                return True
            else:
                return False
        except ValueError:
            print("Error : the enetered power is invalid.")
            return False

    def change_button_color(self):
        if self.laser_status == "off":
            self.button.configure(text="ON", bg="green")
            self.laser_status = "on"
            self.superk.on()
        else:
            self.button.configure(text="OFF", bg="red")
            self.laser_status = "off"
            self.superk.off()