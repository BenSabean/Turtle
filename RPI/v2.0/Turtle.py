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

# Mission
DURATION = 50400 # 8 hours
START = "5:00"
FINISH = "19:00"
RETRY = 4
# Serial
TIME = "TIME"
ACK = "OK"
INTERVAL = "INTERVAL"
SLEEP = "SLEEP"
GPS_LOG = "GPS_LOG"
GPS_DUMP = "GPS_DUMP"
GPS_ERASE = "GPS_ERASE"
# Delays
SD_WAIT_S = 80
SD_UMOUNT_S = 20
# File Path
CAMERA_PATH = "/home/pi/Turtle/RPI/Camera.py"
TEMP_PATH = "/home/pi/Turtle/RPI/USB/gps_raw.txt"
CSV_PATH = "/home/pi/Turtle/RPI/USB/"
HEADERS_PRINTED = False
USB_PATH = "/home/pi/Turtle/RPI/USB"
LOG_PATH = "/home/pi/Turtle/RPI/USB/turtle.log"
# Need to be changes to .mission.json
MISSION_PATH = "/home/pi/Turtle/RPI/USB/mission.txt"

# Set communication parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=19200,
    timeout=3,          # Wait time for data in sec
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT)


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
    global HEADERS_PRINTED
    # wrties twice to the same file 1. at start 2. after sleep
    f_csv = open(CSV_PATH + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv', "a")
    # Opening file for GPS storage
    f_raw = open(TEMP_PATH, "w")

    #
    #   Getting raw GPS data
    #
    # Array of characters to hold GPS bytes
    buff = []
    buff.append('X')
    buff.append('X')
    logging.info("GPS-DUMP STARTED")
    print("GPS-DUMP STARTED")
    # Flushing serial buffer
    port.readline()
    # Send Start Dump log command
    port.write(GPS_DUMP)
    # Breaks from loop after 3 minutes
    start = datetime.datetime.now()
    # Loop to receive GPS data using shift register
    while not ((buff[0] == 'O') and (buff[1] == 'K')):
        # Rotating buffer
        buff[0] = buff[1]
        # Receiving new character
        buff[1] = port.read()
        #if not (buff[1] == ""):
	#	print("%c" % buff[1])
        # Saving
        f_raw.write(buff[1])
	if (datetime.datetime.now() - start).seconds > (3*60):
		logging.info("GPS-DUMP TIMEOUT OCCURED")
		print("GPS-DUMP TIMEOUT OCCURED")
		break

    # Closing temprary raw data file
    f_raw.close()

    #
    #   Parsing
    #
    print("PARSING TO CSV")
    # Parse data as JSOM
    coords = locus.parseFile(TEMP_PATH)
    # filter out bad data
    coords = [c for c in coords if c.fix > 0 and c.fix < 5]
    # Printing into CSV file
    # Headers
    if not (HEADERS_PRINTED == True):
        f_csv.write("Timestamp,Satellite Fix,Latitude,Longitude,Altitude\n")
        HEADERS_PRINTED = True
    # Lines
    for c in coords:
        line = str(c.datetime) +","+ str(c.fix) +","+ str(c.latitude) +","+ str(c.longitude) +","+ str(c.height) +"\n"
        f_csv.write(line)
        # print(line)

    # Closing files
    logging.info("GPS-DUMP FINISHED")
    print("GPS-DUMP FINISHED")
    f_csv.close()
    # Starting new Log
    write(GPS_ERASE)
    sleep(1)
    write(GPS_LOG)


###########################################
##                                       ##
##              MAIN                     ##
##                                       ##
###########################################

#
#   Setting Alive pin HIGH
#
GPIO.output(16, GPIO.HIGH)

#
#   USB initialization
#
# Waiting for SD card to mount properly
sleep(SD_WAIT_S)
# Unmonting USB and removing files
os.system("sudo umount /dev/sda1")
sleep(5)
os.system("sudo rm " + USB_PATH + "/*")
# Mounting USB
os.system("sudo mount /dev/sda1 " + USB_PATH)
logging.basicConfig(filename= LOG_PATH, format="%(asctime)s %(message)s", level=logging.DEBUG)
logging.info("TURTLE CODE STARTED")
print("TURTLE CODE STARTED")

#
#   Mission file data extration
#
# Attempt to get mission data from JSON file
try:
    with open( MISSION_PATH ) as json_data_file:
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
logging.info('INTERVAL_' + str(sTime) + '_' + str(eTime))
logging.info("Recording Time: " + str(DURATION))
print("Recording Time: ", DURATION)

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
#   Spawn Camera.py as child process
#
camera = subprocess.Popen(['python', CAMERA_PATH, str(DURATION)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
print("Child PID: ",camera.pid)
logging.info("Child PID: " + str(camera.pid))
sleep(1)

#
#   Get GPS data and start new log
#
getGPS()

#
#   Main program Loop
#
print("START LOOP")
# Check if camera recording
# poll = camera.poll()
poll = None
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
        # Starting second GPS log
	getGPS()
        logging.info("Sleep command recieved. Shutting down")
        break

    # Check if still camera recording
    #poll = camera.poll()
#
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
# os.system("sudo shutdown -t now")

