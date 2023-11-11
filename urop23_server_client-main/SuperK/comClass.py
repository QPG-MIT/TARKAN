from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from SuperK.utility import *

class com:
    # A frame is as follows (each section 1 Byte):
    # | dst addr | src addr | msg type | register | data | .|.|.| CRC MSB| CRC LSB |
    def __init__(self,port):
        self.serial = Serial(
            port = port,
            baudrate = 115200,
            parity = PARITY_NONE,
            stopbits = STOPBITS_ONE,
            bytesize = EIGHTBITS,
            rtscts = True,
            timeout = 1,
        )
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        
        self._msg = []         # Used to build a telegram before sending
        self.my_address = 0xA2 # HOST address in hex (must be larger than 160)
    
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