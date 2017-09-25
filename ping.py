#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re
import subprocess
import shlex

# MacOSX: 2 packets transmitted, 2 packets received, 0.0% packet loss
# Ubuntu: 2 packets transmitted, 2 received, 0% packet loss, time 1001ms
# RHEL  : 2 packets transmitted, 2 received, 0% packet loss, time 1001ms
re_ping = re.compile("(\d+) packets trans[^,]+, (\d+) [^,]+, ([\d\.]+)% packet loss")

def do_ping(addr, count=2, timeout=5, ping_cmd="/sbin/ping",
            ping_timeout_opt="-W", debug=False):
    cmd = shlex.split("%s -c %d %s %d %s" % (ping_cmd, count, ping_timeout_opt,
                                             timeout, addr))
    if debug:
        print("cmd: ", cmd)
    #
    tx = count
    rx = 0
    loss = 100.
    try:
        ret = subprocess.check_output(cmd)
    except OSError as e:
        raise
    except Exception as e:
        return { "tx":tx, "rx":rx, "loss":loss, "error":repr(e) }
    #
    # re_ping.match() does not work because the ret contains the whole lines
    # returned from the result of the ping.
    #
    r = re_ping.search(ret)
    if r:
        tx = int(r.group(1))
        rx = int(r.group(2))
        loss = float(r.group(3))
    return { "tx":tx, "rx":rx, "loss":loss, "error":"" }

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
    ret = do_ping(host, count=count, ping_timeout_opt="-t", debug=True)
    print("tx:%s rx:%s loss:%s%%" % (ret["tx"], ret["rx"], ret["loss"]))

