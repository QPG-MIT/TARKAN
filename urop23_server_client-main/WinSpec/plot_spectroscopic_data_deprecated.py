import numpy as np
import matplotlib.pyplot as plt
import time

def update_spect_plot(raw_data, pause):
    #intensity_np.pop(0)
    #print(intensity_np)
    #print('This is the number of data points:', len(intensity_np))
    # center_wavelength = raw_data['GRAT_POS']
    plt.ion()
    fig = plt.figure() 
    intensity_np = raw_data['y'][0]
    min_wavelength, max_wavelenght = raw_data['CAL_CALIBVAL'][0], raw_data['CAL_CALIBVAL'][2]
    wavelength_np = np.linspace(min_wavelength, max_wavelenght, len(intensity_np))
                                
    plt.xlabel(r'$Wavelength \ (nm)$', fontsize = 18)
    plt.ylabel(r'$Intensity \ (arb. \ units) $', fontsize=18)
    #plt.scatter(wavelength_np, intensity_np, s=1)
    plt.plot(wavelength_np, intensity_np, color = 'purple')
    fig.canvas.draw()
    fig.canvas.flush_events()
    time.sleep(pause)
   # plt.clf() # clear the previous figure