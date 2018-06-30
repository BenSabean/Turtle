#!/usr/bin/python2

#
# Class to interract with Timing Arduino controller 
# using I2C to exchange timming data
# 1. Register (2nd parameter in func)
# 2. Message lenght 
# 3. Byte array
#

#from smbus import SMBus
from time import sleep
from smbus2 import SMBusWrapper, i2c_msg,  SMBus

class Timer():
    # Definitions
    ARDUINO = 0x05
    SLEEP_CMD = 0x01
    RELEASE_CMD = 0x02
    CHECK_CMD = 0xAA

    # set sleep time for arduino and return result
    def setSleep(self, hour, min):
        with SMBusWrapper(1) as bus:
           bus.write_i2c_block_data(self.ARDUINO, self.SLEEP_CMD, [hour,min])
           sleep(0.5)
           resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)
           if(resp[0] == 1):
               return True
        return False

    # set release time for arduino and return result
    def setRelease(self, hour, min):
        with SMBusWrapper(1) as bus:
           bus.write_i2c_block_data(self.ARDUINO, self.RELEASE_CMD, [hour,min])
           sleep(0.5)
           resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)
           if(resp[1] == 1):
               return True
        return False

    # return array of two status flags from arduino [sleep, release]
    def checkStatus(self):
        with SMBusWrapper(1) as bus:
           return bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)

    # getting battery voltage from arduino
    def getVoltage(self):
        with SMBusWrapper(1) as bus:
            resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)
            try:
                vol = (resp[3] << 8) | resp[2]
                vol = float(vol)/1024 * 5
                return str(vol)
            except: pass
        
