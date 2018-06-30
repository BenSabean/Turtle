#! /usr/bin/python

import os
from gps import *
from time import *
import time
import threading
import csv

gpsd = None
gpsp = None

# Class to run thread for GPSD
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

# Class to interract with the gps and save CSV
class GPS_class():
  gpsp = None                          # Thread to read form gpsd
  fname = ""                           # CSV file name

  # function that check existence of a file
  def FileNamer(self, file, ext):
    # check if file doest exist already
    tmp = """{path}.{extension}""".format(path=file, extension=ext)
    if not os.path.isfile(tmp):
      return tmp
    # make new file name with index 1-100
    for i in range(1,100): 
      tmp = """{path}_{num}.{extension}""".format(path=file, num=i, extension=ext)
      if not os.path.isfile(tmp):
          return tmp
    return None

  # init function, starts gps thread
  def __init__(self, usb_path):
    global gpsp
    gpsp = GpsPoller()             # create the thread
    gpsp.start()                   # start it up
    #self.setTime()                      # set system time
    # generate filename for CSV
    self.fname = self.FileNamer(usb_path + time.strftime("%d_%m_%Y"), "csv")
    if not os.path.isfile(self.fname):
      with open(self.fname, "wb") as fdata:
        writer = csv.writer(fdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        writer.writerow(('mode','time','speed','longitute','latitude','climb', 'altitude','track'))
      fdata.close()

  # function to write one row of data into CSV, only when fix is detected
  def writeCSV(self):
    row = []
    with open(self.fname, "a") as fdata:
      if(gpsd.fix.mode > 1):
        row.append(str(gpsd.fix.mode))
        row.append(str(gpsd.fix.time))
        row.append(str(gpsd.fix.speed))
        row.append(str(gpsd.fix.longitude))
        row.append(str(gpsd.fix.latitude))
        row.append(str(gpsd.fix.climb))
        row.append(str(gpsd.fix.altitude))
        row.append(str(gpsd.fix.track))

        writer = csv.writer(fdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        writer.writerow(row)

    fdata.close()

  # debug function to dump gps data to the screen
  def dumpData(self):
    os.system('clear')
    if hasattr(gpsd.fix, 'mode'):  print "mode:", gpsd.fix.mode
    if hasattr(gpsd.fix, 'time'):  print "time:", gpsd.fix.time
    if hasattr(gpsd.fix, 'speed'): print "speed:", gpsd.fix.speed #* gps.MPS_TO_KPH
    if hasattr(gpsd.fix, 'lon'):   print "longitute:", gpsd.fix.longitude
    if hasattr(gpsd.fix, 'lat'):   print "latitude:", gpsd.fix.latitude
    if hasattr(gpsd.fix, 'climb'): print "climb:", gpsd.fix.climb
    if hasattr(gpsd.fix, 'alt'):   print "altitude:", gpsd.fix.altitude
    if hasattr(gpsd.fix, 'track'): print "track:", gpsd.fix.track
    print " "

  # get time from GPS and set system time
  def setTime(self):
    time.sleep(10)                      # wait for gps to read date properly
    os.system('sudo date +%Y%m%d%T -s \"{}\" --utc'.format(gpsd.utc))

  # closing threads
  def close(self):
    gpsp.running = False
    print("Stopping")
    gpsp.join()               # wait for the thread to finish what it's doing

if __name__ == "__main__":
  USB_FOLDER = "./"
  try:
    print("START")
    gps = GPS_class(USB_FOLDER)
    gps.setTime()
    while(1):
      gps.dumpData()
      gps.writeCSV()
      print("in loop")
      time.sleep(5)
  except:
    gps.close()
    print("STOP")
