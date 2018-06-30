#
# Code to test GPS
#

from gps_class import GPS_class
import os
import time


USB = "/home/pi/USB"

print "start"
gps_cs = GPS_class(USB)
gps_cs.setTime()

for i in range (0, 30):
    os.system("clear")
    try:
        gps_cs.dumpData()
    except Exception as e:
        print e
        raise
    time.sleep(1)

print "\n\nfinished"
gps_cs.close()
quit()



'''
import gps
 
# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
 
while True:
    try:
    	report = session.next()
		# Wait for a 'TPV' report and display the current time
        # Time Position Velocity Report
        if report['class'] == 'TPV':
            # To see all report data, uncomment the line below
            #print report       
            if hasattr(report, 'mode'):     # 1-no fix 2-2D 3-3D
                print "mode:", report.mode
            if hasattr(report, 'time'):
                print "time:", report.time
            if hasattr(report, 'speed'):
				print "speed:", report.speed * gps.MPS_TO_KPH
            if hasattr(report, 'lon'):
                print "longitute:", report.lon
            if hasattr(report, 'lat'):
                print "latitude:", report.lat
            if hasattr(report, 'climb'):
                print "climb:", report.climb
            if hasattr(report, 'alt'):   # presend when mode is 3
                print "altitude:", report.alt
            if hasattr(report, 'track'):   
                print "track:", report.track
            print " "
    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"
'''