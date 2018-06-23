#!/usr/bin/python2

from led_class import Gpio_class    # custom made class to switch led's
import os
import time

try:
    io = Gpio_class()
    while True:
        print io.checkSwitch()
        time.sleep(1)
except:
    quit()