#!/usr/bin/python

import paramiko
import sys

from argparse import ArgumentParser, ArgumentError

def main():
    parser = ArgumentParser(description="Ceph Operations")
    
    main_group = parser.add_mutually_exclusive_group(required=True)
    osd_group = parser.add_argument_group('OSD options',
                                    '-d (--device) required')
                                    
    main_group.add_argument('-M', '--monitor', action='store_true', help ='Add monitors')
    main_group.add_argument('-O', '--osd', action='store_true', help ='Add OSDs')
         
    parser.add_argument('-s', '--server',type=str, help='The ip-address of the server where the ceph component is needed to be installed ', required=True)
    parser.add_argument('-p', '--port', type=int,help='The Port no to connect', default=6789, required=True)
    
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    
    osd_group.add_argument('-d', '--device', help='Device to be used')

    try:
        args = parser.parse_args()
    except ArgumentError, exc:
        print exc.message, '\n', exc.argument
    
#    print "The status of osd is: ", args.osd
#    print "The status of mon is: " ,args.monitor
#    print "The ip_addr of the server is: ", args.server
#    print "The port no to connect is: ", args.port    
#    print "The device to be used as OSD is: ", args.device
#########    #TODO : Check for the presence of server    

def remote_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('ceph-node1', username='ceph', password='lol')
    stdin, stdout, stderr = ssh.exec_command("uptime")
    type(stdin)
    stdout.readlines()
    print "ashish chandra"

    stdin, stdout, stderr = ssh.exec_command("uptime")
    stdout.readlines()

if __name__ =="__main__":
    #remote_ssh()
     main()
