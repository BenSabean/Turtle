#!/usr/bin/python2

#
# I2C function sends data in the following format:
# 1. Register (2nd parameter in func)
# 2. Message lenght 
# 3. Byte array
#


from smbus import SMBus
from time import sleep
import sys


def CRC(val):
  crc = 0
  for byte in val:
        for bitnumber in range(0,8):
            if ( byte ^ crc ) & 0x80 : crc = ( crc << 1 ) ^ 0x31
            else                     : crc = ( crc << 1 )
            byte = byte << 1
        crc = crc & 0xFF
  return crc


ARDUINO = 0x08
DELAY = 2
bus = SMBus(1)

print("Starting")
num = [10, 30]
num.append(CRC(num))
bus.write_block_data(ARDUINO, 0xAA, num)
print(num)

'''
bus.write_byte(ARDUINO,num[0])
print("send "+str(num[0]))
bus.write_byte(ARDUINO,num[1])
print("send "+str(num[1]))
bus.write_byte(ARDUINO,num[2])
print("send "+str(num[2]))
bus.write_byte(ARDUINO,CRC(num))
print("send "+str(hex(CRC(num))))

for i in range(0, 10):
	bus.write_byte(ARDUINO, i*10)
	print("Send "+str(i))
	sleep(DELAY)
'''

