import os
from time import sleep
import serial
import subprocess
import signal
import json
import sys
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
        print("Sending: " + msg)
        port.write(msg)
        resp = port.readline()[:-2]
        if(not (resp == "")):
            return resp
    return "None"

# Create default mission values in case
# communication with the Arduino or JSON
# file fails.
DURATION = 28800 #8 hours
START = "8:00"
FINISH = "16:00"
RETRY = 5

TIME = "TIME"
ACK = "OK"
INTERVAL = "INTERVAL"
SLEEP = "SLEEP"

# Attempt to get mission data from JSON file
try:
    with open('mission.txt') as json_data_file:
        mission = json.load(json_data_file)
    START = str(mission["start"])
    FINISH = str(mission["end"])
except Exception as e:
    print(str(e))
    
# Set communication parameters    
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=2,
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

# Send startup command to Arduino
hour,minute = START.split(":")
sTime = int(hour)*60 + int(minute)
hour,minute = FINISH.split(":")
DURATION = ((int(hour)*60 + int(minute)) - sTime) * 60
print("Recording Time: ", DURATION)
print(write( INTERVAL + '_' + str(sTime) + '_' + str(int(hour)*60 + int(minute))))
sleep(0.5)
message = write(TIME)
sleep(0.5)
port.write(ACK)
print("TIME: " + message)

# Spawn Camera.py as child process
proc = subprocess.Popen(['python','Camera.py', str(message), str(DURATION)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
print("Child PID: ",proc.pid)
sleep(1)

# Listen for Commands from Arduino
print("START")
poll = proc.poll()
while poll == None:
    poll = proc.poll()
    message = port.readline()[:-2]
    if(message != ""):
        print("GOT: " + message)
    if(message == SLEEP):
        print("Shutting down")
        port.write(ACK)
        proc.terminate()
        sleep(2)
        sys.exit()

# Tell Arduino that RPI is ready to turn off 
port.write("DONE")






