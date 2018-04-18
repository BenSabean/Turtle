'''
Date:    Apr 17, 2018

This is the cetral program that reads timing interval
Starts a camera program while maintaining serial connection
Parses and logs GPS data at the end of each recording day

To use serial:
# run: sudo apt-get install python-serial
# disable serial login shell in raspi-config

contact: Arthur Bondar
email:   arthur.bondar.1@gmail.com
'''

import os
from time import sleep
import serial           # serial COM library
import subprocess       # for subprocess opening
import signal           
import json             # JSON for GPS parsing
import sys              # os.system call
import RPi.GPIO as GPIO # Pi GPIO access
import logging          # lib for error logging
import locus            # lib for GPS data parsing
import json             # JSON format library
import datetime         # lib for system datetime

###########################################
##                                       ##
##              DEFINITIONS              ##
##                                       ##
###########################################

# Create default mission values in case
# communication with the Arduino or JSON
# file fails.
DURATION = 28800 #8 hours
START = "8:00"
FINISH = "16:00"
RETRY = 2
# Serial
TIME = "TIME"
ACK = "OK"
INTERVAL = "INTERVAL"
SLEEP = "SLEEP"
GPS_START = "GPS_LOG"
GPS_DUMP = "GPS_DUMP"
GPS_ERASE = "GPS_ERASE"
# Delays
SD_WAIT_S = 90
SD_UMOUNT_S = 20
# File Path
CAMERA_PATH = "/home/pi/Turtle/RPI/Camera.py"
TEMP_PATH = "/home/pi/Turtle/RPI/gps_raw.txt"
CSV_PATH = "/home/pi/Turtle/RPI/"

# Set communication parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,      
    timeout=2,          # Wait time for data in sec
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

###########################################
##                                       ##
##              MAIN                     ##
##                                       ##
###########################################

#
#   Setting Alive pin HIGH
#
GPIO.setup(16, GPIO.OUT)
GPIO.output(16, GPIO.HIGH)

#
#   USB initialization
#
# Waiting for SD card to mount properly
sleep(SD_WAIT_S)
# Unmonting USB and removing files
os.system("sudo umount /dev/sda1")
os.system("sudo rm /home/pi/Turtle/RPI/USB/*")
# Mounting USB
os.system("sudo mount /dev/sda1 /home/pi/Turtle/RPI/USB")
logging.basicConfig(filename="/home/pi/Turtle/RPI/USB/turtle.log", format="%(asctime)s %(message)s", level=logging.DEBUG)
logging.info("TURTLE CODE STARTED")

#
#   Mission file data extration
#
# Attempt to get mission data from JSON file
try:
    with open('/home/pi/Turtle/RPI/USB/mission.txt') as json_data_file:
        mission = json.load(json_data_file)
    START = str(mission["start"])
    FINISH = str(mission["end"])
except Exception as e:
    logging.debug(str(e))

# Get Start recording time
hour,minute = START.split(":")
sTime = int(hour)*60 + int(minute)
# Get End recording time
hour,minute = FINISH.split(":")
eTime = int(hour)*60 + int(minute)
# Get Video Duration
DURATION = (eTime - sTime) * 60
logging.info('INTERVAL ' + str(sTime) + '_' + str(eTime))
print("Recording Time: ", DURATION)
logging.info("Recording Time: " + str(DURATION))

#
#   Send time INTERVAL to Arduino 
#
# Format: INTERVAL_[START]_[FINISH] both times in minutes
response = write(INTERVAL + '_' + str(sTime) + '_' + str(eTime))
print(response)
sleep(1)

#
#   Send TIME commnad to Arduino
#
# Get current time from Arduino Format: YYYY-MM-DD hh:mm:ss
time = write(TIME)
print("TIME: " + time)
logging.info("TIME: " + time)
# Set system time Format: YYYY-MM-DD hh:mm:ss
os.system("sudo date -s '" + time + "'")

#
# Spawn Camera.py as child process
#
camera = subprocess.Popen(['python',CAMERA_PATH, str(DURATION)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
print("Child PID: ",camera.pid)
logging.info("Child PID: " + str(camera.pid))
sleep(1)

#
#   Main program Loop
#



#
#   Main program Loop
#
print("START LOOP") 
# Check if camera recording
poll = camera.poll()
while poll == None:

    #
    #   Check Serial
    #
    message = port.readline()[:-2]
    if(message != ""):
        print("GOT: " + message)
        logging.info("GOT: " + str(message))

    #
    #   Sleep Command received
    #
    if(message == SLEEP):
        print('GOT SLEEP')
        port.write(ACK)
        # Stop camera recording
        camera.terminate()
        sleep(1)
        logging.info("Sleep command recieved. Shutting down")
        break

    # Check if still camera recording
    poll = camera.poll()

# END LOOP

#
#   Shutdown Routine
#
# Unmounting USB
print('UNMOUNTING USB')
logging.info('EXIT TURTLE RECORDING')
# Unmount Delay
sleep(SD_UMOUNT_S)
os.system("sudo umount /dev/sda1")
print('DONE EXECUTION')
os.system("sudo shutdown -t now")


###########################################
##                                       ##
##              FUNCTIONS                ##
##                                       ##
###########################################


'''
    Writes data in a loop over serial port
    Returns response string or 'None'
'''
def write(msg):
    for i in range(0,RETRY):
        print("Sending: " + msg)
        port.write(msg)
	resp = ""
        resp = port.readline()[:-2]
        if(not (resp == "")):
            return resp
    logging.debug("Serial not responding")
    return "None"


'''
    Gets GPS raw data over serial and writes in a file
    Parses into JSON format using locus library
    Re-writes into CSV format with time stamp
'''
def getGPS():
    # Opening file for GPS storage
    file f_raw = open(TEMP_PATH, "w")
    file f_csv = open(CSV_PATH + dt.datetime.now().strftime('%Y-%m-%d') + '.csv', "w")
    # Array of characters to hold GPS bytes
    buff = []  
    buff[0] = 'X'
    buff[1] = 'X'

    logging.info("GPS-DUMP STARTED")
    # Loop to receive GPS data using rotating buffer
    while (buff[0] != 'O') and (buff[1] != 'K'):
        # Rotating buffer
        buff[0] = buff[1]
        # Receiving new character
        buff[1] = port.read()
        # Saving
        print(str(buff[1]))
        raw.write(str(buff[1]))
    # Closing temprary raw data file
    f_raw.close()

    # Parse data as JSON
    coords = locus.parseFile(TEMP_PATH)
    # filter out bad data
    coords = [c for c in coords if c.fix > 0 and c.fix < 5] 
    # Print coordinates as JSON
    json.dumps(coords, fp, cls = Encoder, sort_keys=True, indent=4)
    coord_json = json.loads(fp, cls = Encoder)

    print json.dumps(coord_json)

    logging.info("GPS-DUMP FINISHED")
    # Closing files
    f_csv.close()


'''
    Class used by Locus library for GPS parsing
    Parses raw data form a file into JSON coordinates object
'''
    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, locus.Coordinates):
                return obj.__dict__

            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%dT%H:%M:%S%z")

            return json.JSONEncoder.default(self, obj)

