#!/usr/bin/env python
'''
Wind speed sensor.
Publish to MQTT wind speed in m/s every second, minute, hour, day.
For minute, hour, and day the published speed is average.

Author: Igor Yanyutin.
'''

import time
import RPi.GPIO as GPIO

# Get ready to post MQTT status. Install the lirary first.
# sudo pip install paho-mqtt
import paho.mqtt.publish as publish

pin = 4
TICKS_MS = 10.0  # Keep decimal for parts of m/s
GPIO.setwarnings(False)  # Disable warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
_counter_s = 0
_counter_m = 0
_counter_h = 0
_counter_d = 0

def run():
    '''Poll sensor, count ticks, update MQTT every second of progress.'''
    s = m = h = d = time.time()
    global _counter_s, _counter_m, _counter_h, _counter_d
    while True:
        # Increase counter only in case of actual trigger, not timeout.
        if GPIO.wait_for_edge(pin, GPIO.FALLING, bouncetime=1, timeout=1000):  # times in ms
            _counter_s += 1
        if time.time() - s > 1:   # more than a sec
            publish.single("shm/orchid/wind/last_sec", _counter_s / TICKS_MS, retain=False, hostname="localhost")
            s = time.time()
            _counter_m += _counter_s
            _counter_s = 0
        if time.time() - m > 60:   # more than a min
            publish.single("shm/orchid/wind/last_min", _counter_m / TICKS_MS / 60, retain=False, hostname="localhost")
            m = time.time()
            _counter_h += _counter_m
            _counter_m = 0
        if time.time() - h > 3600:   # more than a hour
            publish.single("shm/orchid/wind/last_hour", _counter_h / TICKS_MS / 3600, retain=False, hostname="localhost")
            h = time.time()
            _counter_d += _counter_h
            _counter_h = 0
        if time.time() - d > 86400:   # more than a day
            publish.single("shm/orchid/wind/last_day", _counter_d / TICKS_MS / 86400, retain=False, hostname="localhost")
            d = time.time()
            _counter_d = 0


# Use this trick to execute the file. Normally, it's a module to be imported.
if __name__ == "__main__":
    print 'Subscribe to data with:'
    print 'mosquitto_sub -v -t "#"'
    print 'Search for wind :)'
    run()
