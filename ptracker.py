#!/usr/bin/env python
'''
Track user presence and absence.
Read users and their MACs from file.
Track their phone presence on the network.
Report status changes to MQTT.
'''

import re
import os
import sys
import time
import subprocess

try:
    # sudo pip install netaddr
    import netaddr
    # Get ready to post MQTT status. Install the library first.
    # sudo pip install paho-mqtt
    import paho.mqtt.publish as publish
except Exception:
    print 'Error: Missing libraries. Run following command first:'
    print 'sudo pip install paho-mqtt netaddr'
    sys.exit(3)

# == GLOBALS ==
VERSION = '0.5.2'
people = []  # List of people to track
# Polling interval: poll less when present and frequent when absent
TIMEOUT_LONG = 80
TIMEOUT_SHORT = 20
_interval = TIMEOUT_SHORT
net = ''  # base IP / mask
last_time_ip = 0  # Register when checked IP addresses and recheck every day.
IP_EXPIRATON_S = 86400  # Secs in day


def logger(msg, process='ptracker'):
    msg = re.sub('[\[\{\:\;\\\'\"\]\}\<\>\(\)\.\,]', '_', msg)
    os.system('logger -t ' + process + ' ' + msg)
    # return msg  # Keep memoize updated


def run_cmd(cmd, error_message='', input=None, log_error=True, exit=False):
    """Run a command, optionally logging error message if return code not zero. Exit program on error if required."""

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input)
    if p.returncode and log_error:
        logger('cmd: ' + cmd)
        logger('RC: %s %s' % (p.returncode, error_message))
        if err:
            logger(err)
        if exit:
            sys.exit(1)
    return out, p.returncode, err


class Person(object):
    name = ''           # User name to represent it
    mac = None          # Full or partial MAC of user's phone
    presence = False    # Status
    ip = None
    ltsip = 0           # Last time seen IP --> refresh every day

    def __init__(self, name, mac):
        self.name = name
        self.mac = mac

    def __repr__(self):
        return '%s, %s, %s, %s' % (self.name, self.mac, self.ip, self.presence)

    def check_presence(self):
        if not self.ip:
            return False

        _, rc, _ = run_cmd('ping -c2 ' + self.ip, log_error=False)
        self.presence = rc == 0
        return self.presence


def check_presence():
    if all(get_ips()):
        # Run precise presence check
        for i in people:
            i.check_presence()
    else:
        # Use global scan to find missing IP.
        collect_ips()

    set_interval()


def check_ip_expiration():
    flag = False
    for i in people:
        if time.time() - i.ltsip > IP_EXPIRATON_S:
            i.ip = None  # Force nmap run by cleaning old IP
            flag = True

    return flag


def get_presence():
    return [i.presence for i in people]


def get_ips():
    return [i.ip for i in people]


def set_interval():
    global _interval
    _interval = TIMEOUT_LONG if any(get_presence()) else TIMEOUT_SHORT


def get_net():
    """Fill net variable for check_presence function in format ditted_ip/mask_bits."""

    global net
    out, _, _ = run_cmd("ifconfig | grep 'inet addr' | grep -v '127.0'")
    m = re.findall(':(\S+)', out)
    if len(m) < 3:
        print 'Error: Network configuration is weird.'
        sys.exit(9)

    net = m[0] + '/' + str(netaddr.IPAddress(m[2]).netmask_bits())


def collect_ips():
    """Fill IP addresses into people list. Return if all addresses collected or not."""

    out, rc, _ = run_cmd('sudo nmap -sn ' + net, log_error=False)
    if rc:
        print "Error: nmap is required. Run following command:"
        print "sudo apt-get -y install nmap"
        sys.exit(4)

    # Regex seeks IP @ pos 0 and MAC @ pos 2.
    addrs = re.findall('(?is)((\d+\.){3}\d+).*?(([\da-fA-F]{2}:?){6})', out)
    for a, b in enumerate(people):
        if b.mac in out.upper() and not b.ip:
            for g in addrs:
                if b.mac in g[2].upper():
                    people[a].ip = g[0]
                    people[a].presence = True  # Avoid extra ping
                    people[a].ltsip = time.time()

    return all(get_ips())


def main():
    try:
        # Read user list from file
        f = open('people.csv', 'r')
        l = f.read()
    except Exception:
        print "Error: Can't read file people.csv"
        sys.exit(2)

    print "Users expected:"
    ul = re.findall('(\S+),(\S+)', l)
    if not ul:
        print "Error: Empty file people.csv"
        sys.exit(8)

    for i in ul:
        try:
            people.append(Person(i[0], i[1].upper()))
            print people[-1]
        except IndexError:
            print "Error: Can't parse file people.csv. Check the file format: name,MAC"
            sys.exit(6)
        except Exception:
            print "Error: Can't process file people.csv"
            sys.exit(7)

    last_presence = get_presence()
    get_net()  # Assume that network properties don't change

    # Get IPs from MACs
    retries = 0
    while not collect_ips() and retries < 3:
        retries += 1

    while True:
        ts = time.time()
        print ">>> IP", "" if check_ip_expiration() else 'not', 'expired'
        check_presence()
        curr_presence = get_presence()
        if curr_presence != last_presence:
            # Report MQTT
            sl = []
            for i, p in enumerate(people):
                sl.append('{"name":"%s","changed":"%s","present":"%s"}' % (p.name, p.presence != last_presence[i], p.presence))
            msg = '[%s]' % ','.join(sl)
            publish.single("shm/rpi/presence/", msg)

            last_presence = curr_presence
            # Report to shell
            sts = [p.name + ((' ' if p.presence else ' dis') + 'appeared') for p in people]
            print 'Status change:', ', '.join(sts)
            print msg

        time.sleep(max(0, _interval - (time.time() - ts)))


# Use this trick to execute the file. Normally, it's a module to be imported.
if __name__ == "__main__":
    print 'Monitor person presence v' + VERSION
    main()
