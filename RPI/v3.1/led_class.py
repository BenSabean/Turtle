#!/usr/bin/python2

#
# Class to interract with status LED's and Alive pin
# 

import RPi.GPIO as GPIO
from time import sleep

class Gpio_class():
    REC_LED = 27
    RUN_LED = 22
    ALIVE = 17
    SWITCH = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    def __init__(self, rec_led = 27, run_led = 22, alive = 17, switch = 26):
        self.REC_LED = rec_led
        self.RUN_LED = run_led
        self.ALIVE = alive
        self.SWITCH = switch
        # declare IO
        GPIO.setup(self.ALIVE, GPIO.OUT)
        GPIO.setup(self.REC_LED, GPIO.OUT)
        GPIO.setup(self.RUN_LED, GPIO.OUT)
        GPIO.setup(self.SWITCH, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        # set initial states
        GPIO.output(self.ALIVE, GPIO.HIGH)
        GPIO.output(self.RUN_LED, GPIO.HIGH)
        
    # set recording ON and run led OFF
    def setRec(self):
        GPIO.output(self.REC_LED, GPIO.HIGH)
        GPIO.output(self.RUN_LED, GPIO.LOW)
    
    # set run ON and recording led OFF
    def setRun(self):
        GPIO.output(self.REC_LED, GPIO.LOW)
        GPIO.output(self.RUN_LED, GPIO.HIGH)
    
    # set both LED's low
    def clear(self):
        GPIO.output(self.REC_LED, GPIO.LOW)
        GPIO.output(self.RUN_LED, GPIO.LOW)

    # blink run led number of times
    def blink(self, times):
        for i in range (0, times):
            GPIO.output(self.RUN_LED, GPIO.LOW)
            sleep(0.2)
            GPIO.output(self.RUN_LED, GPIO.HIGH)
            sleep(0.2)
    
    # check if switch pin is pulled low
    def checkSwitch(self):
        return GPIO.input(self.SWITCH)