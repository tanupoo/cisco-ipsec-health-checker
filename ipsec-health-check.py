#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re
import argparse
from argparse import RawDescriptionHelpFormatter
import os
from ping import do_ping
from sshcmd import sshcmd
import logging
from logging.handlers import SysLogHandler as syslog

_NAME="ipsec-health-check"
_SHOW_SA_CMD="show crypto session"

def parse_args():
    p = argparse.ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            description="The IPsec end point health checker.",
            epilog="""
ENVIRONMENT VARIABLE:

  Instead of specifying the username and password in the argument, the
  environment variable of HLCHK_SSH_USR and HLCHK_SSH_PWD can be used
  to specify the username and password respectively.

NOTE:

  It does not look to define a general rule of the tag to pick the IP address
  of the peer assigned.  The known tags are like below:

  IKEv1 pre-shared key of ISR4000 IOS 16.5:
    IPSEC FLOW:.*host ([\w\d\.]+)

  IKEv2 RSA-SIG of ISR4000 IOS 16.5:
    Assigned address: ([\w\d\.]+)

""")
    p.add_argument("-s", required=True, action="store", dest="server",
        help="specify the server address.")
    p.add_argument("-u", action="store", dest="username",
        help="specify the user name to execute the command.")
    p.add_argument("-p", action="store", dest="password",
        help="specify the password for the user.")
    p.add_argument("--syslog", action="store_true", dest="f_syslog",
        help="enable to send a message to syslog. default is disable.")
    p.add_argument("--sshport", action="store", dest="ssh_port", type=int,
        default=22,
        help="specify the ssh port number. default is 22")
    p.add_argument("--sshmode", action="store", dest="ssh_mode",
        default="rsa",
        help="specify the ssh authentication mode. Either 'pwd' or 'rsa' can be specified. default is 'rsa'")
    p.add_argument("--timeout", action="store", dest="timeout", type=int,
        default=15,
        help="specify the timeout to pint. default is 15")
    p.add_argument("--tagtype", action="store", dest="tag_type",
        default="rsa", choices=["rsa", "psk"],
        help="specify the tag type to pick up the peer's IP address. default is 'rsa'")
    p.add_argument("--ping-timeout-opt", action="store",
        dest="ping_timeout_opt", default="-W",
        help="specify the option name of the ping timeout. default is '-W'")
    p.add_argument("--show-ipsec-session-command", action="store",
        dest="show_sa_cmd", default=_SHOW_SA_CMD,
        help="specify the command to show the ipsec session. default is 'show crypto session'")
    p.add_argument("--ping-command", action="store",
        dest="ping_cmd", default="/sbin/ping",
        help="specify the ping command. default is '/sbin/ping'.")
    p.add_argument("-v", action="store_true", dest="f_verbose", default=False,
        help="enable verbose mode.")
    p.add_argument("-d", action="append_const", dest="_f_debug", default=[],
        const=1, help="increase debug mode.")
    p.add_argument("--version", action="version", version="%(prog)s 0.2")

    args = p.parse_args()
    args.debug_level = len(args._f_debug)

    return args

'''
main
'''
opt = parse_args()

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

# setup logging
logger = logging.getLogger(_NAME)
if opt.f_syslog:
    ch = syslog(facility=syslog.LOG_USER)
    fmt = logging.Formatter(
            fmt="%(name)s:%(levelname)s: %(message)s")
else:
    ch = logging.StreamHandler()
    fmt = logging.Formatter(
            fmt="%(asctime)s:%(name)s:%(levelname)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S")
#
ch.setFormatter(fmt)
do_debug = False
if opt.debug_level:
    do_debug = True
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
#
logger.addHandler(ch)

#
if opt.tag_type == "psk":
    # ISR4000 IOS 16.5 IKEv1 PSK
    re_host = re.compile("IPSEC FLOW:.*host ([\w\d\.]+)")
elif opt.tag_type == "rsa":
    # ISR4000 IOS 16.5 IKEv2 RSA
    re_host = re.compile("Assigned address: ([\w\d\.]+)")
else:
    logger.error("ERROR: invalid tag type.")
    exit(1)

#
# start
#
logger.info("start ipsec-health-check")

ssh = sshcmd(opt.server, opt.username, opt.password,
             port=opt.ssh_port, mode=opt.ssh_mode, debug=do_debug)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.execcmd(opt.show_sa_cmd)

for line in ssh_stdout:
    if opt.debug_level > 1:
        logger.debug(line)
    r = re_host.search(line)
    if r:
        addr = r.group(1)
        ret = do_ping(addr, ping_timeout_opt=opt.ping_timeout_opt,
                      ping_cmd=opt.ping_cmd,
                      debug=do_debug)
        if opt.f_verbose or opt.debug_level:
            logger.info("addr:%s, tx:%s, rx:%s, loss:%s%%" % (addr, ret["tx"],
                                                        ret["rx"], ret["loss"]))
        if ret["loss"] > 99:
            logger.warn("%s is not stable." % addr)

ssh.close()

logger.info("end ipsec-health-check")
logging.shutdown()
