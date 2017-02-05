#!/usr/bin/env python
# Simple demo of reading the difference between channel 1 and 0 on an ADS1x15 ADC.
# Authors: Tony DiCola, igrowing,
# License: Public Domain
import time

# Import the ADS1x15 module.
import Adafruit_ADS1x15

# Get ready to post MQTT status. Install the lirary first.
# sudo pip install paho-mqtt
import paho.mqtt.publish as publish

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()  # Default address id 0x48
adc1 = Adafruit_ADS1x15.ADS1115(address=0x49)

adc._data_rate_config(250)
adc1._data_rate_config(250)

# Note you can change the I2C address from its default (0x48), and/or the I2C
# bus by passing in these optional parameters:
#adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 4
NUM_CURRENT_SAMPLES = 100

# Sensor is 30A/1V. Max reading is 16 bits. It's differential, so 15 bits for absolute value. 
# Gain = 4 => +/-1.024V (exclude 0.024V as saturated data). From here:
# Max range is 2^15 for 0-1V. Max value provides a peak current.
# TrueRMS_sine = PeakCurrent / sqrt(2) => 30A / 1.414 / 2^15 is a constant for conversion.
# Use mA instead of Ampers for easy further calculations. Calculate the constant once for CPU saving.
# 30000 mA / 1.414 = 21429
# 1.73 is empiric coefficient for correct current representation.
CONVERTOR = 1.73 * 21429 / 2 ** 15

def readCurrent():
    sum = 0.0
    max = {0: 0, 1: 0, 2: 0, 3: 0}
    # Read the difference between channel 0 and 1 (i.e. channel 0 minus channel 1).
    # Note you can change the differential value to the following:
    #  - 0 = Channel 0 minus channel 1
    #  - 1 = Channel 0 minus channel 3
    #  - 2 = Channel 1 minus channel 3
    #  - 3 = Channel 2 minus channel 3
    for x in xrange(NUM_CURRENT_SAMPLES):
        raw = {
             0: abs(adc1.read_adc_difference(0, gain=GAIN)),
             1: abs(adc1.read_adc_difference(3, gain=GAIN)),
             2: abs(adc.read_adc_difference(0, gain=GAIN)),
             3: abs(adc.read_adc_difference(3, gain=GAIN)),
            }
	for i in xrange(len(raw)):
            max[i] = raw[i] if raw[i] > max[i] else max[i]

    #current_rms = math.sqrt(sum / NUM_CURRENT_SAMPLES) * 5
    #return current_rms
    #return max * 1.0 / CONVERTOR
    return {i: int(y / CONVERTOR) for i, y in max.iteritems()}


def main(count=10):
    print('Press Ctrl-C to quit...')
    #while True:
    for zzz in range(count):
        #time.sleep(0.5)
        d = readCurrent()
        print d
        msgs = []
        for i, y in d.iteritems():
            #publish.single("shm/rpi/power/main/phase/" + str(i), y)
            msgs.append({'topic': "shm/rpi/power/main/phase/" + str(i), 'payload': y, 'retain': False})
        publish.multiple(msgs, hostname='127.0.0.1')

# Examples of MQTT use:
#publish.single("test/test", "Hello world! :)", retain=False, hostname="localhost")
# API: https://pypi.python.org/pypi/paho-mqtt

# Use this trick to execute the file. Normally, it's a module to be imported.
if __name__ == "__main__":
    import sys
    try:
        n = int(sys.argv[1])
    except:
        n = 10
    main(n)
