import tkinter as tk
from tkinter import ttk
import os, sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd()) 
from WinSpec.WinSpecClass import WinSpec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WinSpecControlFrame(tk.Frame):
    def __init__(self, master, spect_address, spect_port, get_initial_params, measurement):
        super().__init__(master, bg="white")
        self.master = master
        self.spect = WinSpec(spect_address, spect_port, measurement)
        self.wavelength = self.spect.wavelength
        self.grating = self.spect.grating
        self.exposure = self.spect.exposure
        self.save_location = self.spect.save_location

        self.create_widgets(get_initial_params)

    def create_widgets(self, get_initial_params):
        label = tk.Label(self, text="WinSpec Spectrometer", font=("Arial", 15, "bold"), bg="white")
        label.grid(row=0, column=0, padx=10, pady=10)

        # WinSpec start/close control
        self.onoff_button = tk.Button(self, text="WinSpec is running", command=lambda: self.spect.toggle_WinSpec(self.onoff_button), bg='green')
        self.onoff_button.grid(row=1, column=0, padx=10, pady=10)

        # Parameters window
        parameters_frame = ttk.LabelFrame(self, text="Parameters")
        parameters_frame.grid(row=2, column=0, padx=10, pady=10)

        wavelength_label = tk.Label(parameters_frame, text="Wavelength", font=("Arial", 10), bg="white")
        wavelength_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.wavelength_entry = tk.Entry(parameters_frame, textvariable=self.wavelength, width=10)
        self.wavelength_entry.grid(row=0, column=1, padx=5, pady=5)

        grating_label = tk.Label(parameters_frame, text="Grating Selection", font=("Arial", 10), bg="white")
        grating_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.grating_entry = tk.Entry(parameters_frame, textvariable=self.grating, width=10)
        self.grating_entry.grid(row=1, column=1, padx=5, pady=5)

        exposure_label = tk.Label(parameters_frame, text="Exposure", font=("Arial", 10), bg="white")
        exposure_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.exposure_entry = tk.Entry(parameters_frame, textvariable=self.exposure, width=10)
        self.exposure_entry.grid(row=2, column=1, padx=5, pady=5)

        ok_button = ttk.Button(parameters_frame, text="OK", command=self.spect.update_parameters)
        ok_button.grid(row=3, column=1, padx=5, pady=5)

        current_params_button = ttk.Button(parameters_frame, text="Get current parameters", command=self.spect.get_parameters)
        current_params_button.grid(row=4, column=1, padx=5, pady=5)

        # Functions window
        functions_frame = ttk.LabelFrame(self, text="Functions")
        functions_frame.grid(row=3, column=0, padx=10, pady=10)

        acquire_button = ttk.Button(functions_frame, text="Acquire", command=lambda: self.spect.acquire_and_plot_data(self.spect.fig))
        acquire_button.grid(row=0, column=0, padx=5, pady=5)

        self.focus_button = tk.Button(functions_frame, text="Focusing stopped", command=lambda: self.spect.focus(self.focus_button, self.master), bg='red')
        self.focus_button.grid(row=0, column=1, padx=5, pady=5)

        # Save window
        save_frame = ttk.LabelFrame(self, text='Saving')
        save_frame.grid(row=4, column=0, padx=10, pady=10)
        self.directory_button = tk.Button(save_frame, text="Choose Save Directory", font=("Arial", 10), bg="white", command=self.spect.choose_directory)
        self.directory_button.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.directory_entry = tk.Entry(save_frame, textvariable=self.save_location, width=20)
        self.directory_entry.grid(row=1, column=1, padx=5, pady=5)

        save_button = ttk.Button(save_frame, text="Save", command=lambda: self.spect.save(hmp=True))
        save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Plot window
        plot_frame = ttk.LabelFrame(self, text="Data Plot")
        plot_frame.grid(row=0, column=1, rowspan=5, padx=10, pady=10)

        canvas = FigureCanvasTkAgg(self.spect.fig, master=plot_frame)
        plot_widget = canvas.get_tk_widget()
        plot_widget.grid(row=0, column=0, sticky='e')

        # Get the initial parameters on startup
        if get_initial_params:
            self.spect.get_parameters()

    

    


