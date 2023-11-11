import time
import serial
from control_superk_original import superk

if __name__ == "__main__":
    with superk() as laser:
        laser.on()
        laser.setpower(100)
        laser.setbandwidth(1)
        laser.setwavelength(630)
        laser.setND(40) # 95 originally... but this doesn't seem to change anything
        print(laser.getpower())
        print(laser.getbandwidth())
        print(laser.getwavelength())
        # print(laser.getND())
        # time.sleep(10)

        laser.off()