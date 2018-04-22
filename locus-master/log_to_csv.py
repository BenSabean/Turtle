

# Program to test locus data parsing into CSV file

import locus            # lib for GPS data parsing
import json             # JSON format library
import datetime         # lib for system datetime


TEMP_PATH = "gps_raw.txt"

f_csv = open(datetime.datetime.now().strftime('%Y-%m-%d') + '.csv', "a")

print("PARSING STARTED")
# Parse data as JSOM
coords = locus.parseFile(TEMP_PATH)
# filter out bad data
coords = [c for c in coords if c.fix > 0 and c.fix < 5]
# Printing into CSV file
# Headers
f_csv.write("Timestamp,Satellite Fix,Latitude,Longitude,Altitude\n")

# Lines
for c in coords:
    line = str(c.datetime) +","+ str(c.fix) +","+ str(c.latitude) +","+ str(c.longitude) +","+ str(c.height)
    f_csv.write(line +"\n")
    print(line)