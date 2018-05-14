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
import json             # JSON for GPS parsing
import sys              # os.system call
import RPi.GPIO as GPIO # Pi GPIO access
import logging          # lib for error logging
import datetime         # lib for system datetime
import picamera         # for camera recording

###########################################
##                                       ##
##              DEFINITIONS              ##
##                                       ##
###########################################

# Mission
REC_TIME = 10*60*60     # Camera timings default 10 hours per day - 36000 sec
GPS_INTERVAL = 2*60     # Interval to get gps data in seconds - 120
PARAM_INTERVAL = 2*60   # Interval for logging mission paramters in sec - 60
CAMERA_FAILED = False
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
# Need to be changes to .mission.json
MISSION_FILE = USB_PATH + ".mission.json"
LOG_FILE = "/home/pi/Turtle/RPI/turtle.log"

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
GPIO.setup(18, GPIO.OUT)

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
    print("WARNING: Serial not responding")
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
GPIO.output(18, GPIO.HIGH)

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
    with open( MISSION_FILE ) as json_data_file:
        mission = json.load(json_data_file)
    START = str(mission["start"])
    FINISH = str(mission["end"])
except Exception as e:
    print(str(e))
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
Interval = 'INTERVAL_' + str(sTime) +'_'+ str(eTime)
logging.info(Interval)
logging.info("Recording Time: " + str(REC_TIME))
print(Interval)
print("Recording Time: ", REC_TIME)

#
#   Send time INTERVAL to Arduino
#
port.readline()     # flush buffer
# Format: INTERVAL_[START]_[FINISH] both times in minutes
response = serial_send(Interval)
# Retry 1
if not response == ACK:
    response == serial_send(Interval)
sleep(0.5)
if not response == ACK:
    serial_send(Interval)
sleep(0.5)

#
#   Send TIME commnad to Arduino
#
port.readline() # flushing the buffer
response = serial_send(TIME)
# If valid time received
# Set system time Format: YYYY-MM-DD hh:mm:ss
if not (response == "None"):
    os.system("sudo date -s '" +response+ "'")

#
#   Opening CSV file for GPS data recording
#
# CSV file named using the current date
CSV_FILE = USB_PATH + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv'
f_csv = open(CSV_FILE, "w")
# Printing headers
f_csv.write("Timestamp,Fix,Quality,Longitute,Latitude,Speed,Angle\n")
# Closing file
f_csv.close()

#
#   CAMERA SETUP
#
camera = picamera.PiCamera()
try:
    #   Camera Initialization
    camera.resolution = (1640, 922) # (1280x720)fullFoV (1640x922)16:9
    camera.framerate = 25
    camera.rotation = 180
    # Text frame parameters
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Output file for saving
    camera.start_recording(USB_PATH + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.h264')
    logging.info('CAMERA RECORDING STARTED')
    print('CAMERA RECORDING STARTED')
except Exception as e:
    logging.debug(str(e))
    print(str(e))
    CAMERA_FAILED = True

#
#   Main program Loop
#
print(" -- START LOOP -- ")
# Start timing loop to retrieve GPS data
timer1 = datetime.datetime.now()
timer2 = datetime.datetime.now()
# Camera timing
start = datetime.datetime.now()
while (datetime.datetime.now() - start).seconds < REC_TIME:

    #   Check Serial
    message = port.readline()[:-2]

    #
    #   get GPS data every number of minutes
    #
    if((datetime.datetime.now() - timer1).seconds > GPS_INTERVAL):
        response = serial_send(GPS)     # send GPS command
        if not response == "None":
            f_csv = open(CSV_FILE, "a")
            parse_GPS(f_csv, response)  # parse and write to file
            f_csv.close()
        timer1 = datetime.datetime.now() # reset timer

    #
    #   Log mission parameters every number of minutes
    #
    if((datetime.datetime.now() - timer2).seconds > PARAM_INTERVAL):
        response = serial_send(PARAM)     # send GPS command
        if not response == "None":
            arr = response.split("_")
            if len(arr) == 3:
                print("Start: " +arr[0]+ " Now: " +arr[1]+ " End: " +arr[2])
                logging.info("Start: " +arr[0]+ " Now: " +arr[1]+ " End: " +arr[2])
        timer2 = datetime.datetime.now() # reset timer

    #
    #   Sleep Command received
    #
    if(message == SLEEP):
        print("Sleep command recieved.")
        logging.info("Sleep command recieved.")
        # Returning Acknowledgement
        port.write(ACK)
        break

    # Update Timer on the screen
    if CAMERA_FAILED == False:
        camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
# END LOOP

#
#   Shutdown Routine
#
# Finish recording
if CAMERA_FAILED == False:
    print("CAMERA RECORDING FINISHED")
    logging.info("CAMERA RECORDING FINISHED")
    camera.stop_recording()
    camera.close()
logging.info("EXIT MAIN CODE")
# Coping log file
os.system("cp "+LOG_FILE+" "+USB_PATH)
# Unmounting USB
print('UNMOUNTING USB')
sleep(SD_UMOUNT_S)
os.system("sudo umount /dev/sda1")
# Exiting & Shutting down
print('EXIT MAIN CODE')
os.system("sudo shutdown -t now")
