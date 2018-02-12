from time import sleep
import picamera
import datetime as dt

'''
    This program demostrates how to work with picamera
    to convert to m4 use:
    $ sudo apt-get install gpac
    $ MP4Box -add myvideo.h264 myvideo.mp4 && rm myvideo.h264
    to preview use :
    $ omxplayer myvideo.mp4
'''

# Setting parameters
camera = picamera.PiCamera()
try:
    # Setting parameters
    camera.resolution = (1640, 922) # (1280x720)fullFoV (1640x922)16:9
    camera.framerate = 25
    camera.rotation = 180
    # Start recording
    camera.start_preview()
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Specifing output file
    camera.start_recording('/home/pi/Desktop/test2.h264')
    start = dt.datetime.now()
    while (dt.datetime.now() - start).seconds < 30:
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        camera.wait_recording(0.2)
    # Finish recording
    camera.stop_recording()
    camera.stop_preview()
    pass
finally:
    camera.close()








