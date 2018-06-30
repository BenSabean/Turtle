#!/usr/bin/python2

#
# Class to interract with setup.txt file
# Parses according to the following format:
# [parameter]=[value] \n
# ...
# 

class SetupFile():
    filepath = "/home/pi/USB/setup.txt"
    delim = '='
    param = []
    value = []
    start = ""
    end = ""

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
    
    # Return value based on parameter name
    def getParam(self, parameter):
        try:
            for i in range(len(self.param)):
                if(self.param[i] == parameter):
                    return self.value[i]
            return None
        except Exception as e:
            print e
            pass

    # return sleep interval (int) [hour,min]
    def getSleep(self):
        # Converting to minutes
        _start = self.toMin(self.start)+1440
        _end = self.toMin(self.end)
        s_dur = _start - _end
        hr = int(s_dur/60)
        m = s_dur%60
        return [hr, m]

    # return recording interval in minutes (int)
    def getRec(self):
        # Converting to minutes
        _start = self.toMin(self.start)
        _end = self.toMin(self.end)
        return _end - _start

    # convert from string [hh]:[mm] to int min
    def toMin(self, str_time):
        hr, min = str_time.split(':')
        return int(hr)*60 + int(min)
        
        