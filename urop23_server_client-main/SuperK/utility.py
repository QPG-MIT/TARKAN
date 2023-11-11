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

