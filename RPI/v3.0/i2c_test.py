#!/usr/bin/python2

#
# I2C function sends data in the following format:
# 1. Register (2nd parameter in func)
# 2. Message lenght 
# 3. Byte array
#


from smbus import SMBus
from time import sleep
import RPi.GPIO as GPIO
import sys

# Functions
# Calculating CRC for a number of bytes #
def CRC(val):
  crc = 0
  for byte in val:
        for bitnumber in range(0,8):
            if ( byte ^ crc ) & 0x80 : crc = ( crc << 1 ) ^ 0x31
            else                     : crc = ( crc << 1 )
            byte = byte << 1
        crc = crc & 0xFF
  return crc

# Definitions
ARDUINO = 0x05
SLEEP_CMD = 0x01
RELEASE_CMD = 0x01
CHECK_CMD = 0xAA
ALIVE = 17

# Setting Alive pin HIGH
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ALIVE, GPIO.OUT)
GPIO.output(ALIVE, GPIO.HIGH)

# i2c bus
bus = SMBus(1)

print("Starting")
msg = [0, 2]
msg.append(CRC(msg))
bus.write_block_data(ARDUINO, SLEEP_CMD, msg)
print("Sent: ", msg)

sleep(2)
print("Sent: ", CHECK_CMD)
resp = bus.read_block_data(ARDUINO, CHECK_CMD)
try:
  print("Got: "+str(resp[0])+str(resp[1]))
except Exception as e:
  print e


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

