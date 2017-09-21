#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re
import subprocess
import shlex

re_ping = re.compile("(\d+) packets transmitted, (\d+) packets received, ([\d\.]+)% packet loss")

def do_ping(addr, count=2, timeout=5, ping_cmd="/sbin/ping", debug=False):
    cmd = shlex.split("%s -c %d -t %d %s" % (ping_cmd, count, timeout, addr))
    if debug:
        print("cmd: ", cmd)
    #
    tx = count
    rx = 0
    loss = 100.
    try:
        ret = subprocess.check_output(cmd)
    except Exception as e:
        return tx, rx, loss
    r = re_ping.search(ret)
    if r:
        tx = int(r.group(1))
        rx = int(r.group(2))
        loss = float(r.group(3))
    return tx, rx, loss

if __name__ == "__main__" :
    count = 2
    if len(sys.argv) == 2:
        host = sys.argv[1]
    elif len(sys.argv) == 3:
        host = sys.argv[1]
        count = int(sys.argv[2])
    else:
        print("Usage: %s (host) [count]" % (sys.argv[0]))
        exit(1)
    print("### pinging %s" % host)
    tx, rx, loss = do_ping(host, count=count, debug=True)
    print("tx:%s rx:%s loss:%s%%" % (tx, rx, loss))

