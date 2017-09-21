#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re
import argparse
import os
from ping import do_ping
from sshcmd import sshcmd

def parse_args():
    p = argparse.ArgumentParser(
            description="The IPsec end point health checker.",
            epilog="Instead of specifying the username and password in the argument, the environment variable of HLCHK_SSH_USR and HLCHK_SSH_PWD can be used to specify the username and password respectively.")
    p.add_argument("-s", required=True, action="store", dest="server",
        help="specify the server address.")
    p.add_argument("-u", action="store", dest="username",
        help="specify the user name to execute the command.")
    p.add_argument("-p", action="store", dest="password",
        help="specify the password for the user.")
    p.add_argument("--sshport", action="store", dest="sshport", type=int,
        default=22,
        help="specify the ssh port number. default is 22")
    p.add_argument("--timeout", action="store", dest="timeout", type=int,
        default=15,
        help="specify the timeout to pint. default is 15")
    p.add_argument("--tagtype", action="store", dest="tag_type",
        default="rsa",
        help="Either 'rsa' or 'psk' can be specified to pick the IP address of the peer assigned. default is psk")
    p.add_argument("-v", action="store_true", dest="f_verbose", default=False,
        help="enable verbose mode.")
    p.add_argument("-d", action="append_const", dest="_f_debug", default=[],
        const=1, help="increase debug mode.")
    p.add_argument("--verbose", action="store_true", dest="f_verbose",
        default=False, help="enable verbose mode.")
    p.add_argument("--version", action="version", version="%(prog)s 1.0")

    args = p.parse_args()
    args.debug_level = len(args._f_debug)

    return args

'''
test code
'''
opt = parse_args()

do_debug = False
if opt.debug_level:
    do_debug = True

if not opt.username:
    opt.username = os.getenv("HLCHK_SSH_USR")
    if not opt.username:
        print("ERROR: username is required.")
        exit(1)

if not opt.password:
    opt.password = os.getenv("HLCHK_SSH_PWD")
    if not opt.password:
        print("ERROR: password is required.")
        exit(1)

#
cmd = "show crypto session"

ssh = sshcmd(opt.server, opt.username, opt.password,
             port=opt.sshport, debug=do_debug)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.execcmd(cmd)

if opt.tag_type == "psk":
    # ISR4000 IOS 16.5 IKEv1 PSK
    re_host = re.compile("IPSEC FLOW:.*host ([\w\d\.]+)")
elif opt.tag_type == "rsa":
    # ISR4000 IOS 16.5 IKEv2 RSA
    re_host = re.compile("Assigned address: ([\w\d\.]+)")
else:
    print("ERROR: invalid tag type.")
    exit(1)

for line in ssh_stdout:
    if opt.debug_level > 1:
        print(line)
    r = re_host.search(line)
    if r:
        addr = r.group(1)
        print("addr: %s" % addr)
        tx, rx, loss = do_ping(addr, debug=do_debug)
        if loss > 99:
            print("%s is not stable." % addr)

ssh.close()
