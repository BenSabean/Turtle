#! /usr/bin/python

import os
from gps import *
import time
import threading
import csv


# global - gps deamon
gpsd = None

# Class to run thread for GPSD
class GpsPoller(threading.Thread):
  global gpsd
  running = True
  # init
  def __init__(self):
    threading.Thread.__init__(self)
    self.current_value = None
    self.running = True                # setting the thread running to true
  # listening for the gps
  def run(self):
    global gpsd
    while self.running:
      gpsd.next()                 # this will continue to loop and grab EACH set of gpsd info to clear the buffer

# Class to interract with the gps and save CSV
class GPS_class():
  global gpsd
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
    global gpsd
    gpsd = gps(mode=WATCH_ENABLE)       # starting the stream of info GPS Demon program
    self.gpsp = GpsPoller()             # create the thread
    self.gpsp.start()                   # start it up
    self.setTime()                      # set system time
    # generate filename for CSV
    self.fname = self.FileNamer(usb_path + time.strftime("%d_%m_%Y"), "csv")

  # function to write one row of data into CSV, only when fix is detected
  def writeCSV(self):
    global gpsd
    # write headers
    if not os.path.isfile(self.fname):
      with open(self.fname, "wb") as fdata:
        writer = csv.writer(fdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        writer.writerow(('latitude','longitude','time utc','altitude (m)','eps','epx','epv','ept','speed (m/s)','climb','track'))
    # write data row if fix present
    if gpsd.fix.mode == 2 or gpsd.fix.mode == 3:
      with open(self.fname, "wb") as fdata:
        writer = csv.writer(fdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        writer.writerow((gpsd.fix.latitude,gpsd.fix.longitude,str(gpsd.utc),gpsd.fix.altitude,gpsd.fix.eps,gpsd.fix.epx,gpsd.fix.epv,gpsd.fix.ept,gpsd.fix.speed,gpsd.fix.climb,gpsd.fix.track))

  # debug function to dump gps data to the screen
  def dumpData(self):
    global gpsd
    os.system('clear')
    print '----------------------------------------'
    print 'latitude    ' , gpsd.fix.latitude
    print 'longitude   ' , gpsd.fix.longitude
    print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
    print 'altitude (m)' , gpsd.fix.altitude
    print 'eps         ' , gpsd.fix.eps
    print 'epx         ' , gpsd.fix.epx
    print 'epv         ' , gpsd.fix.epv
    print 'ept         ' , gpsd.fix.ept
    print 'speed (m/s) ' , gpsd.fix.speed
    print 'climb       ' , gpsd.fix.climb
    print 'track       ' , gpsd.fix.track
    print 'mode        ' , gpsd.fix.mode
    print 'sats        ' , gpsd.satellites

  # get time from GPS and set system time
  def setTime(self):
    time.sleep(10)                      # wait for gps to read date properly
    #date_time = time.strptime("%d_%m_%Y"), self.gpsd.utc)

  # closing threads 
  def close(self):
    print "Killing Thread..."
    self.gpsp.running = False
    try: self.gpsp.join()               # wait for the thread to finish what it's doing
    except: pass
    print "Done"