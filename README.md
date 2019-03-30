# RaspberryPi

Project details are posted in the <a href="https://github.com/igrowing/RaspberryPi/wiki">Wiki</a>.

## ptracker.py
People/human presence detector.
The goal of the scrip is: 
Make reliable and cheap user presence detection with no adding hardware. 

Major assumption is: Every capable person in premises (your home. your office) has mobile phone and connected automatically to the WiFi.

Prerequisites:

1. In `/home/pi` folder create `people.csv` file in format:
```
user_name,full_or_part_MAC
```
Example:
```
joe,AA:BB:FF
bar,12:23:34:45:56
```
2. Install `sudo pip install paho-mqtt netaddr` on your Linux.

The script sends the MQTT status and prints to the shell only on its change (when any user departs or arrives the premises).
Add your own logic to take actions.

See [Node-Red flow as example os use](https://flows.nodered.org/flow/06f2eabb78d608153da5dccb9a2a6912).

## Power monitoring
3 SCTs + 2 ADC ADS1115 are used to digitize AC electricity consumption.

- read4channels.py - reads all differential channels of 2 ADCs and prints to screen + can post to MQTT.
- poll_power.py - is used as driver for read4channels. It aggregates power monitoring and sends/publishes averages to MQTT. Power monitoring can be invoked from /etc/rc.local, or in any other way as background service.

## Removing retained MQTT messages from the broker
During R&D process the MQTT broken becomes full of irrelevant messages. 

- clean_retained_mqtt.sh - Simple script cleans the MQTT broker.
