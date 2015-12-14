#!/usr/bin/python

import os
#import subprocess
#from subprocess import Popen
#import sys
import pexpect
from pexpect import pxssh


def ping_check(hostname, username, password):
    """Function that does a Ping Check on the hosts"""
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        print hostname + " is up"
        https_check(hostname, username, password)
    else:
        print hostname + " is down"
    exit


def https_check(hostname, username, password):
    try:
        s = pxssh.pxssh()
        s.login (hostname, username, password)
        s.sendline ('curl -sv \"http://ADDRESS\"')
        s.prompt
        print s.before
        if s.before == "Hello, world!\n":
            print hostname + " has http server up and running"
            customization(hostname, username, password)
        else:
            print hostname + " has http server down"
        exit
    except pxssh.ExceptionPxssh as e:
        print "pxssh failed on login."
        print str(e)
        
    


def http_check(hostname, username, password):
    """Function that does a http check on the host"""
    command_check = 'curl -sv \"http://ADDRESS\"'
    ssh = subprocess.Popen(["ssh", hostname, command_check], SHELL=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == "Hello, world!\n":
        print hostname + " has http server up and running"
        customization(hostname)
    else:
        print hostname + " has http server down"
        exit


def customization(hostname):
    """This will let you customize your options for the automation script"""
    print "customization for " + hostname

file_name = raw_input("Enter file name containing hostnames:")
username = raw_input("Enter username:")  
password = raw_input("Enter password:")

try:
    host_list = open(file_name, 'r')
except IOError:
    print "There was an error reading the file"

    
#for hostname in host_list:
#    ping_check(hostname)
