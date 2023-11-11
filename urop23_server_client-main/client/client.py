import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd()) 

from clientClass import client
from WinSpec.plot_spectroscopic_data_deprecated import plot_spect_data

myclient = client(host = '18.25.30.120', port = 36577)

#print(myclient.ping_spectrometer())
#print(myclient.com('spectrometer', 'start'))
#myclient.com('_get_modules')
#myclient.com('superkClass', 'off')
myclient.com('spectrometer', 'get_params')

#plot_spect_data(spect_data)

#myclient.com('superkClass', 'off')


