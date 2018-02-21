'''
    This program records video and stores GPS data into a file
    GPS data format is Timestamp, Longitude and Latitude
    New File created for every video and GPS file
'''

import os
from time import sleep
from picamera
import RPi.GPIO as GPIO
import serial                   


''' ----- METHODS ----- '''
# file path to store GPS data and Video
path = "/home/pi/Video/usb/"

# Send request and receive one set of GPS Data
def port_getGPS(port):
    port.write("GPS")               # Send GPS command
    message = ""
    message = port.readline()
    if (message != "" and message != "EOT"):
        port.write("OK")            # Handshake for data reception
        message = message[:-2]      # Clearing end of string garbage
    return message

# Writes gps data into CSV File
def store_GPS(_f, _time, _long, _lat):
    _f.write(_time+","+_long+","+_lat+"\n")

# Send request and receive Date-Time
def port_getTime(port):
    port.write("TIME")               # Send GPS command
    message = ""
    message = port.readline()
    if (message != ""):
        port.write("OK")            # Handshake for data reception
        message = message[:-2]      # Clearing end of string garbage
    return message

# Converts string array to int array
def toInt (array):
    for element in array:
        element = int(element)
    return array

# Converts int array to string array
def toString (array):
    for element in array:
        element = str(element).zfill(2)
    return array

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


''' ----- PARAMETERS & VARIABLES ----- '''
# Setting Serial parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=1,                     # in seconds
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)

# Indexes for Date-Time
year = 0
month = 1
day = 2
hour = 3
minute = 4
# Getting date from Adruino
message = port_getTime(port)
# Format YYYY_MM_DD_HH_mm_SS
now = message.split("_")
# Variable to keep track of minutes
prev_min = int(now[minute])

# Creating file name for GPS file
file_name = path + now[year] + "_" + now[month] + "_" + now[day] + ".csv"
# If file have not been created, writes the headers
if (os.path.isfile(file_name) == False):
    file csv = open(file_name, "w")
    csv.write("TimeStamp,Latitude,Longitude\n")
else:
    file csv = open(file_name, "a")

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
    camera.start_recording(path + now[year] + "_" + now[month] + "_" + now[day] + '.h264')

     ''' ----- PROGRAM LOOP ----- '''
    # Starting a loop and constantly checking for SLEEP command 
    while checkSleep() != True:     # 1 second delay from serial port waiting time
        camera.annotate_text = now[year] + "/" + now[month] + "/" + now[day] + " " + now[hour] + ":" + now[minute]
        # Cheking if minute past
        if(prev_min != int(now[minute])):
            # Getting GPS position every min
            message = port_getGPS(port)
                if(message != "" and message != "EOT"):
                    array = message.split(";")
                    store_GPS(csv, array[0], array[1], array[2])
            # Updating prev minute
            prev_min = int(now[minute])
        # Updating video time every second
        configureTime(now)

    # Finish recording
    camera.stop_recording()
    camera.stop_preview()           # DEBUG
    pass
finally:
    camera.close()
    csv.close()
    # os.system("shutdown -t now")






