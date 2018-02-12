import os
from time import sleep
from picamera
import RPi.GPIO as GPIO
import serial                   

# Setting Serial port parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=60,                    # port delay in seconds
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

# gets a time string over Serial COM from Arduino module
def getTime (port):
    time = "2018-02-07-22-15"
    port.write("TIME")              # Sending command to get Time
    time = port.readline()
    if (time != ""):
        time = time[:-2]
        print(time)                 # DEBUG
        array = time.split('-')
        # Converting to type string again with Zero fill
        array = toInt(array)
        array = toString(array)
    return array

# Converts string array to int array
def toInt (array):
    for element in array:
        element = int(element)

# Converts int array to string array
def toString (array):
    for element in array:
        element = str(element).zfill(2)

# keeping track of the time minute by minute
def configureTime (_now):
    # Converting to type int
    _now = toInt(_now)
    _now[minute] += 1
    if(_now[minute] > 60)
        _now[minute] -= 60
        _now[hour] += 1
    if(_now[hour] > 24)
        _now[hour] -= 24
        _now[day] += 1
    _now = toString(_now)
    return _now

# this function returns True/False if Sleep command received
def checkSleep (port):
    message = port.readline()
    if (message != ""):
        message = message[:-2]
        if(message == "SLEEP"):
            port.write("OK")
            return True
    return False

# indexes for date-time formating
year = 0
month = 1
day = 2
hour = 3
minute = 4

# getting array with current data-time
now = getTime(port)
# creating camera object
camera = picamera.PiCamera()
try:
    # Setting parameters
    camera.resolution = (1640, 922) # (1280x720)fullFoV (1640x922)16:9
    camera.framerate = 25           # Max for resolution high res is 30
    camera.rotation = 180
    # Start recording
    camera.start_preview()          # DEBUG
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = now[year] + "/" + now[month] + "/" + now[day] + " " + now[hour] + ":" + now[minute]
    # Specifing output file
    camera.start_recording('/home/pi/Desktop/' + now[year] + "_" + now[month] + "_" + now[day] + '.h264')
    # Starting a loop and constantly checking for SLEEP command 
    while checkSleep() != True:
        camera.annotate_text = now[year] + "/" + now[month] + "/" + now[day] + " " + now[hour] + ":" + now[minute]
        configureTime(now)

    # Finish recording
    camera.stop_recording()
    camera.stop_preview()           # DEBUG
    pass
finally:
    camera.close()
    # os.system("shutdown -t now")






