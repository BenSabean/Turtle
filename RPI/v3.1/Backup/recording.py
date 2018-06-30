'''
Date:    May 19, 2018

This is a test program to record a video in 1hr section.
When one section is finished, second is started and old section 
is moved to the USB until total recording time in past

This code is used to testing long recording loops 
and USB stick thermal performace

resolution:
1920x1080 - 16:9 - 30fps - FOV:partial
1640x1232 - 4:3 - 40fps - FOV:Full
'''

import os
from time import sleep
import subprocess       # for subprocess opening
import signal
import sys              # os.system call
import RPi.GPIO as GPIO # Pi GPIO access
import datetime         # lib for system datetime

###########################################
##                                       ##
##              DEFINITIONS              ##
##                                       ##
###########################################

# Mission
DURATION = 8*60*60*1000 # 8 hours
START = "5:00"
FINISH = "19:00"
RETRY = 5
# Delays
SD_MOUNT_S = 30
SD_UMOUNT_S = 20
# Pins
REC_LIGHT = 17
RUN_LIGHT = 27
# File Path
USB_PATH = "/home/pi/USB/"
TEMP_PATH = 'home/pi/Videos/'
SEM_PATH = "home/pi/Semaphore/shutdown.sem"
LOG_FILE = USB_PATH + "turtle.log"
TERMINATE = False

# Camera default paramters
PARAM = [
    'raspivid',                 # program to call
    '-t', str(60*60*1000),      # videos duration in milliseconds
    '-o', TEMP_PATH,            # output file
    '-a', '12',                 # test annotations - time and date 20:09:33 10/28/15
    '-ae', '32,0xff,0x808000',  # white test on black background
    '-w', '1640',               # image width
    '-h', '1232',               # image height
    '-b', '15000000',           # bit rate, for 1080p30 15Mbits/s
    '-fps', '30'                # frames per second
]

# Recording LED setuip
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(REC_LIGHT, GPIO.OUT)
GPIO.setup(RUN_LIGHT, GPIO.OUT)

###########################################
##                                       ##
##              FUNCTIONS                ##
##                                       ##
###########################################

def mountUSB (path):
    print("mounting usb ...")
    os.system("sudo umount /dev/sda1")
    os.system("sudo rm " + path + "*")
    os.system("sudo mount /dev/sda1 " + path) # Mounting USB
    sleep(20) # Waiting for SD card to mount properly
    print("usb mounted")

def checkSemaphore(sem_path):




###########################################
##                                       ##
##              MAIN                     ##
##                                       ##
###########################################

#   Run Light
GPIO.output(RUN_LIGHT, GPIO.HIGH)

#   Recording parameters
try:
    DURATION = int(sys.argv[1])
except Exception as e:
    print(e)
print("recording time is "+str(DURATION))

#   USB initialization
mountUSB(USB_PATH)

#   Spawn Camera.py as child process
# python ../Camera.py DURATION (in minutes)
camera = subprocess.Popen(['python', CAMERA_PATH, str(DURATION)],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.STDOUT)
print("Child PID: ",camera.pid)

#
#   Main program Loop
# -------------------------------------------
print("recording loop started")
# Check if camera recording
poll = camera.poll()
while not TERMINATE == True:


    # Check if still camera recording
    poll = camera.poll()
# -------------------------------------------
# END LOOP


#   Shutdown Routine
#
print('unmounting usb ...')
os.system("sudo umount /dev/sda1")
sleep(SD_UMOUNT_S) # Unmount Delay
# Exiting & Shutting down
print('finished')
# os.system("sudo shutdown -t now")
sys.exit()

