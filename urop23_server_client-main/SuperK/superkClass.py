import sys
import os
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd()) 
from serial.tools import list_ports
from SuperK.utility import *
from SuperK.comClass import com
import tkinter as tk


class SuperKerror(Exception):
    # Wrapper for superk._com transmission/reply errors
    pass

class superk:
    HELP = \
'''Available functions (* means 'get' or 'set' available)
on - turns emission on
off - turns emission off
emission - returns on/off depending on emission state
getcurrent - gets current (%)
*power - power (%)
*pulsepicker - pulse picker divider (integer); reprate is changed by this
*reprate - reprate (MHz); pulsepicker is changed by this
*wavelength - sets center wavelength (nm)
*bandwidth - sets bandwidth (nm)
*ND - sets ND filter (%)'''

    def __init__(self, serial_number=None):
        self.ui = serial_number  # add your unique identifier! format: '0000:0000'
        if self.ui is None:
            raise SuperKerror('No unique identifier set')
        port = [port.device for port in list_ports.comports() if self.ui in port.usb_info()]
        if not len(port)==1:
            raise SuperKerror('Found %i ports matching the unique identifier'%len(port))
        self.serial = com(port[0])
        self.retries = 3  # Retries on checksum failure or busy

        self.max_reprate = 78.074  # MHz
        # Addresses
        self._module = 15
        self._varia = 17
        
        self.OD = tk.StringVar(value='n/a')

        self.setpulsepicker(2)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self._Close()

    def _Close(self):
        if self.serial.isOpen():
            self.serial.close()

    def _com(self,dest,typ,reg,data=[]):
        # Return true on ACK
        # Return data on DATAGRAM
        # Error otherwise
        tries = 0
        while tries < self.retries:
            tries += 1
            self.serial.send(dest,typ,reg,data)
            [src,typ,reg,data] = self.serial.recv()
            if typ == NACK:
                raise SuperKerror('Message not understood, not applicable, or not allowed.')
            elif typ == CRC_ERR or typ == BUSY:
                tries += 1
            elif typ == ACK:
                return True
            elif typ == DATAGRAM:
                return data
        if typ == CRC_ERR:
            raise SuperKerror('CRC Error.')
        elif typ == BUSY:
            raise SuperKerror('Busy.')
        else:
            raise SuperKerror('Unhandled Error.')

    def _help():
        return superk.HELP

    # SuperK Extreme Controls
    def on(self):
        return self._com(self._module,WRITE,0x30,0x3)

    def off(self):
        return self._com(self._module,WRITE,0x30,0x0)

    def emission(self):
        val = self._com(self._module,READ,0x30)[0]
        if val == 0:
            return 'off'
        elif val == 3:
            return 'on'
        else:
            raise SuperKerror('Unexpected value returned.')

    def getcurrent(self):
        # Percent
        data = self._com(self._module,READ,0x38)
        data = bytes2int(data)
        return data*0.1

    def getpower(self):
        # Percent
        data = self._com(self._module,READ,0x37)
        data = bytes2int(data)
        return data*0.1

    def setpower(self,val):
        # val is percent
        data = int(float(val)*10)
        return self._com(self._module,WRITE,0x37,data)

    def getpulsepicker(self):
        # Divider integer
        return bytes2int(self._com(self._module,READ,0x34))

    def setpulsepicker(self,val):
        # val is Divider integer
        return self._com(self._module,WRITE,0x34,int(val))

    def getreprate(self):
        # MHz
        return float(self.max_reprate)/bytes2int(self._com(self._module,READ,0x34))

    def setreprate(self,val):
        # Val in MHz
        divider = int(round(float(self.max_reprate)/float(val)))
        assert divider>0, 'Maximum reprate is %0.2f MHz, you tried to set %0.2f MHz'%(self.max_reprate,val)
        self._com(self._module,WRITE,0x34,divider)
        set_reprate = float(self.max_reprate)/divider
        return set_reprate

    # SuperK Varia Controls
    def getwavelength(self):
        # nm
        LWP = bytes2int(self._com(self._varia,READ,0x34))*0.1
        SWP = bytes2int(self._com(self._varia,READ,0x33))*0.1
        return (LWP+SWP)/2.0

    def setwavelength(self,center):
        # nm
        BW = self.getbandwidth()
        LWP = float(center) - BW/2.0
        SWP = float(center) + BW/2.0
        assert LWP<SWP, SuperKerror('LWP is greater than SWP!')
        self._com(self._varia,WRITE,0x34,LWP*10)
        self._com(self._varia,WRITE,0x33,SWP*10)
        return True

    def getbandwidth(self):
        # nm
        LWP = bytes2int(self._com(self._varia,READ,0x34))*0.1
        SWP = bytes2int(self._com(self._varia,READ,0x33))*0.1
        return SWP-LWP

    def setbandwidth(self,BW):
        # nm
        center = self.getwavelength()
        LWP = center - float(BW)/2.0
        SWP = center + float(BW)/2.0
        assert LWP<SWP, SuperKerror('LWP is greater than SWP!')
        self._com(self._varia,WRITE,0x34,LWP*10)
        self._com(self._varia,WRITE,0x33,SWP*10)
        return True

    def getND(self):
        # percent
        return bytes2int(self._com(self._varia,READ,0x32))*0.1

    def setND(self,val):
        # percent
        data = int(float(val)*10)
        return self._com(self._varia,WRITE,0x32,data)

    # General access to full control (advanced users)
    def custom(self,addr,reg,data=[]):
        # Assumes read if data=[], write otherwise
        typ = READ
        data = [float(item) for item in data]
        if len(data):
            typ = WRITE
        return self._com(addr,typ,reg,data)

# if __name__=='__main__':
#     print(superk._help())
#     with superk() as s:
#         print('Port:',s.serial.serial.port)
#         #s.on()
#         s.off()
#         s.setwavelength(620)
#         s.setpower(20)
#         s.setbandwidth(10)
#         print('Emission:',s.emission())
#         print('Power: %0.1f %%'%s.getpower())
#         print('Current: %0.1f %%'%s.getcurrent())
#         print('Pulse Picker Divider: %i (%0.2f MHz)'%(s.getpulsepicker(),s.getreprate()))
#         print('Wavelength: %0.1f nm'%s.getwavelength())
#         print('Bandwidth: %0.1f nm'%s.getbandwidth())
#         print('ND Filter: %0.1f %%'%s.getND())
    
