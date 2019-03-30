#!/bin/bash
echo Collecting retained messages...
timeout 10 mosquitto_sub -t "#" -v > remove_mqtt
cat remove_mqtt | awk '{print $1}' > remove_mqtt1
for i in `cat remove_mqtt1`; do echo Removing $i; mosquitto_pub -r -t $i -m ''; done
rm remove_mqtt*
