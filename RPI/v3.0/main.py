import os
from time import sleep
import subprocess       # for subprocess opening
import signal
import sys              # os.system call
import datetime         # lib for system datetime

# file path's
DUR =      5       # video duration in minutes
TEMP_FOLDER =   "/home/pi/Video/"
USB_FOLDER =     "/home/pi/USB/"
TERM_SEM =      "/home/pi/Semaphore/terminate.sem"
TERM = False
camera = None
poll = 1

# Camera default paramters
PARAM = [
    'raspivid',                 # program to call
    '-t', str(1*60*1000),       # videos duration in milliseconds
    '-o', TEMP_FOLDER+"noname.h264",# output file
    '-a', '12',                 # test annotations - time and date 20:09:33 10/28/15
    '-ae', '32,0xff,0x808000',  # white test on black background
    '-w', '1640',               # image width
    '-h', '1232',               # image height
    '-b', '15000000',           # bit rate, for 1080p30 15Mbits/s
    '-rot', '180',           # bit rate, for 1080p30 15Mbits/s
    '-fps', '30'                # frames per second
]

# File names
NEW_FILE = ""
OLD_FILE = ""
print("code started ["+datetime.datetime.now().strftime('%H:%M:%S')+"]")

# unmounting USB
os.system("sudo umount /dev/sda1")
# Removing old files
os.system("rm "+TEMP_FOLDER+"*")
os.system("rm "+USB_FOLDER+"*")
print("old files removed")
# mounting USB
print("mounting usb ...")
os.system("sudo mount /dev/sda1 "+USB_FOLDER)
print("usb mounted")

#   Recording parameters
try:
    DUR = int(sys.argv[1])
except Exception as e:
    print("parameter not provided")
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
            os.system("sudo mv "+OLD_FILE+" "+USB_FOLDER)
            print("file moved")
            break
        # assemble filename
        NEW_FILE = TEMP_FOLDER + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".h264"
        PARAM[4] = NEW_FILE
        # start new camera recording
        camera = subprocess.Popen(PARAM,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
        print("camera pid: "+str(camera.pid))
        # move old file to USB
        print("moving file to usb ...")
        os.system("mv "+OLD_FILE+" "+USB_FOLDER)
        print("file moved")
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
else:
    print("code finished ["+datetime.datetime.now().strftime('%H:%M:%S')+"]")