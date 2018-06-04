#!/usr/bin/env python
from __future__ import print_function
import os
# Get ready to post MQTT status. Install the library first.
# sudo pip install paho-mqtt
import paho.mqtt.publish as publish
import sensors.read4channels as read4channels

os.system("logger -t poll_power 'Started power monitoring.'")

while True:
    
    d = []  # Empty list of dictionaries for power reading
    measures = 75
    for c in xrange(measures):  #  Collect data for ~5 minutes
        # Read energy
        d.append(read4channels.readCurrent())
        
    # Calc avg for values
    # Sum all values into d[0]
    for c in xrange(1, len(d)):
        for k, v in d[c].iteritems():
            d[0][k] += v
    # Divide values in d[0] by count
    for k, v in d[0].iteritems():
        d[0][k] = v / len(d)
    
    # attempt to publish this data to the topic
    try:
        msgs = []
        for i, y in d[0].iteritems():
            # publish.single("shm/rpi/power/main/phase/" + str(i), y)
            msgs.append({'topic': "shm/hub/power/main/phase/" + str(i), 'payload': y, 'retain': False})
        publish.multiple(msgs, hostname='127.0.0.1')

    except KeyboardInterrupt:
        break

    except:
        os.system("logger -t poll_power 'There was an error while publishing the data.'")
