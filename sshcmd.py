#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import paramiko

class sshcmd():
    def __init__(self, server, username, password, port=22,
                 hostkey_file="~/.ssh/known_hosts",
                 mode="pwd", pkey_file="~/.ssh/id_rsa", debug=False):
        '''
        mode: "pwd" or "rsa"
        pkey_file: valid if mode is "rsa"
        '''
        if debug:
            paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        hostkey_file = os.path.expanduser(hostkey_file)
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys(hostkey_file)
        #
        if mode == "rsa":
            pkey_file = os.path.expanduser(pkey_file)
            pkey = paramiko.RSAKey.from_private_key_file(pkey_file,
                                                         password=password)
            self.ssh.connect(server, port=port,
                            username=username,
                            pkey=pkey,
                            allow_agent=False,
                            timeout=15, auth_timeout=15)
        elif mode == "pwd":
            self.ssh.connect(server, port=port,
                            username=username,
                            password=password,
                            allow_agent=False,
                            timeout=15, auth_timeout=15)

    def execcmd(self, cmd):
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
