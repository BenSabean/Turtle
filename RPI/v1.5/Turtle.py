'''
Date:    Apr 23, 2018

This is the cetral program that reads timing interval
Starts a camera program while maintaining serial connection
GPS avaible using the commands and will record position during the day

To use serial:
# run: sudo apt-get install python-serial
# disable serial login shell in raspi-config
# ? Change usb interface in config ?

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
DURATION = 3*60*60  # Mission duration default 3 days - 10800 minutes
REC_TIME = 10*60*60 # Camera timings default 10 hours per day - 36000
GPS_INTERVAL = 2*60 # Interval to get gps data in seconds 120
PARAM_INTERVAL = 5*60 # Interval for logging mission paramters
START = "5:00"
FINISH = "19:00"
RETRY = 5
# Serial
TIME = "TIME"
ACK = "OK"
INTERVAL = "INTERVAL"
SLEEP = "SLEEP"
GPS = "GPS"
PARAM = "PARAM"
# Delays
SD_MOUNT_S = 30
SD_UMOUNT_S = 20
# File Path
USB_PATH = "/home/pi/Turtle/RPI/USB/"
CAMERA_PATH = "/home/pi/Turtle/RPI/Camera.py"
# Need to be changes to .mission.json
MISSION_FILE = USB_PATH + "mission.txt"
LOG_FILE = USB_PATH + "turtle.log"

# Set communication parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=19200,
    timeout=2,          # Wait time for data in sec
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
    Return: response or 'None'
'''
def serial_send(msg):
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
        if not (resp == ""):
            return resp
    # no response after all retries
    logging.debug("WARNING: Serial not responding")
    return "None"

'''
    Takes a file pointer and data string from GPS
    Parses the data line and writes into CSV file
    String Format: [Fix]_[Quality]_[Long]_[Lat]_[Speed]_[Angle]
'''
def parse_GPS(_file, _str):
    # Writing time stamp
    _file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # Splitting data
    arr = _str.split("_")
    # Writing in sequence
    for element in arr:
        _file.write(',' + element)
    # End of data line
    _file.write('\n')


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
sleep(10)
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
    DURATION = str(mission["duration"])
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
REC_TIME = (eTime - sTime) * 60
# Assembeling interval command
Interval = 'INTERVAL_' + str(sTime) +'_'+ str(eTime) +'_'+ str(DURATION)
logging.info(Interval)
logging.info("Recording Time: " + str(REC_TIME))
print("Recording Time: ", REC_TIME)

#
#   Send time INTERVAL to Arduino
#
# Format: INTERVAL_[START]_[FINISH]_[DURATION] both times in minutes
response = serial_send(Interval)
# Retry 1
if not response == ACK:
    serial_send(Interval)
sleep(1)

#
#   Send TIME commnad to Arduino
#
response = serial_send(TIME)
# If valid time received
# Set system time Format: YYYY-MM-DD hh:mm:ss
if not (response == "None"):
    os.system("sudo date -s '" +response+ "'")

#
#   Spawn Camera.py as child process
#
# python ../Camera.py DURATION (in minutes)
camera = subprocess.Popen(['python', CAMERA_PATH, str(REC_TIME)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
print("Child PID: ",camera.pid)
logging.info("Child PID: " + str(camera.pid))
sleep(1)

#
#   Opening CSV file for GPS data recording
#
# CSV file named using the current date
CSV_FILE = USB_PATH + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv'
f_csv = open(CSV_FILE, "w")
# Printing headers
f_csv.write("Timestamp,Fix,Quality,Longitute,Latitude,Speed,Angle\n")

#
#   Main program Loop
#
print(" -- START LOOP -- ")
# Start timing loop to retrieve GPS data
timer1 = datetime.datetime.now()
timer2 = datetime.datetime.now()
# Check if camera recording
poll = camera.poll()
while poll == None:

    #   Check Serial
    message = port.readline()[:-2]

    #
    #   get GPS data every 2 minutes
    #
    if((datetime.datetime.now() - timer1).seconds > GPS_INTERVAL):
        response = serial_send(GPS)     # send GPS command
        if not response == "None":
            parse_GPS(f_csv, response)  # parse and write to file
        timer1 = datetime.datetime.now() # reset timer

    #
    #   Log mission parameters every 5 minutes
    #
    if((datetime.datetime.now() - timer2).seconds > PARAM_INTERVAL):
        response = serial_send(GPS)     # send GPS command
        if not response == "None":
            arr = response.split("_")
            if len(arr) == 6:
                logging.info("Mission -> start: " +arr[0]+ " now: " +arr[1]+ " end: " +arr[2])
                logging.info("Timer   -> timer: " +arr[3]+ " duration: " +arr[4])
                logging.info("Battery Voltage: " +arr[5])
        timer2 = datetime.datetime.now() # reset timer

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
        break

    # Check if still camera recording
    poll = camera.poll()
#
# END LOOP

#
#   Shutdown Routine
#
f_csv.close()
# Unmounting USB
print('UNMOUNTING USB')
os.system("sudo umount /dev/sda1")
sleep(SD_UMOUNT_S) # Unmount Delay
# Exiting & Shutting down
logging.info('EXIT TURTLE RECORDING')
print('EXIT TURTLE RECORDING')
# os.system("sudo shutdown -t now")
sys.exit()
