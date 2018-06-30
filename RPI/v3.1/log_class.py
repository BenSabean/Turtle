#!/usr/bin/python2

#
# Class to log data in a log file
# Every message is timestamped and
# Opens and closes the file on every log
# 

import datetime                 # lib for system datetime

class LogClass():
    PATH = "/home/pi/log.txt"   # default path for storing file

    # set file path on creation of the file
    def __init__(self, file_path):
        self.PATH = file_path
    
    # writing single line statement starting with the date
    def write(self, _str):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | "
        with open(self.PATH, "a") as _file:
            try:
                _file.write(now + _str + '\n')
            except:
                pass 
