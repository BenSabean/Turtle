'''
Date:    Apr 23, 2018

This is the cetral program that reads timing interval
Starts a camera program while maintaining serial connection
GPS avaible using the commands and will record position during the day

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
RETRY = 5
# Serial
TIME = "TIME"
ACK = "OK"
INTERVAL = "INTERVAL"
SLEEP = "SLEEP"
GPS = "GPS"
# Delays
SD_MOUNT_S = 30
SD_UMOUNT_S = 20
# File Path
USB_PATH = "/home/pi/Turtle/RPI/USB/"
CAMERA_PATH = "/home/pi/Turtle/RPI/Camera.py"
# Need to be changes to .mission.json
MISSION_FILE = USB_PATH + "mission.txt"
LOG_FILE = USB_PATH + "turtle.log"
TEMP_FILE = USB_PATH + "gps_raw.txt"
HEADERS_PRINTED = False

# Set communication parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=19200,
    timeout=1,          # Wait time for data in sec
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
    Sends message in a loop over serial port
    If response not equal OK, resends again
    Return: True - got OK, False didnot get OK
'''
def write(msg):
    for i in range(0,RETRY):
        print("[" + str(i) + "] Sending: " + msg)
        # Flushing the buffer once
        if i == 0:
            port.readline()
        # Sending command
        port.write(msg)
        # Getting response
        resp = port.readline()[:-2]
        # Returning response
        if resp == "OK":
            return True
    # no response after all retries
    logging.debug("WARNING: Serial not responding")
    return False


'''
    Gets GPS raw data over serial and writes in a file
    Parses into JSON format using locus library
    Re-writes into CSV format with time stamp
'''
def getGPS():
    # Variable to indicate when file headers been printed
    global HEADERS_PRINTED
    # CSV file named using the current date
    CSV_FILE = USB_PATH + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv'
    # wrties twice to the same file 1. at start 2. after sleep
    f_csv = open(CSV_FILE, "a")
    # Opening file for GPS storage
    f_raw = open(TEMP_FILE, "w")

    #
    #   Getting raw GPS data
    #
    # Array of characters to hold GPS bytes, two bytes at a time
    buff = []
    buff.append('X')
    buff.append('X')
    logging.info("GPS-DUMP STARTED")
    print("GPS-DUMP STARTED")
    # Send Start Dump log command
    write(GPS_DUMP)
    # Breaks from loop after 3 minutes
    start = datetime.datetime.now()
    # Loop to receive GPS data using shift register
    # When OK signal received, loop exits
    while not ((buff[0] == 'O') and (buff[1] == 'K')):
        # Shifting buffer
        buff[0] = buff[1]
        # Receiving new character
        buff[1] = port.read()
        #if not (buff[1] == ""):
	    #print("%c" % buff[1])
        # Saving
        f_raw.write(buff[1])
        # After 3 minutes, loop exits automatically
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
    coords = locus.parseFile(MISSION_FILE)
    # filter out bad data
    coords = [c for c in coords if c.fix > 0 and c.fix < 5]
    # Printing into CSV file
    # Headers
    if not (HEADERS_PRINTED == True):
        f_csv.write("Timestamp,Satellite Fix,Latitude,Longitude\n")
        HEADERS_PRINTED = True
    # Lines
    for c in coords:
        line = str(c.datetime) +","+ str(c.fix) +","+ str(c.latitude) +","+ str(c.longitude) +"\n"
        f_csv.write(line)
        # print(line)

    # Closing CSV file
    f_csv.close()
    logging.info("GPS-DUMP FINISHED")
    print("GPS-DUMP FINISHED")

    # Starting new Log
    write(GPS_ERASE)
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

# Unmonting USB and removing files
os.system("sudo umount /dev/sda1")
sleep(SD_UMOUNT_S)
os.system("sudo rm " + USB_PATH + "*")
# Mounting USB
os.system("sudo mount /dev/sda1 " + USB_PATH)
# Waiting for SD card to mount properly
sleep(SD_MOUNT_S)
logging.basicConfig(filename= LOG_FILE, format="%(asctime)s %(message)s", level=logging.DEBUG)
logging.info("TURTLE CODE STARTED")
print("TURTLE CODE STARTED")

#
#   Mission file data extration
#
# Attempt to get mission data from JSON file
try:
    with open( USB_PATH + "mission.txt" ) as json_data_file:
        mission = json.load(json_data_file)
    START = str(mission["start"])
    FINISH = str(mission["end"])
except Exception as e:
    logging.debug(str(e))

#
#   Mission data parsing
#
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
write(INTERVAL + '_' + str(sTime) + '_' + str(eTime))
sleep(1)

#
#   Send TIME commnad to Arduino
#
# Get current time from Arduino Format: YYYY-MM-DD hh:mm:ss
for i in range(0,RETRY):
    # Flushing the buffer once
    if i == 0:
        port.readline()
    # Sending TIME
    port.write(TIME)
    time = port.readline()[:-2]
    print("[" +str(i)+ "] TIME: " + time)
    logging.info("[" +str(i)+ "] TIME: " + time)
    # If valid time received
    if not (time == ""):
        # Set system time Format: YYYY-MM-DD hh:mm:ss
        os.system("sudo date -s '" + time + "'")
        break

#
#   Spawn Camera.py as child process
#
# python ../Camera.py DURATION (in minutes)
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
print(" -- START LOOP -- ")
# Check if camera recording
poll = camera.poll()
message = ""
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
        print("Sleep command recieved.")
        logging.info("Sleep command recieved.")
        # Returning Acknowledgement
        port.write(ACK)
        # Stop camera recording
        camera.terminate()
        # Starting second GPS log
	    getGPS()
        break

    # Check if still camera recording
    poll = camera.poll()
#
# END LOOP


#
#   Shutdown Routine
#
# Unmounting USB
print('UNMOUNTING USB')
os.system("sudo umount /dev/sda1")
sleep(SD_UMOUNT_S) # Unmount Delay
# Exiting & Shutting down
logging.info('EXIT TURTLE RECORDING')
print('EXIT TURTLE RECORDING')
# os.system("sudo shutdown -t now")
sys.exit()

