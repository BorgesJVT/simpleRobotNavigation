#! /usr/bin/python
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)

while 1:
    #Turn LED On
    GPIO.output(4, GPIO.HIGH)
    print "1"
    time.sleep(1)

    #Turn LED Off
    GPIO.output(4, GPIO.LOW)
    print "0"
    time.sleep(1)
