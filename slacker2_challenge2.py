#!/usr/bin/python

import os
import getpass
import paramiko
import re
from scp import SCPClient

paramiko.util.log_to_file("auto_log")

def ping_check(hostname, username, password):
    """Function that does a Ping Check on the hosts"""
    """Usually the http_config only runs when the ping check is successful, but in this test, we run even when unsuccessful"""
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        print hostname + " is up"
        http_config(hostname, username, password)
    else:
        print hostname + " is down"
        http_config(hostname, username, password)
    exit



def createSSHClient(server, port, user, password):
    """This function is used to establish ssh connection """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def http_config(hostname, username, password):
    connect = createSSHClient(hostname, 22, username, password)

    """ Installing Apache on the servers"""
    print "\n Installing Apache on the Servers " 
    stdin, stdout, stderr = connect.exec_command('apt-get -y install apache2')
    error = stderr.readlines() 
    print 'This is output =',stdout.readlines()
    print 'This is error =',error
    k = 0
    for each in error:
        if re.search(r"No space left on device", each) != None:
#            space_cleanup(hostname, username, password)
            """Identifying the space usage culprit"""
            print "\n Identifying the space usage culprit "    
            stdin, stdout, stderr = connect.exec_command("lsof -s | grep /tmp/tmp | awk '{print $2}'")
            output = stdout.readlines()
            print 'This is output =',output
            print 'This is error =',stderr.readlines()
            process_kill = ''.join(output)
            print "The process to kill is : " + process_kill
            
            """killing the stray Process"""
            print "Killing the process %s to save space" %process_kill
            kill_command = "kill -9 " + process_kill
            print kill_command
            stdin, stdout, stderr = connect.exec_command(kill_command)
            print 'This is output =',stdout.readines()
            print 'This is error =',stderr.readlines()
            print "\n Trying Apache Installation again " 
            stdin, stdout, stderr = connect.exec_command('apt-get -y install apache2')
            error = stderr.readlines() 
            print 'This is output =',stdout.readlines()
            print 'This is error =',error
            break
    else:
        k += 1
    if k > 0:
        print k 
        print "Cleanup not Required"


    """Copying the index.php file"""
    print "\n Copying the Index.php file remotely"
    scp = SCPClient(connect.get_transport())
    scp.put(local_path, remote_path)

    """Customizing Apache on the servers"""
    print "\n Customizing Apache "    
    stdin, stdout, stderr = connect.exec_command('mv /var/www/html/index.html /var/www/html/index.html_backup')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()

    """Changing Permissions on index.php file"""
    print "\n Changing File permissions "    
    stdin, stdout, stderr = connect.exec_command('chown root:root /var/www/html/index.php')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()

    """Customizing Apache on the servers"""
    print "\n Changing File permissions "    
    stdin, stdout, stderr = connect.exec_command('chmod 644 /var/www/html/index.php')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()    
    
    """Restarting the Apache server"""
    print "\n Restarting the Apache Server " 
    stdin, stdout, stderr = connect.exec_command('service apache2 restart')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()
    
    """Verify that http server is up and can spit out Hello World"""
    print "\n Verifying http server"
    stdin, stdout, stderr = connect.exec_command('curl -sv "http://localhost"| grep -i hello')
    list_http = stdout.readlines()
    print 'This is output =',list_http
    print 'This is error =',stderr.readlines()
    i = 0
    for each in list_http:
        if re.search(r'Hello', each) != None:
            print "\n ***HTTP server is up and running with Hello World***\n\n\n"
            break
    else:
        i +=1
    if i > 0:
            print "\n ***HTTP Server does not have Hello World***\n\n\n"
    
    connect.close()
    
    

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
    ping_check(hostname, username, password)
