#! /usr/bin/python

import os
from gps import *
import time
import threading
import csv

# Class to run thread for GPSD
class GpsPoller(threading.Thread):
    # starts the Thread
    def __init__(self):
        threading.Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        self.current_value = None

    # get the most recent buffered value
    def get_current_value(self):
        return self.current_value

    # keeps the thread running listening to gpsd data
    def run(self):
        try:
            while True:
                self.current_value = self.session.next()
                time.sleep(0.2) # tune this, you might not get values that quickly
        except StopIteration:
            pass

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
    self.gpsp = GpsPoller()             # create the thread
    self.gpsp.start()                   # start it up
    self.setTime()                      # set system time
    # generate filename for CSV
    self.fname = self.FileNamer(usb_path + time.strftime("%d_%m_%Y"), "csv")

  # function to write one row of data into CSV, only when fix is detected
  def writeCSV(self):
    # write headers
    if not os.path.isfile(self.fname):
      with open(self.fname, "wb") as fdata:
        writer = csv.writer(fdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        writer.writerow(('mode','time','speed','longitute','latitude','altitude','track'))
    # write data row if fix present
    try:
        report = self.gpsp.get_current_value()
        if report['class'] == 'TPV' and report['mode'] != '1':
            row = []
            with open(self.fname, "wb") as fdata:
                if hasattr(report, 'mode'): row.append(str(report.mode))
                if hasattr(report, 'time'): row.append(str(report.time))
                if hasattr(report, 'speed'): row.append(str(report.speed*gps.MPS_TO_KPH))
                if hasattr(report, 'lon'): row.append(str(report.lon))
                if hasattr(report, 'lat'): row.append(str(report.lat))
                if hasattr(report, 'climb'): row.append(str(report.climb))
                if hasattr(report, 'alt'): row.append(str(report.alt))
                if hasattr(report, 'track'): row.append(str(report.track))
                writer = csv.writer(fdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
                writer.writerow(row)
    except Exception as exp:
        return str(exp)
    else:
        return "gps data logged succesfully"

  # debug function to dump gps data to the screen
  def dumpData(self):
    os.system('clear')
    try:
        report = self.gpsp.get_current_value()
        # Time Position Velocity Report
        if report['class'] == 'TPV':
            # To see all report data, uncomment the line below
            #print report 1-no fix 2-2D 3-3D   
            if hasattr(report, 'mode'):  print "mode:", report.mode
            if hasattr(report, 'time'):  print "time:", report.time
            if hasattr(report, 'speed'): print "speed:", report.speed * gps.MPS_TO_KPH
            if hasattr(report, 'lon'):   print "longitute:", report.lon
            if hasattr(report, 'lat'):   print "latitude:", report.lat
            if hasattr(report, 'climb'): print "climb:", report.climb
            if hasattr(report, 'alt'):   print "altitude:", report.alt
            if hasattr(report, 'track'): print "track:", report.track
            print " "
    except: pass

  # get time from GPS and set system time
  def setTime(self):
    time.sleep(10)                      # wait for gps to read date properly
    #date_time = time.strptime("%d_%m_%Y"), self.gpsd.utc)

  # closing threads 
  def close(self):
    self.gpsp.running = False
    #self.gpsp.join()               # wait for the thread to finish what it's doing