#! /usr/bin/env python

import sys
import time
import argparse
import RPi.GPIO as GPIO

relays = {1: 5, 2: 6, 3: 12, 4: 13}  # Channels 1, 2, 3 accordingly
GPIO.setwarnings(False)       # Disable warnings
statuses = ('off', 'on')

m_name = __file__
help = ''' Valve/Relay control module.
./%(m_name)s valve_number <on/off/status> [--duration=minutes | -d minutes] [-h] [-i | --invert] [-l | --list]

Examples:
./%(m_name)s 1 status
./%(m_name)s 1 on
./%(m_name)s -i 2 on
./%(m_name)s 3 off
./%(m_name)s 2 on --duration=70
./%(m_name)s 3 on -d 70
./%(m_name)s -i 1 on -d 10
./%(m_name)s -l
./%(m_name)s -h

Authors: Igor Yanyutin,

''' % locals()

class Relay(object):
    def __init__(self, relay, active_low=True):
        GPIO.setmode(GPIO.BCM)
        # Determine GPIOs to work with
        self.relayIO = relays[relay]
        self.active_low = active_low

    def get_status(self):
        GPIO.setup(self.relayIO, GPIO.OUT)
        return self.active_low ^ GPIO.input(self.relayIO)

    def set_status(self, status):
        '''For status use 0 or 1 as off and on accordingly.'''

        GPIO.setup(self.relayIO, GPIO.OUT)
        GPIO.output(self.relayIO, self.active_low ^ status)


def main():
    '''Process command line arguments.
    Call set_status and get_status functions directly when use as a module.
    '''

    # Get and parse arguments.
    parser = argparse.ArgumentParser()
    parser.usage = help
    parser.add_argument('valve', metavar='valve_number', nargs='?', type=int, help='Number of valve for action.')
    parser.add_argument('action', metavar='action', nargs='?', choices=['on', 'off', 'status'], help='Required action.')
    parser.add_argument('-d', '--duration', type=int, help="Duration of valve open action in minutes.")
    parser.add_argument('-i', '--invert', action='store_true', help='Use "active low" logic.')
    parser.add_argument('-l', '--list', action='store_true', help='Print known valves and GPIOs.')
    args = parser.parse_args()

    if args.list:
        print 'Valve : GPIO'
        for k, v in relays.iteritems():
            print k, ':', v
        return

    if args.valve not in relays.keys():
        print "Error: Unknown valve number."
        print help
        sys.exit(253)

    # Initialize legal GPIO.
    valve = Relay(args.valve, active_low=args.invert)

    if args.action == 'status':
        status = valve.get_status()
        print 'Status of valve # %s is %s.' % (args.valve, statuses[status])
        sys.exit(status)
    elif args.action in statuses:
        valve.set_status(statuses.index(args.action))
        print 'Status of valve # %s is set to %s.' % (args.valve, args.action)
        if args.duration:
            time.sleep(args.duration * 60)  # mins -> secs
            valve.set_status(0)
            print 'Status of valve # %s is set to off.' % args.valve
           

# Use this trick to execute the file. Normally, it's a module to be imported.
if __name__ == "__main__":
    main()
