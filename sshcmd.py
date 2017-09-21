#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import paramiko

'''
test code
'''
class sshcmd():
    def __init__(self, server, username, password, port=22,
                 keyfile="~/.ssh/known_hosts", debug=False):
        if debug:
            paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        keys = os.path.expanduser(keyfile)
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys(keys)
        self.ssh.connect(server, port=port,
                    username=username, password=password,
                    allow_agent=False,
                    timeout=15, auth_timeout=15)

    def execcmd(self, cmd):
        #ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
        return self.ssh.exec_command(cmd)

    def close(self):
        return self.ssh.close()

if __name__ == "__main__" :
    if len(sys.argv) < 5:
        print("Usage: %s (server) (username) (password) (cmd...)" %
              (sys.argv[0]))
        exit(1)
    #
    server = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    #
    ssh = sshcmd(server, username, password, debug=True)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.execcmd("".join(sys.argv[4:]))
    #
    print("STDIN:", type(ssh_stdin))
    print("STDOUT:", type(ssh_stdout))
    print("STDERR:", type(ssh_stderr))
    print("====")
    #
    for line in ssh_stdout:
        print(line.rstrip())
    #
    ssh.close()
