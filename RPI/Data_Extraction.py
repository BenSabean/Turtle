'''
    This program saves data stored during night time by Arduino controller
    Data format is Timestamp, Longitude and Latitude
    Data to be stored in a csv file, with date as the name
'''

from time import sleep
import serial 


''' METHODS & STRUCTURES '''
# GPS Data containter
class cGPS:
    time: str
    x: float
    y: float

# Send request and receive one set of GPS Data
def port_getGPS():
    port.write("GPS")               # Send GPS command
    message = ""
    message = port.readline()
    if (message != "" and message != "EOT"):
        port.write("OK")            # Handshake for data reception
        message = message[:-2]      # Clearing end of string garbage
    return message

# Send request and receive Date-Time
def port_getTime():
    port.write("TIME")               # Send GPS command
    message = ""
    message = port.readline()
    if (message != ""):
        port.write("OK")            # Handshake for data reception
        message = message[:-2]      # Clearing end of string garbage
    return message


''' PARAMETERS AND VARIABLES'''
# Setting parameters
port = serial.Serial(
    port = "/dev/ttyS0",
    baudrate=9600,
    timeout=5,                      # in seconds
    parity = serial.PARITY_NONE,
    bytesize = serial.EIGHTBITS,
    stopbits = serial.STOPBITS_ONE
)
# GPS Object
GPS = cGPS("X", 0, 0)
message = "start"


 ''' PROGRAM LOOP '''
# Getting date from Adruino
message = port_getTime()
array = message.split()
file_name = array[0] + "_" + array[1] + "_" + array[2] + ".csv"
file_name = "/home/pi/Video/usb/" + file_name
file _file = open(file_name, )

try:
    # loop untill the end of transmition
    while message != "EOT":


finally:



