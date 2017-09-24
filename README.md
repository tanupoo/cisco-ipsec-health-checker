Simple IPsec health checker for Cisco router
============================================

It just logins into the Cisco router you specified at the argument.
And, it takes a set of IP addresses which are assigned to the peer
for the IPsec tunnel.
Then, it tries to send some ping packets to each of them.

The default timeout is 15 seconds for each ping.
Please note that it takes 15 seconds multiplied
by the number of peers at most to check the all peers.

## REQUIREMENT

- python2.7.  python3 is not tested.
- [paramiko](http://www.paramiko.org/), a python module for ssh.  The instruction to install paramiko is [here](http://www.paramiko.org/installing.html).

## USAGE

    ipsec-health-check.py [-h] -s SERVER [-u USERNAME] [-p PASSWORD]
                             [--sshport SSH_PORT] [--sshmode SSH_MODE]
                             [--timeout TIMEOUT] [--tagtype TAG_TYPE] [-v]
                             [-d] [--verbose] [--version]

    optional arguments:
      -h, --help          show this help message and exit
      -s SERVER           specify the server address.
      -u USERNAME         specify the user name to execute the command.
      -p PASSWORD         specify the password for the user.
      --sshport SSH_PORT  specify the ssh port number. default is 22
      --sshmode SSH_MODE  specify the ssh authentication mode. Either 'pwd' or
                          'rsa' can be specified. default is 'pwd'
      --timeout TIMEOUT   specify the timeout to pint. default is 15
      --tagtype TAG_TYPE  specify the tag type to pick up the peer's IP address.
                          Either 'rsa' or 'psk' can be specified. default is 'psk'
      -v                  enable verbose mode.
      -d                  increase debug mode.
      --verbose           enable verbose mode.
      --version           show program's version number and exit
    
    ENVIRONMENT VARIABLE:
    
      Instead of specifying the username and password in the argument, the
      environment variable of HLCHK_SSH_USR and HLCHK_SSH_PWD can be used
      to specify the username and password respectively.
    
    NOTE:
    
      It does not look to define a general rule of the tag to pick
      the IP address of the peer assigned.  The known tags are like below:
    
        IKEv1 pre-shared key of ISR4000 IOS 16.5:
          IPSEC FLOW:.*host ([\w\d\.]+)
    
        IKEv2 RSA-SIG of ISR4000 IOS 16.5:
          Assigned address: ([\w\d\.]+)

