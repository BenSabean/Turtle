#!/bin/bash

sudo mount /dev/sda1 /home/pi/Turtle/RPI/USB | echo > turtle.log

sudo python /home/pi/Turtle/RPI/ledoff.py

sudo python /home/pi/Turtle/RPI/Camera_test.py

sudo MP4Box -add /home/pi/Turtle/RPI/USB/test2.h264 -tmp /home/pi/Turtle/RPI/USB/ /home/pi/Turtle/RPI/USB/test2.mp4 | echo > turtle.log

sudo umount /home/pi/Turtle/RPI/USB | echo > turtle.log

sudo python /home/pi/Turtle/RPI/led.py

# rm /home/pi/Turtle/RPI/USB/test2.h264

