import os
from time import sleep
import serial
# run: sudo apt-get install python-serial
# disable serial login shell

# Setting parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=2,
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE,
    inter_byte_timeout = None
    #parser = serialport.parsers.readline("")
)

message = "none"

while(1):
    message = "This is a very long string abcdefghijklmnopqrstuvwxyz"
    port.write(message)
    print(message)
    message = port.readline()
    if (message != ""):
        print(message[:-2])
    sleep(1)










