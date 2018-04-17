from time import sleep
import sys
import picamera
from datetime import datetime
import datetime as dt
import logging
'''
    This program demostrates how to work with picamera
    to convert to m4 use:
    $ sudo apt-get install gpac
    $ MP4Box -add myvideo.h264 myvideo.mp4 && rm myvideo.h264
    to preview use :
    omxplayer myvideo.mp4
'''
logging.basicConfig(filename='/home/pi/Turtle/RPI/USB/camera.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
# Setting parameters
camera = picamera.PiCamera()
logging.info("CAMERA STARTED")

if(len(sys.argv) != 3):
    print("Usage: python " + sys.argv[0] + " <TIME> <DURATION>")
    sys.exit(0)

logging.info("TIME: " + str(sys.argv[1]))
logging.info("Recording Time: " + str(sys.argv[2]))
recording_time = int(sys.argv[2])  # recording time in seconds

try:
    # Try to set current time as time recieved from Arduino
    # or set to system time if resonse was corrupted
    try:
        currentTime = datetime.strptime(sys.argv[1], '%Y_%m_%d_%H:%M:%S')
    except Exception as e:
        logging.debug(str(e))
        currentTime = dt.datetime.now()
    print(currentTime)
    # Setting parameters
    camera.resolution = (1640, 922) # (1280x720)fullFoV (1640x922)16:9
    camera.framerate = 25
    camera.rotation = 180
    # Start recording
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = currentTime.strftime('%Y-%m-%d %H:%M:%S')

    # Specifing output file
    camera.start_recording('/home/pi/Turtle/RPI/USB/' + currentTime.strftime('%Y_%m_%d_%H-%M-%S') + '.h264')
    # sorry this was bothering me        str(str(currentTime).replace(' ', '_') + '.h264').replace(':','-'))

    start = dt.datetime.now()
    while (dt.datetime.now() - start).seconds < (recording_time):
        currentTime = currentTime + dt.timedelta(0,1)
        camera.annotate_text = currentTime.strftime('%Y-%m-%d %H:%M:%S')
        camera.wait_recording(1)

except Exception as e:
    #f = open("/home/pi/Turtle/RPI/error.log", "a")
    #f.write("EXEPTION:" + str(e) + "/n")
    #f.close()
    logging.debug(str(e))

finally:
    # Finish recording
    logging.info('CAMERA CODE FINISHED')
    camera.stop_recording()
    camera.close()


