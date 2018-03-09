import os
from time import sleep
import serial
import subprocess
import signal
import json
import sys
import RPi.GPIO as GPIO
import datetime as dt
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
LOG = "Turtle.log"
PATH = "/home/pi/Turtle/RPI/"
# Commands
TIME = "TIME"
ACK = "OK"
INTERVAL = "INTERVAL"
SLEEP = "SLEEP"

# Setting alive pin to signal Waking up
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT)
GPIO.output(16, GPIO.HIGH)

# Set communication parameters    
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=57600,
    timeout=2,
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

# Waiting for system to fully boot
sleep(90)

# Unmounting USB and removing cleaning files
os.system("sudo umount /dev/sda1")
os.system("sudo rm " + PATH + "USB/*")

# Attempt to get mission data from JSON file
try:
    with open(PATH + 'USB/mission.txt') as json_data_file:
        mission = json.load(json_data_file)
        START = str(mission["start"])
        FINISH = str(mission["end"])
# Log error on failure
except Exception as e:
    print(str(e))
    log = open(PATH + LOG, "a")
    log.write(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " -> Cannot read mission file\n")
    log.close()
    
# Getting Start - End times
hour,minute = START.split(":")
startMin = int(hour)*60 + int(minute)
hour,minute = FINISH.split(":")
endMin = int(hour)*60 + int(minute)

# Calculating video duration
DURATION = (startMin - endMin) * 60
print("Recording Time: ", DURATION)

# Sending Recording intervals to Arduino
print(write(INTERVAL + '_' + str(startMin) + '_' + str(endMin))
sleep(0.5)

# Sending Time to Arduino
message = write(TIME)
sleep(0.5)
port.write(ACK)

# If Arduino Failed to send us time
if message == "None":
    message = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
print("TIME: " + message)

# Spawn Camera.py as child process
proc = subprocess.Popen(['python', PATH + 'Camera.py', str(message), str(DURATION)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
print("Child PID: ",proc.pid)
sleep(1)

# Listen for Commands from Arduino
print("STARTING LOOP")
poll = proc.poll()
while poll == None:
    poll = proc.poll()
    message = ""
    message = port.readline()[:-2]
    if(message != ""):
        print("GOT: " + message)
    if(message == SLEEP):
        port.write(ACK)
        print("Shutting down")
        proc.terminate()
        sleep(2)
        #os.system("sudo shutdown -h now")
        os.system("python " + PATH + "off.py")
        sys.exit()

# Tell Arduino that RPI is ready to turn off 
port.write("DONE")






