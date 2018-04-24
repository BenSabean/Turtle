'''
Date:    Apr 17, 2018

This program is used to record video into a file
program excepts recording inverval in seconds
recording will continue for interval period
or units a Kill Signal is received

Recorded videos are in .h264 format
to decode videos, use open source free decoder:
$ sudo apt-get install gpac
$ MP4Box -add myvideo.h264 myvideo.mp4 && rm myvideo.h264
to preview use :
omxplayer myvideo.mp4

contact: Arthur Bondar
email:   arthur.bondar.1@gmail.com
'''

from time import sleep
import sys
import picamera
from datetime import datetime
import datetime as dt
import logging

# File path's
LOG_PATH = "/home/pi/Turtle/RPI/USB/camera.log"
REC_PATH = "/home/pi/Turtle/RPI/USB/"

# Creating Log file
logging.basicConfig(filename=LOG_PATH, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info("CAMERA STARTED")

# Checking command line arguments
# (1) python (2) ../Camera.py (3) 50400
if(len(sys.argv) != 3):
    logging.info("WRONG ARGUMENT NUMBER")
    print("WRONG ARGUMENT NUMBER")
    sys.exit(0)

# Logging start of recording
logging.info("TIME: " + dt.datetime.now())
logging.info("Recording Time: " + str(sys.argv[2]))
recording_time = int(sys.argv[2])   # recording time in seconds

camera = picamera.PiCamera()
try:

    #
    #   Camera Initialization
    #
    # Video Parameters
    camera.resolution = (1640, 922) # (1280x720)fullFoV (1640x922)16:9
    camera.framerate = 25
    camera.rotation = 180
    # Text frame parameters
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Output file for saving
    camera.start_recording(REC_PATH + dt.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.h264')

    #
    #   Recording Loop
    #
    start = dt.datetime.now()
    while (dt.datetime.now() - start).seconds < (recording_time):
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        camera.wait_recording(1)

except Exception as e:
    logging.debug(str(e))


finally:
    #
    #   Exiting Routine
    #
    # Finish recording
    logging.info("CAMERA CODE FINISHED")
    camera.stop_recording()
    camera.close()


