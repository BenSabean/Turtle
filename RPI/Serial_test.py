import os
from time import sleep
import serial                   
# run: sudo apt-get install python-serial
# disable serial login shell

# Setting parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=5,
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

message = "none"

while(1):
    message = "Send stuff Now"
    port.write(message)
    message = port.readline()
    if (message != ""):
        print(message[:-2])










