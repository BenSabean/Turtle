#!/usr/bin/python2

import os                           # os.system call
from time import sleep              # sleep function in seconds
from timer_class import Timer       # custom made class for i2c com
from parser_class import SetupFile  # custom made class to read setup file
from led_class import Gpio_class    # custom made class to switch led's
from log_class import LogClass      # custom made class to log program status
from gps_class import GPS_class     # custom made class for gps readings
import subprocess                   # for subprocess opening
import signal                       # not sure what that is for
import sys                         
import datetime                     # lib for system datetime

# Definitions
DUR =               5               # video duration in minutes
VIDEO_SECTION =     2               # video sections duration
TEMP_FOLDER =       "/home/pi/Video/"
USB_FOLDER =        "/home/pi/USB/"
TERM_SEM =          "/home/pi/semaphore/terminate.sem"
SETUP_FILE =        USB_FOLDER + "setup.txt"
LOG_FILE =          USB_FOLDER + "log.txt"
# Global Variables
TERM = False
camera = None
poll = 1
NEW_FILE = ""
OLD_FILE = ""
# Camera default paramters
PARAM = [
    'raspivid',                 # program to call                                   (param 0)
    '-t', str(VIDEO_SECTION*60*1000),# videos duration in milliseconds              (param 2)
    '-o', TEMP_FOLDER+"noname.h264",# output file                                   (param 4)
    '-a', '12',                 # test annotations - time and date 20:09:33 10/28/15(param 6)
    '-ae', '32,0xff,0x808000',  # white test on black background                    (param 8)
    '-w', '1640',               # image width   1920x1080-16:9-30fps-FOV:partial    (param 10)
    '-h', '1232',               # image height  1640x1232-4:3-40fps-FOV:Full        (param 12)
    '-b', '15000000',           # bit rate, for 1080p30 15Mbits/s                   (param 14)
    '-rot', '180',              # bit rate, for 1080p30 15Mbits/s                   (param 16)
    '-fps', '30'                # frames per second                                 (param 18)
]

# move video file from Pi SD to USB
# uses cp and rm since mv cannot preserve permitions
def move(old_path, new_path):
    os.system("sudo cp "+OLD_FILE+" "+USB_FOLDER)
    os.system("sudo rm "+OLD_FILE)
    
# Objects
log = LogClass(LOG_FILE)            # Log file object
timer = Timer()                     # Arduino COM object
setup_file = SetupFile(SETUP_FILE)  # Setup file object
io = Gpio_class()                   # GPIO class (switch,led,alive)
io.clear()

# unmounting USB
os.system("sudo umount /dev/sda1")
# Removing old files
os.system("sudo rm "+TEMP_FOLDER+"*")
os.system("sudo rm "+USB_FOLDER+"*")
# mounting USB
os.system("sudo mount /dev/sda1 "+USB_FOLDER)

# GPS object
gps = GPS_class(USB_FOLDER)
gps.setTime()

log.write("START")
io.blink(10)                         # indicate beginning of the code
# getting full deployment duration and sending to arduino
# checking if release time has been set
flag = timer.checkStatus()
if flag[1] == 0:
    # parsing release time from file
    time = []*2
    time = setup_file.getParam("release")
    log.write("setting release time for: "+str(time[0])+"hr "+str(time[1])+"min")
    try:
        if not time == 0: 
            resp = timer.setRelease(time[0], time[1])
            if resp == True: log.write("release time set succesfully")
            else:            log.write("release time set failed")
    except Exception as exp:
        log.write(str(exp))
        pass
    
# getting recording duration
REC_DUR = setup_file.getParam("recording")
log.write("recording time is "+str(REC_DUR)+" min")
# getting video sections
section = setup_file.getParam("sections")
if section > 0 and section <= 720: VIDEO_SECTION = section
log.write("recording sections "+str(VIDEO_SECTION)+" min")
# video width
width = setup_file.getParam("width")
if width > 0 and width <= 3280: PARAM[10] = str(width)
# video height
height = setup_file.getParam("height")
if height > 0 and height <= 2464: PARAM[12] = str(height)
# frames per second
fps = setup_file.getParam("fps")
if fps > 0 and fps <= 90: PARAM[18] = str(fps)
# camera rotation
rot = setup_file.getParam("rotation")
if rot > 0 and rot <= 360: PARAM[16] = str(rot)

# -----------------------------------------------
while REC_DUR > 0 or poll == None:
    # checking if recording program finished
    if not poll == None:
        io.setRun()
        # substract interval from recording time
        REC_DUR -= VIDEO_SECTION
        log.write("time left: "+str(DUR)+" min")
        # assemble filename
        NEW_FILE = TEMP_FOLDER + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".h264"
        PARAM[4] = NEW_FILE             # parameter 4 is filename
        # start new camera recording
        camera = subprocess.Popen(PARAM,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
        log.write("camera pid: "+str(camera.pid))
        # move old file to USB
        log.write("moving file to usb ...")
        move(OLD_FILE, USB_FOLDER)
        log.write("file moved")
        # updating prev file
        OLD_FILE = NEW_FILE
    # ------

    # Checking termination semaphore
    #TERM = io.checkSwitch()
    TERM = False
    if TERM == True:
        # closing current camera program
        log.write("killing current camera process: "+str(camera.pid))
        camera.kill()
        break   # exiting the main loop when switch pulled low

    io.setRec()
    log.write(gps.writeCSV())
    sleep(1)
    poll = camera.poll()
# -----------------------------------------------

# moving the last file to USB
log.write("moving file to usb ...")
move(OLD_FILE, USB_FOLDER)
log.write("file moved")

if TERM == True:
    log.write("code terminated using semaphore")
else:
    # Setting Sleep time for Arduino
    s_hr, s_min = setup_file.getParam("sleep") 
    log.write("recording finished, sleep for "+str(s_hr)+"hr "+str(s_min)+"min")
    if timer.setSleep(s_hr, s_min):
        log.write("sleep set succesfully")
    else:
        log.write("sleep failed")

io.blink(10)         # indicate code termination
io.clear()          # turn off both LED's
quit()