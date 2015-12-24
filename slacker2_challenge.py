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

    """ Checking disk space"""
    print "\n Checking Disk space " 
    stdin, stdout, stderr = connect.exec_command('df -h | grep 100%')
    output = stdout.readlines() 
    print 'This is output =',output
    print 'This is error =',stderr.readlines()
    k = 0
    for each in output:
        if re.search(r"/dev/xvda1", each) != None:
            print each
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
            print 'This is output =',stdout.readlines()
            print 'This is error =',stderr.readlines()
            break
    else:
        k += 1
    if k > 0:
        print k 
        print "Cleanup not Required"
    
    """Copying the resolv.conf file"""
    print "\n Copying the Resolv.conf file remotely for lookups"
    scp = SCPClient(connect.get_transport())
    scp.put(local_path_resolv, remote_path_resolv)
    

    """ Update apt-get Sources before installing"""
    print "\n Update apt-get Sources before installing "    
    stdin, stdout, stderr = connect.exec_command('apt-get update')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()
    
    """ Check for port 80 usage"""
    print "\n Checking Port 80 usage "
    command = "lsof -i :80 | awk '{print $2}' | grep -v PID"
    stdin, stdout, stderr = connect.exec_command(command)
    output = stdout.readlines() 
    print 'This is output =',output
    print 'This is error =',stderr.readlines()
    for each in output:
        print "This process is listening on port 80 and will be killed: ", each
        kill_command = 'kill -9 ' + each
        stdin, stdout, stderr = connect.exec_command(kill_command)
        print 'This is output =',stdout.readlines()
        print 'This is error =',stderr.readlines()
        
    
    """Removing the iptable Rule that DROPS http connections"""
    print "\n Removing the iptable Rule that DROPS http connections"
    stdin, stdout, stderr = connect.exec_command('iptables -D INPUT -p tcp --dport http -j DROP')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()
    
    """ Installing php on the servers"""
    print "\n Installing php5 on the Servers "    
    stdin, stdout, stderr = connect.exec_command('apt-get -y install php5')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()

    """ Installing Apache on the servers"""
    print "\n Installing Apache on the Servers "    
    stdin, stdout, stderr = connect.exec_command('apt-get -y install apache2')
    print 'This is output =',stdout.readlines()
    print 'This is error =',stderr.readlines()

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
local_path_resolv = '/Users/rdevineni/Documents/slack/files/resolv.conf'
remote_path_resolv = '/etc/resolv.conf'

try:
    content = open(file_name, 'r')
except IOError:
    print "There was an error reading the file"

host_list = content.read().splitlines()

for hostname in host_list:    
    http_config(hostname, username, password)
