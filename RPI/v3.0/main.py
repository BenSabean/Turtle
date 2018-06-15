#!/usr/bin/python2

import os
from time import sleep
from timer_class import Timer # custom made class for i2c com
from parser_class import SetupFile  # custom made class to read setup file
import subprocess             # for subprocess opening
import signal
import sys                    # os.system call
import datetime               # lib for system datetime

# file path's
DUR =      5       # video duration in minutes
TEMP_FOLDER =   "/home/pi/Video/"
USB_FOLDER =     "/home/pi/USB/"
TERM_SEM =      "/home/pi/Semaphore/terminate.sem"
SETUP_FILE =    USB_FOLDER + "setup.txt"
TERM = False
camera = None
poll = 1

# Camera default paramters
PARAM = [
    'raspivid',                 # program to call                                   (param 0)
    '-t', str(1*60*1000),       # videos duration in milliseconds                   (param 2)
    '-o', TEMP_FOLDER+"noname.h264",# output file                                   (param 4)
    '-a', '12',                 # test annotations - time and date 20:09:33 10/28/15(param 6)
    '-ae', '32,0xff,0x808000',  # white test on black background                    (param 8)
    '-w', '1640',               # image width                                       (param 10)
    '-h', '1232',               # image height                                      (param 12)
    '-b', '15000000',           # bit rate, for 1080p30 15Mbits/s                   (param 14)
    '-rot', '180',              # bit rate, for 1080p30 15Mbits/s                   (param 16)
    '-fps', '30'                # frames per second                                 (param 18)
]

# File names
NEW_FILE = ""
OLD_FILE = ""
print("code started ["+datetime.datetime.now().strftime('%H:%M:%S')+"]")

# unmounting USB
#os.system("sudo umount /dev/sda1")
subprocess.check_output("sudo umount /dev/sda1", stderr=subprocess.STDOUT, shell=True)
# Removing old files
#os.system("rm "+TEMP_FOLDER+"*")
subprocess.check_output("rm "+TEMP_FOLDER+"*", stderr=subprocess.STDOUT, shell=True)
#os.system("rm "+USB_FOLDER+"*")
subprocess.check_output("rm "+USB_FOLDER+"*", stderr=subprocess.STDOUT, shell=True)
print("old files removed")
# mounting USB
print("mounting usb ...")
#os.system("sudo mount /dev/sda1 "+USB_FOLDER)
subprocess.check_output("sudo mount /dev/sda1 "+USB_FOLDER, stderr=subprocess.STDOUT, shell=True)
print("usb mounted")

# creating setup file class
setup_file = SetupFile(SETUP_FILE)
# Getting rec duration
DUR = setup_file.getRec()
print("recording time is "+str(DUR)+" min")

# -----------------------------------------------
while not TERM == True:
    # checking if recording program finished
    if not poll == None:
        # substract interval from full time
        DUR -= 1
        print("time left: "+str(DUR)+" min")
        if DUR < 0:
            print("moving file to usb ...")
            #code = os.system("sudo mv "+OLD_FILE+" "+USB_FOLDER)
            subprocess.check_output("sudo mv "+OLD_FILE+" "+USB_FOLDER, stderr=subprocess.STDOUT, shell=True)
            print("mv command finished")
            # exiting the main loop when recording duration excedeed
            break   
        # assemble filename
        NEW_FILE = TEMP_FOLDER + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".h264"
        PARAM[4] = NEW_FILE             # parameter 4 is filename
        # start new camera recording
        camera = subprocess.Popen(PARAM,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
        print("camera pid: "+str(camera.pid))
        # move old file to USB
        print("moving file to usb ...")
        #os.system("mv "+OLD_FILE+" "+USB_FOLDER)
        subprocess.check_output("sudo mv "+OLD_FILE+" "+USB_FOLDER, stderr=subprocess.STDOUT, shell=True)
        print("mv command finished")
        # updating prev file
        OLD_FILE = NEW_FILE
    # ------
    # Checking termination semaphore
    TERM = os.path.isfile(TERM_SEM) 
    if TERM == True:
        # closing current camera program
        print("killing current camera process: "+str(camera.pid))
        camera.kill()
        # move old file to USB
        print("moving file to usb ...")
        os.system("sudo mv "+OLD_FILE+" "+USB_FOLDER)
        print("file moved")

    sleep(1)
    poll = camera.poll()
# -----------------------------------------------

if TERM == True:
    print("code terminated using semaphore ["+datetime.datetime.now().strftime('%H:%M:%S')+"]")
    sys.exit()
else:
    #print("code finished ["+datetime.datetime.now().strftime('%H:%M:%S')+"]")
    s_hr, s_min = setup_file.getSleep() 
    print("sending sleep for "+str(s_hr)+"hr "+str(s_min+"min"))
    timer = Timer()
    if timer.setSleep(s_hr, s_min):
        print("sleep set succesfully")
    else:
        print("sleep failed")