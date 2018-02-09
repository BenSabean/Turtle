import os
from time import sleep
from picamera import PiCamera
# run: sudo apt-get install python-serial
# disable serial login shell

# Setting parameters
camera = PiCamera()
camera.resolution = (1920, 1080)

# keeping track of the time minute by minute
def configureTime (_now):
    _now[minute] += 1
    if(_now[minute] > 60)
        _now[minute] -= 60
        _now[hour] += 1
    if(_now[hour] > 24)
        _now[hour] -= 24
        _now[day] += 1
    return _now

# constants for date-time formating
year = 0
month = 1
day = 2
hour = 3
minute = 4

# getting array with current data-time
now = [2018, 2, 9, 15, 0]

# Start recording
camera.start_preview() # DEBUG
camera.annotate_background = picamera.Color('black')
camera.start_recording('/home/pi/Desktop/' + now[year] + '_' + now[month] + '_' + now[day] + '.h264')
start = dt.datetime.now()

while(port.readline() != "SLEEP"):
    camera.annotate_text = now[year] + "/" + now[month] + "/" + now[day] + " " + now[hour] + ":" + now[minute]
    sleep(60)
    now = configureTime(now)

camera.stop_recording()
camera.stop_preview() # DEBUG








