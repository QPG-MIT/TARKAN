# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 10:52:15 2023

@author: SPECTRO
"""

#for pinging COM ports with a Princeton Instruments spectrograph attached
import serial

TIMEOUT = 10

def clearSer(obj):
    obj.flushInput()
    obj.flushOutput()

#the wait function blocks the thread until an 'ok' is returned by the instrument
def WaitForSerial(specObj):
    flagStop = 0
    commStr = ''
    print('we are inside WaitForSerial')
    commStr = specObj.read(1).decode()
    while flagStop == 0:
        old_commStr = commStr
        # print('we are inside the while loop')
        commStr += specObj.read(1).decode()
        if 'ok' in commStr or old_commStr == commStr:
            flagStop = 1
    print(commStr)
    clearSer(specObj)

#in the next line, change the COM port to the one you want to use
ser=serial.Serial('COM10',baudrate=9600,parity=serial.PARITY_NONE,bytesize=serial.EIGHTBITS,
                  stopbits=serial.STOPBITS_ONE,timeout=TIMEOUT)
print('this is the port name', ser.name)
clearSer(ser)

ser.write('?GRATINGS'.encode()+ b'\x0d')
WaitForSerial(ser)
#ser.write('750 goto'.encode()+ b'\x0d')
#WaitForSerial(ser)
#ser.write('750 goto'.encode()+ b'\x0d')
#WaitForSerial(ser)
ser.write('620 INIT-WAVELENGTH'.encode()+ b'\x0d')
WaitForSerial(ser)
ser.write('MODEL'.encode()+ b'\x0d')
WaitForSerial(ser)
print('done')
ser.close()


#example output
#  1 1200 g/mm BLZ=  500NM
#  2  600 g/mm BLZ=  500NM
#  3  150 g/mm BLZ=  800NM
#  4  Not Installed    
#  5  Not Installed    
#  6  Not Installed    
#  7  Not Installed    
#  8  Not Installed    
#  9  Not Installed    
#  ok
#  ok
#  ok
# done