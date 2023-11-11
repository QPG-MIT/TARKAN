from client.clientClass import client
import pickle
from tkinter import filedialog
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import datetime

class WinSpec():
    def __init__(self, spect_address, spect_port, measurement):
        self.client = client(host=spect_address, port=spect_port)
        self.wavelength = tk.StringVar(value='650')
        self.grating = tk.StringVar(value='3')
        self.exposure = tk.StringVar(value='1')
        self.save_location = tk.StringVar(value='No directory selected.')
        self.data = None
        self.measurement = measurement

        # Create the one and only figure that gets passed to the acquisition and plot functions for drawing.
        # It gets flushed and redrawn any time a new plot is made.
        self.fig = plt.figure(figsize=(7, 4))

    def update_parameters(self):
        wavelength = self.wavelength.get()
        grating = self.grating.get()
        exposure = self.exposure.get()
        # Update the spectrometer parameters with the values

        print("Updated parameters:")
        print("Wavelength:", wavelength)
        print("Grating:", grating)
        print("Exposure:", exposure)

        #if self.wavelength != wavelength or self.grating != grating:
        first_resp = self.client.com('spectrometer', 'grating', grating, wavelength)
        print('Success status of setting the grating and the wavelength: ', first_resp['success'])
        
        #if self.exposure != exposure:
        second_resp = self.client.com('spectrometer', 'exposure', exposure)
        print('Success status of setting the exposure: ', second_resp['success'])

    def focus(self, button, master):
        # Code to focus the spectrometer until the user clicks on the focus button again
        if button['text'] == 'Focusing stopped':
            print("Focusing...")
            try:
                button.configure(text="Focusing started", bg="green")
                master.update_idletasks() # to make the button update instantly after clicking rather than letting the event loop do it
                                          # a couple seconds later
                self.run_focus(self.fig, button, master)
            except Exception as err:
                print('Some exception was raised during focusing: ', err)
        else:
            print("Stopping focusing...")
            button.configure(text="Focusing stopped", bg="red")

    def run_focus(self, figure, button, master):
        self.acquire_and_plot_data(figure)
        master.update_idletasks() # to make the plot update instantly after taking the data, otherwise the plot updates generally
                                  # trail behind 2-3 data acquisitions, and sometimes they freeze and don't update at all for some period
        if button['text'] == 'Focusing started':
            master.after(int(float(self.exposure.get())+1), self.run_focus, figure, button, master)
            
    def acquire_and_plot_data(self, figure):
        # Code to acquire data from the spectrometer
        print("Establishing connection and acquiring data...")
        # Sometimes, there is a problem with data acquisition. json.loads() throws an 'unexpected delimeter' error. The error
        # seems to be random and inherent to the way quote/unquote functions are working in Python, and despite me trying to 
        # correct it inside the com class manually, sometimes the error still 
        # seems to slip. Therefore, the best way to tackle this seems to just retry data acquisition. Here, we try re-acquiring
        # data 5 times before we finally raise an error. 
        retries = 5 
        while retries > 0:
            try:
                resp = self.client.com('spectrometer', 'acquire')
                break
            except Exception as error:
                retries -= 1
                if retries == 0:
                    print('Data acquisition failed after 5 retries. The most recent error was:\n', error)
                    raise error
                print('The following error was encountered during data acquisition, therefore, retrying...\n', error)
                continue
            
        print('Success status of acquiring data: ', resp['success'])
        self.data = resp['response']
        self.update_spect_plot(self.data, figure)
        return self.data

    def select_save_location(self):
        save_location = self.save_location.get()
        # Code to select the save location
        print("Selected save location:", save_location)

    def setup(self):
        # Run setup.vbs 
        print('Running setup.vbs...')
        resp = self.client.com('spectrometer', 'setup')
        print('Success status of setup: {}'.format(resp['success']))

    def get_parameters(self):
        '''
        Get the current value of [grating, wavelength, exposure]
        '''
        print('Querying parameters...')
        resp = self.client.com('spectrometer', 'getgratingandexposure')
        #print('The current value of [grating, wavelength, exposure] is {}'.format(resp['response']))
        self.grating.set(resp['response'][0])
        self.wavelength.set(resp['response'][1])
        self.exposure.set(resp['response'][2])
        return resp['response']

    def update_spect_plot(self, raw_data, fig):
        fig.clf() # clear the previous figure
        plt.xlabel(r'$Wavelength \ (nm)$', fontsize = 10)
        plt.ylabel(r'$Intensity \ (arb. \ units) $', fontsize=10)
        intensity_np = raw_data['y'][0]
        min_wavelength, max_wavelenght = float(raw_data['CAL_CALIBVAL'][0]), float(raw_data['CAL_CALIBVAL'][2])
        wavelength_np = np.linspace(min_wavelength, max_wavelenght, len(intensity_np))
        plt.plot(wavelength_np, intensity_np, color = 'purple', )
        self.fig.canvas.draw_idle() # redraw the canvas after plotting

    def choose_directory(self):
        # Open the file dialog to choose a directory
        directory = filedialog.askdirectory()

        # Display the chosen directory
        if directory:
            self.save_location.set(directory)
        else:
            self.save_location.set("No directory selected.")
    
    def save(self, hmp, label=None):
        all_params = self.measurement.get_all_params(True, True, hmp)
        data_to_save = all_params | {'data': self.data} # merge parameter and data dictionaries 
        if hmp:
            tot_voltage = all_params['hmp_params']['tot_voltage']
        else:
            tot_voltage = None
        filename = self.get_filename(tot_voltage, label)
        with open(filename+'.pkl', "wb") as file:
            pickle.dump(data_to_save, file)
        self.fig.savefig(filename+'_spect_graph')

    def get_filename(self, tot_voltage, label=None):
        now = str(datetime.datetime.now()).replace(' ', '-').replace(':', '_')[:19] # we slice because we don't need the time after decimal point
        if tot_voltage is not None:
            split_voltage = str(tot_voltage).split('.')
            voltage_underscore = split_voltage[0]+'_'+split_voltage[1]
            filename = self.save_location.get() + '\\' + voltage_underscore + '_' + now
        elif label is not None:
            filename = self.save_location.get() + '\\' + label + '_' + now
        return filename
    
    def toggle_WinSpec(self, button):
        # Code to turn the spectrometer on or off
        if button['text'] == 'WinSpec is closed':
            button.configure(text="WinSpec is running", bg="green")
            print("Starting WinSpec...")
            resp = self.client.com('spectrometer', 'start')
            print('Message from server: ', resp['response'])
        else:
            button.configure(text="WinSpec is closed", bg="red")
            print("Closing WinSpec...")
            resp = self.client.com('spectrometer', 'close')
            print('Message from server: ', resp['response'])

# Example usage
#root = tk.Tk()
#spectrometer_frame = WinSpecControlFrame(root, False)
#spectrometer_frame.pack()
#root.mainloop()
