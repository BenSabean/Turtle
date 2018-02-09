import os
from time import sleep
import serial                   
# run: sudo apt-get install python-serial
# disable serial login shell

# Setting parameters
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)


while(message != "EXIT"):
    message = "none"
    message = port.readline()
    if (message != "none"):
        print(message)
    message = raw_input()
    port.write(message)









