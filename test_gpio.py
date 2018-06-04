#! /usr/bin/env python

import RPi.GPIO as GPIO
import time
gpios = [5, 6, 12] # Channels 1, 2, 3 accordingly
GPIO.setmode(GPIO.BCM)
for i in gpios:
    print "setup", i
    GPIO.setup(i, GPIO.OUT)

#GPIO.output(12, True)

while True:
    for i in gpios:
        GPIO.output(i, not GPIO.input(i))
        time.sleep(1)

