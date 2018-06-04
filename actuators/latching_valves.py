#! /usr/bin/env python

import sys
import time
import argparse
import RPi.GPIO as GPIO

# Dictionary includes:
# Valve#: which contain dictionary of GPIO numbers per state.
valves = {1: {'on': 5, 'off': 6}, 2: {'on': 12, 'off': 13}}
GPIO.setwarnings(False)  # Disable warnings
statuses = ('off', 'on')

m_name = __file__
help = '''Latching Valve/Relay control module.
./%(m_name)s valve_number <on/off/status> [--duration=minutes | -d minutes]

Examples:
./%(m_name)s 1 status
./%(m_name)s 1 on
./%(m_name)s 3 off
./%(m_name)s 2 on --duration=70
./%(m_name)s 3 on -d 70

Authors: Igor Yanyutin,

''' % locals()

class LatchingValve(object):
    def __init__(self, valve):
        GPIO.setmode(GPIO.BCM)
        # Determine GPIOs to work with
        self.on = valves[valve]['on']
        self.off = valves[valve]['off']
    
    def get_status(self):
        # TODO: implement status read with REDIS (or else)
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(valve, GPIO.OUT)
        # return GPIO.input(valve)
        pass
        
    def set_status(self, status):
        '''For status use 0 or 1 as off and on accordingly.'''

        # Set mode for both controlling GPIOs
        GPIO.setup(self.on, GPIO.OUT)
        GPIO.setup(self.off, GPIO.OUT)
        # Ensure both GPIOs grounded
        GPIO.output(self.on, 0)
        GPIO.output(self.off, 0)
        # Set required status for valve for 0.5 sec
        active = self.on if status else self.off
        GPIO.output(active, 1)
        time.sleep(0.5)   
        # Ground active GPIO
        GPIO.output(active, 0)
    

def main():
    '''Process command line arguments.
    Call set_status and get_status functions directly when use as a module.
    '''

    parser = argparse.ArgumentParser()
    parser.usage = help
    parser.add_argument('valve', metavar='valve_number', type=int, help='Number of valve for action.')
    parser.add_argument('action', metavar='action', choices=['on','off','status'], help='Required action.')
    parser.add_argument('-d', '--duration', type=int, help="Duration of valve open action.")
    args = parser.parse_args()

    if args.valve not in valves.keys():
        print "Error: Unknown valve number."
        print help
        sys.exit(253)

    # Initialize legal GPIO.
    valve = LatchingValve(args.valve)

    if args.action == 'status':
        # status = get_status(valve)
        # print 'Status of valve # %s is %s.' % (args.valve, statuses[status])
        # sys.exit(status)
        print 'Not implemented.'
    elif args.action in statuses:
        valve.set_status(statuses.index(args.action))
        print 'Status of valve # %s is set to %s.' % (args.valve, args.action)
        if args.duration:
            time.sleep(args.duration * 60)
            valve.set_status(0)
            print 'Status of valve # %s is set to off.' % args.valve


# Use this trick to execute the file. Normally, it's a module to be imported.
if __name__ == "__main__":
    main()
