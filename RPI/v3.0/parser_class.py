#!/usr/bin/python2

#
# Class to interract with setup.txt file
# Parses according to the following format:
# [parameter]=[value] \n
# ...
# 

import datetime

class SetupFile():
    filepath = "/home/pi/USB/setup.txt"
    delim = '='
    param = []
    value = []
    start = "08:00"
    end = "17:00"
    release = "72:00"

    def __init__(self, path):
        self.filepath = path
        # Openning the file
        with open(self.filepath, 'r') as _file:
            # loop throught each line
            for line in _file:
                if line and line[0].isalpha():
                    p,val = line.split(self.delim)
                    self.param.append(p)
                    self.value.append(val[:-1])
                    if(p == "start"): self.start = val
                    if(p == "end"): self.end = val
                    if(p == "release"): self.release = val
    
    # Return value based on parameter name
    def getParam(self, parameter):
        try:
            # returning pre defined mission parameters
            if(parameter == "sleep"): return self.calcSleep()
            if(parameter == "recording"): return self.calcRec()
            # returnning release time from setup file
            # format: [hr, min]
            if(parameter == "release"): 
                try:
                    rls = self.release.split(":")
                    return [int(rls[0]), int(rls[1])]
                except: pass
                return 0
            # returning any other parameter from the file
            for i in range(len(self.param)):
                if(self.param[i] == parameter): 
                    return int(self.value[i])
        except Exception as e:
            print e
        return 0

    # return sleep interval (int) [hour,min]
    def calcSleep(self):
        try:
            # Converting to minutes
            _start = self.toMin(self.start)             # start time
            _now = datetime.datetime.now()              # current time
            _now = self.toMin(str(_now.hour)+":"+str(_now.minute))
            # caculate sleep time 
            if(_now > _start): _start += 1440
            s_dur = _start - _now
            # break down to [hh,mm]
            hr = int(s_dur/60)
            m = s_dur%60
            return [hr, m]
        except Exception as exp:
            print exp
            pass
        return [15, 0]

    # return recording interval in minutes (int)
    def calcRec(self):
        # Converting to minutes
        _start = self.toMin(self.start)             # start timeifconfig
        _end = self.toMin(self.end)                 # end time
        _now = datetime.datetime.now()              # current time
        _now = self.toMin(str(_now.hour)+":"+str(_now.minute))
        # check if start/end times are currect
        if(_start > _end):
            _temp = _start      # swap
            _start = _end       # swap
            _end = _temp        # swap
        # past recording time
        if(_now > _end or _now < _start): return 0
        # in the recording zone
        return _end - _now

    # convert from string [hh]:[mm] to int min
    def toMin(self, str_time):
        try:
            hr, min = str_time.split(':')
            return int(hr)*60 + int(min)
        except Exception as exp:
            print exp
            pass
        return 0