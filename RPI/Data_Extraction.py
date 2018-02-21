'''
    This program saves data stored during night time by Arduino controller
    Data format is Timestamp, Longitude and Latitude
    Data to be stored in a csv file, with date as the name
'''

import os
from time import sleep
import serial 


''' ----- METHODS ----- '''
# file path to store GPS data
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

# Send request and receive Date-Time
def port_getTime(port):
    port.write("TIME")               # Send GPS command
    message = ""
    message = port.readline()
    if (message != ""):
        port.write("OK")            # Handshake for data reception
        message = message[:-2]      # Clearing end of string garbage
    return message

# Writes gps data into CSV File
def store_GPS(_f, _time, _long, _lat):
    _f.write(_time+","+_long+","+_lat+"\n")

# Checks wether new GPS file needs to be created (after 00:00)
def newDay(dateTime, oldDay):
    dateTime = dateTime.split('_')
    day = dateTime[2]               # YYYY_MM_DD_HH_mm
    if(int(day) > int(oldDay)):
        return True
    else:
        return False
    
# Opens a file and prints headers if necessary
def openFile(_path):
    # if file is doesn't exist write headers and create file
    if (os.path.isfile(_path) == False):
        file f = open(file_name, "w")
        csv1.write("TimeStamp,Latitude,Longitude\n")
    else:
        file f = open(file_name, "a")
    return f

''' ----- PARAMETERS & VARIABLES ----- '''
# Setting parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=5,                      # in seconds
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE 
)
message = "start"


 ''' ----- PROGRAM SETUP ----- '''
# Getting date from Adruino
message = port_getTime(port)
date = message.split("_")
# Creating file name for first GPS file
file_name = path + date[0] + "_" + str(int(date[1])-1) + "_" + date[2] + ".csv"
file csv1 = openFile(file_name)
# Creating file name for second GPS file
file_name = path + date[0] + "_" + date[1] + "_" + date[2] + ".csv"
file csv2 = openFile(file_name)


 ''' ----- PROGRAM LOOP ----- '''
try:
    # loop untill the end of transmition
    while message != "EOT":
        message = port_getGPS(port)
        if(message != "" and message != "EOT"):
            array = message.split(";")
            # GPS data went over 00:00 -> new file needs to be open
            if(newDay(array[0], str(int(date[1])-1)) == True):
                # Store new GPS data
                store_GPS(csv1, array[0], array[1], array[2])
            else:
                store_GPS(csv2, array[0], array[1], array[2])

finally:
    csv1.close()
    csv2.close()


