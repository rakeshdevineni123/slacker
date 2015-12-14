#!/usr/bin/python

import os
#import pexpect
from pexpect import pxssh
import getpass
import paramiko
from paramiko import SSHClient
from scp import SCPClient


def ping_check(hostname, username, password):
    """Function that does a Ping Check on the hosts"""
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        print hostname + " is up"
        http_config(hostname, username, password)
    else:
        print hostname + " is down"
        http_config(hostname, username, password)
    exit


def createSSHClient(server, port, user, password):
    """This function is used to remotely copy the files"""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def http_config(hostname, username, password):
    try:
        s = pxssh.pxssh()
        s.login (hostname, username, password)   
        
        """Installing Apache on the servers"""
        print "Installing Apache on the Servers \n"
        s.sendline('apt-get -y install apache2')
        s.prompt
        print s.before
        
        s.sendline('mv /var/www/html/index.html /var/www/html/index.html_backup')
        s.prompt
        print s.before
        
        """Changing Permissions on index.php file"""
        print "Changing File permissions"
        s.sendline('chown root:root /var/www/html/index.php')
        s.prompt
        print s.before
        s.sendline('chmod 644 /var/www/html/index.php')
        s.prompt
        print s.before
        
        """Restarting the Apache server"""
        s.sendline('service apache2 restart')
        s.prompt
        print s.before
        
        """Verify that http server is up and can spit out Hello World"""
        print "Verifying http server"
        s.sendline ('curl -sv \"http://ADDRESS\"')
        s.prompt
        print s.before
        if s.before == "Hello, world!\n":
            print hostname + " has http server up and running"
        else:
            print hostname + " has http server down"
        s.logout()
    except pxssh.ExceptionPxssh as e:
        print "pxssh failed on login."
        print str(e)


file_name = raw_input("Enter file name containing hostnames:")
username = raw_input("Enter username:")  
password = getpass.getpass('password: ')
local_path = '/Users/rdevineni/Documents/slack/files/index.php'
remote_path = '/var/www/html/'

try:
    content = open(file_name, 'r')
except IOError:
    print "There was an error reading the file"

host_list = content.read().splitlines()

for hostname in host_list:    
    print "Copying the Index.php file remotely"
    ssh = createSSHClient(hostname, 22, username, password)
    scp = SCPClient(ssh.get_transport())
    scp.put(local_path, remote_path)
    ping_check(hostname, username, password)
