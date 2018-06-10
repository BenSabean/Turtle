#!/usr/bin/python2

#
# I2C function sends data in the following format:
# 1. Register (2nd parameter in func)
# 2. Message lenght 
# 3. Byte array
#


#from smbus import SMBus
from time import sleep
import RPi.GPIO as GPIO
import sys
from smbus2 import SMBusWrapper, i2c_msg,  SMBus

# Functions

# Definitions
ARDUINO = 0x05
SLEEP_CMD = 0x01
RELEASE_CMD = 0x02
CHECK_CMD = 0xAA
ALIVE = 17

# Setting Alive pin HIGH
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ALIVE, GPIO.OUT)
GPIO.output(ALIVE, GPIO.HIGH)

# i2c bus
# Single transaction writing two bytes then read two at address 80
with SMBusWrapper(1) as bus:
    print bus.read_i2c_block_data(ARDUINO, CHECK_CMD, 2)
    sleep(3)
    print "Send release for 2 min"
    bus.write_i2c_block_data(ARDUINO, SLEEP_CMD, [0,2])
    sleep(3)
    print bus.read_i2c_block_data(ARDUINO, CHECK_CMD, 2)
    sleep(3)
    print "Send sleep for 2 min"
    bus.write_i2c_block_data(ARDUINO, RELEASE_CMD, [0,2])
    sleep(3)
    print bus.read_i2c_block_data(ARDUINO, CHECK_CMD, 2)
    sleep(10)
    print "ALIVE pin = Low"
    GPIO.output(ALIVE, GPIO.LOW)

'''
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