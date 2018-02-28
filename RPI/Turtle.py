import os
from time import sleep
import serial
import subprocess
import json
# run: sudo apt-get install python-serial
# disable serial login shell

###########################################
##  Function : Write                     ##
##  Continually write to Arduino after   ##
##  timeout period until RPI recieves a  ##
##  response.                            ##
###########################################
def write(msg):
    for i in range(0,RETRY):
        port.write(msg)
        resp = port.readline()[:-2]
        if(not (resp == "")):
            return resp
    return "None"

# Create default mission values in case
# communication with the Arduino or JSON
# file fails.
DURATION = 30
START = "8:00"
RETRY = 2

# Attempt to get mission data from JSON file
try:
    with open('mission.json') as json_data_file:
        mission = json.load(json_data_file)
    START = str(mission["start"])
except Exception as e:
    print(str(e))
    
# Set communication parameters    
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=10,
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)


# Send startup command to Arduino
print(str(write(START)))
message = write("TIME")
port.write("OK")
print("TIME: " + message)

# Spawn Camera.py as child process
proc = subprocess.Popen(['python','Camera.py', str(message), str(DURATION)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
# Empty stray "OK" from buffer
print(str(port.readline()[:-2]))

# Listen for Commands from Arduino
print("START")
poll = proc.poll()
while poll == None:
    poll = proc.poll()
    message = port.readline()
    if (message != ""):
        print("GOT: " + message[:-2])

# Tell Arduino that RPI is ready to turn off 
port.write("DONE")






