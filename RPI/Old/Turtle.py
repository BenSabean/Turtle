import os
from time import sleep
import serial
import subprocess
import signal
import json
import sys
import RPi.GPIO as GPIO
import logging
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
    logging.debug("Serial not found")
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
SD_WAIT_S = 90

# Setting Alive pin HIGH
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT)
GPIO.output(16, GPIO.HIGH)

# Waiting for SD card to mount properly
sleep(SD_WAIT_S)

# Unmonting USB and removing files
os.system("sudo umount /dev/sda1")
os.system("sudo rm /home/pi/Turtle/RPI/USB/*")

# Mounting USB
os.system("sudo mount /dev/sda1 /home/pi/Turtle/RPI/USB")
logging.basicConfig(filename="/home/pi/Turtle/RPI/USB/turtle.log", format="%(asctime)s %(message)s", level=logging.DEBUG)

# Attempt to get mission data from JSON file
try:
    with open('/home/pi/Turtle/RPI/USB/mission.txt') as json_data_file:
        mission = json.load(json_data_file)
    START = str(mission["start"])
    FINISH = str(mission["end"])
except Exception as e:
    logging.debug(str(e))

# Set communication parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=74880,
    timeout=2,
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

logging.info("TURTLE CODE STARTED")

# Send startup command to Arduino
# Get Start recording time
hour,minute = START.split(":")
sTime = int(hour)*60 + int(minute)
# Get End recording time
hour,minute = FINISH.split(":")
eTime = int(hour)*60 + int(minute)
# Get Video Duration
DURATION = (eTime - sTime) * 60
print("Recording Time: ", DURATION)
logging.info("Recording Time: " + str(DURATION))
logging.info('INTERVAL ' + str(sTime) + '_' + str(eTime))
# Send time Interval to Arduino
print( write(INTERVAL + '_' + str(sTime) + '_' + str(eTime)) )
sleep(1)
# Get current time from Arduino
message = write(TIME)
sleep(1)
port.write(ACK)
print("TIME: " + message)
logging.info("TIME: " + message)

# Spawn Camera.py as child process
proc = subprocess.Popen(['python','/home/pi/Turtle/RPI/Camera.py', str(message), str(DURATION)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
print("Child PID: ",proc.pid)
logging.info("Child PID: " + str(proc.pid))
sleep(1)

# Listen for Commands from Arduino
print("START")
logging.info("Listening for commands from controller")
poll = proc.poll()
while poll == None:
    poll = proc.poll()
    message = port.readline()[:-2]
    if(message != ""):
        print("GOT: " + message)
        logging.info("GOT: " + str(message))
    if(message == SLEEP):
        print("Shutting down")
        port.write(ACK)
        proc.terminate()
        sleep(2)
	print('GOT SLEEP DONE RECORDING')
        logging.info("Sleep command recieved. Shutting down")
        #os.system("sudo shutdown -h now")
        #os.system("python /home/pi/Turtle/RPI/off.py")
        sys.exit()

# Tell Arduino that RPI is ready to turn off
#os.system("sudo shutdown -h now")
port.write("DONE")
logging.info('EXIT TURTLE RECORDING')







