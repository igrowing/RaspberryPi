#!/usr/bin/env python3
import os
import re
import sys
import json
import time
import subprocess
from pprint import pprint
from threading import Thread

VERSION = '0.1'

### JSON configuration file protocol:
# {
#   "device_name": {
#     "protocol_name": {
#       "command": "",   // use single quotes ' if needed
#       "expected": "",
#       "timeout": 10,   // optional
#       "retries": 1,    // optional
#       "ok_msg": "OK",  // optional
#       "err_msg": "Cannot ping"
#     }
#   }
# }



def print_help(err=''):
    print('Usage:', file=sys.stderr)
    print(f'{__file__} [config.json]', file=sys.stderr)
    print(err, file=sys.stderr)


def run_cmd(cmd, input=None, exit=False):
    """Run a command, optionally logging error message if return code not zero. Exit program on error if required."""

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input)
    if p.returncode and exit:
        sys.exit(1)
    return out.decode('utf-8'), p.returncode, err.decode('utf-8')


def process(details):
    cmd = details["command"].replace("'", '"')
    exp = details["expected"]
    tout = details.get("timeout", 10)
    retr = details.get("retries", 1)
    details['result'] = 1

    while retr >= 0:
        retr -= 1
        out, rc, err = run_cmd(f'timeout {tout} {cmd}')
        if re.search(exp, out + err):
            return

        # Interval before retry
        time.sleep(5)

    details['result'] = 0


if __name__ == "__main__":
    print('Nagios-lite-like v' + VERSION, file=sys.stderr)
    args = sys.argv
    fn = args[1] if len(args) > 1 else 'config.json'
    try:
        f = open(fn, 'r')
        config = f.read()
    except (OSError, IOError):
        print_help(f'File {args[1]} not found.', file=sys.stderr)
        sys.exit()

    jd = json.loads(config)
    ts = time.time()
    jobs = []
    for k, v in jd.items():
        for p, d in v.items():
            jobs.append(Thread(target=process, args=(d,)))
            jobs[-1].start()

    for j in jobs:
        j.join()

    res = {}
    for k, v in jd.items():
        res[k] = {}
        # Check all results are positive.
        prelim = all(d["result"] for d in list(v.values()))
        # Add only summary verdict for positive check.
        if prelim:
            res[k]['status'] = 'OK'
        else:
            # Elaborate details of failed check
            for p, d in v.items():
                res[k][p] = d["ok_msg"] if d["result"] else "Error: " + d["err_msg"]
                # print(f'Device: {k}, Protocol: {p}, Result: {d["ok_msg"] if d["result"] else d["err_msg"]}')

    print(json.dumps(res).replace(' "', '"').replace(' {', '{'))
    print(f'Completed in {time.time() - ts} seconds.', file=sys.stderr)
