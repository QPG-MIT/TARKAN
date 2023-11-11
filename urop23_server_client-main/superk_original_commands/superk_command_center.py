import Driver
import hwserver

class SuperK(Driver):
    hwname = 'superk'

    def __init__(self, ip):
        self.connection = hwserver(ip)

    def com(self, funcname, *args):
        return self.connection.com(self.hwname, funcname, *args)

    def on(self):
        self.com('on')

    def off(self):
        self.com('off')

    def setPower(self, val):
        assert 0 < val < 100, 'Power should be between 0% and 100%'
        strval = str(val)
        self.com('setpower', strval)

    def setND(self, val):
        assert 0 < val < 100, 'ND filter setting should be between 0% and 100%'
        strval = str(val)
        self.com('setND', strval)

    def setBandwidth(self, val):
        assert val > 0, 'Bandwidth must be > 0'
        strval = str(val)
        self.com('setbandwidth', strval)

    def setPulsePicker(self, val):
        assert val % 1 == 0, 'Must pick out an integer # of pulses'
        strval = str(val)
        self.com('setpulsepicker', strval)

    def setRepRate(self, val):
        assert val > 0, 'Rep. rate must be positive'
        strval = str(val)
        self.com('setreprate', strval)

    def setWavelength(self, val):
        strval = str(val)
        self.com('setwavelength', strval)

    def getND(self):
        return self.com('getND')

    def getBandwidth(self):
        return self.com('getbandwidth')

    def getPower(self):
        return self.com('getpower')

    def getPulsePicker(self):
        return self.com('getpulsepicker')

    def getRepRate(self):
        return self.com('getreprate')

    def getCurrent(self):
        return self.com('getcurrent')

    def getWavelength(self):
        return self.com('getwavelength')