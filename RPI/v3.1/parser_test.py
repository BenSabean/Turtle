#!/usr/bin/python2

from parser_class import SetupFile  # custom made class to read setup file
from time import sleep              # sleep function in seconds
from timer_class import Timer       # custom made class for i2c com
import os

USB_FOLDER =        "/home/pi/USB/"
SETUP_FILE = USB_FOLDER + "setup.txt"

# Objects
setup_file = SetupFile(SETUP_FILE)      # Setup file object
timer = Timer()                         # Arduino COM object

sleep(1)
print("START")
os.system("date")
sleep(1)

flag = timer.checkStatus()
sleep(1)
if flag[1] == 0:
    # parsing release time from file
    time = []*2
    time = setup_file.getParam("release")
    print("setting release time for: "+str(time[0])+"hr "+str(time[1])+"min")
    try:
        if not time == 0: 
            resp = timer.setRelease(time[0], time[1])
            if resp == True: print("release time set succesfully")
            else:            print("release time set failed")
    except Exception as exp:
        print(str(exp))
        pass

sleep(1)
# record battery voltage
print("battery voltage is "+timer.getVoltage()+"v")
sleep(1)
# getting recording duration
REC_DUR = setup_file.getParam("recording")
print("recording time is "+str(REC_DUR)+" min")
# getting video sections
section = setup_file.getParam("sections")
if section > 0 and section <= 720: VIDEO_SECTION = section
print("recording sections "+str(VIDEO_SECTION)+" min")
# video width
print "width" ,setup_file.getParam("width")
# video height
print "height", setup_file.getParam("height")
# frames per second
print "fps", setup_file.getParam("fps")
# camera rotation
print "rotation", setup_file.getParam("rotation")

sleep(2)
# Setting Sleep time for Arduino
s_hr, s_min = setup_file.getParam("sleep") 
print("recording finished, sleep for "+str(s_hr)+"hr "+str(s_min)+"min")
if timer.setSleep(s_hr, s_min):
    print("sleep set succesfully")
else:
    print("sleep failed")