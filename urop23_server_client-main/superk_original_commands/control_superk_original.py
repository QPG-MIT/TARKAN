import serial
from serial.tools import list_ports
from serial import rs485

# Telegram special characters
SOT = 0x0D  # Start of telegram
EOT = 0x0A  # End of telegram
SOE = 0x5e  # Start of subsitituion
ECC = 0x40  # Value to shift for subsitution

# Response Message Types
NACK    = 0x00
CRC_ERR = 0x01
BUSY    = 0x02
ACK     = 0x03
DATAGRAM= 0x08
# Transmission Message Types
READ = 0x04
WRITE= 0x05


CHAR = 0xFF    # 8 bits
INT = 0xFFFF   # 16 bits

def int2bytes(val,nbytes=None):
    # Little-endian
    bytes = []
    if nbytes:
        for i in range(nbytes):
            bytes.append(val&0xFF)
            val = val >> 8
    else:
        if val == 0:
            return [0]
        while val:
            bytes.append(val & 0xFF)
            val = val >> 8
    return bytes

def bytes2int(bytes):
    # Bytes in Little-endian
    val = 0
    bytes.reverse()
    for byte in bytes:
        val = val << 8
        val ^= byte
    return val

class com:
    # A frame is as follows (each section 1 Byte):
    # | dst addr | src addr | msg type | register | data | .|.|.| CRC MSB| CRC LSB |
    def __init__(self,port):
        self.serial = serial.Serial(
            port = port,
            baudrate = 115200,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            rtscts = True,
            timeout = 1,
        )
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        
        self._msg = []         # Used to build a telegram before sending
        self.my_address = 0xA2 # HOST address (must be larger than 160)
    
    # Carry over some serial functions
    def isOpen(self):
        return self.serial.isOpen()
    def close(self):
        return self.serial.close()
    
    # Calculate CRC value
    @staticmethod
    def _crc(data,crc=0):
        assert crc <= INT, Exception('crc needs to be a 16 bit value')
        assert data <= CHAR, Exception('Data needs to be an 8 bit value')
        # Code adapted from C code in manual
        #   crc should be 16 bit integer
        #   data should be 8 bit integer
        crc = (((crc>>8)&CHAR)|(crc<<8))&INT
        crc ^= data
        crc ^= (crc&CHAR)>>4
        crc ^= (((crc<<8)&INT)<<4)&INT
        crc ^= ((((crc&CHAR)<<4)&INT)<<1)&INT
        return crc&INT

    # Place Byte
    def _com_putc(self,data):
        self._msg.append(data)
        if data == EOT:
            self.serial.write(bytearray(self._msg))
            self.serial.flush()
            self._msg = []

    # Transmit without CRC calc
    def _TXnocrc(self,data):
        assert data < 2**8, Exception('Data needs to be an 8 bit value')
        if data == SOT or data == EOT or data == SOE:
            self._com_putc(SOE)
            data += ECC
        self._com_putc(data)

    # Transmit 1 byte and calculate CRC
    def _TX1(self,data,crc):
        crc = self._crc(data,crc)
        self._TXnocrc(data)
        return crc

    # Transmit complete telegram
    def send(self,dest,typ,reg,data=[],nbytes=None):
        # data needs to be an array or integer
        # nbytes (if specified) will force int2bytes to return nbytes

        # Format data correctly, and check type
        if type(data)!=list:
            data = [data]
        for i, dat in enumerate(data):
            if type(dat)==int:
                continue
            try:
                if int(dat)==float(dat):
                    data[i] = int(dat)
                else:
                    raise ValueError()
            except ValueError:  # Catch if data is non-numeric string or non-integer value
                raise ValueError('Data needs to be integer or list of integer values.')

        self._com_putc(SOT)                     # Start telegram
        crc = self._TX1(dest,0)                 # Destination address
        crc = self._TX1(self.my_address,crc)    # Source address
        crc = self._TX1(typ,crc)                # Message type
        crc = self._TX1(reg,crc)                # Register number
        for dat in data:
            for byte in int2bytes(dat,nbytes):
                crc = self._TX1(byte,crc)        # Transmit data
        self._TXnocrc((crc>>8)&0xFF)            # Transmit CRC MSB
        self._TXnocrc(crc&0xFF)                 # Transmit CRC LSB
        self._com_putc(EOT)                     # End telegram

    def recv(self):
        # Receives data and checks for accuracy and destination
        # returns: src, typ, reg, data
        # Data will be empty unless type = DATAGRAM
        # Data is in raw format and will depend on query
        #   Remember an integer is little-endian

        # Get full message
        raw = []
        while len(raw)==0 or raw[-1] != EOT:
            byte = self.serial.read(1)
            assert len(byte) == 1, IOError('Did not receive a response in time.')
            raw.append(ord(byte))
        # Decode frame
        tlg = []
        crc = 0
        special_char = False
        for byte in raw:
            if byte == SOT:
                continue
            elif byte == EOT:
                assert crc == 0, Exception('Checksum failed.')
                break
            elif byte == SOE:
                special_char = True
            else: # Default
                if special_char:
                    special_char = False
                    byte -= ECC
                crc = self._crc(byte,crc)
                tlg.append(byte)
        dest = tlg[0]
        src = tlg[1]
        typ = tlg[2]
        reg = tlg[3]
        data = tlg[4:-2]
       # assert dest==self.my_address, Exception('Wrong destination address.')
        return [src,typ,reg,data]

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

    def __init__(self):
        ui = '10C4:EA60'  # Unique identifier
        port = [port.device for port in list_ports.comports() if ui in port.usb_info()]
        if not len(port)==1:
            raise SuperKerror('Found %i ports matching the unique identifier'%len(port))
        self.serial = com(port[0])

        self.retries = 3  # Retries on checksum failure or busy

        self.max_reprate = 78.074  # MHz
        # Addresses
        self._module = 15
        self._varia = 17

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

if __name__=='__main__':
    print(superk._help())
    with superk() as s:
        print('Port:',s.serial.serial.port)
     #   s.off()
        print('Emission:',s.emission())
        print('Power: %0.1f %%'%s.getpower())
        print('Current: %0.1f %%'%s.getcurrent())
        print('Pulse Picker Divider: %i (%0.2f MHz)'%(s.getpulsepicker(),s.getreprate()))
        print('Wavelength: %0.1f nm'%s.getwavelength())
        print('Bandwidth: %0.1f nm'%s.getbandwidth())
        print('ND Filter: %0.1f %%'%s.getND())