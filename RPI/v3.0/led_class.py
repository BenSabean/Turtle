#!/usr/bin/python2

#
# Class to interract with status LED's and Alive pin
# 

import RPi.GPIO as GPIO

class Gpio_class():
    REC_LED = 27
    RUN_LED = 22
    ALIVE = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(ALIVE, GPIO.OUT)
    GPIO.setup(REC_LED, GPIO.OUT)
    GPIO.setup(RUN_LED, GPIO.OUT)

    def __init__(self, rec_led = 27, run_led = 22, alive = 17):
        self.REC_LED = rec_led
        self.RUN_LED = run_led
        self.ALIVE = alive
        GPIO.output(self.ALIVE, GPIO.HIGH)
        GPIO.output(self.RUN_LED, GPIO.HIGH)
        
    def setRec(self):
        GPIO.output(self.REC_LED, GPIO.HIGH)
        GPIO.output(self.RUN_LED, GPIO.LOW)
    
    def setRun(self):
        GPIO.output(self.REC_LED, GPIO.LOW)
        GPIO.output(self.RUN_LED, GPIO.HIGH)
    
    def clear(self):
        GPIO.output(self.REC_LED, GPIO.LOW)
        GPIO.output(self.RUN_LED, GPIO.LOW)