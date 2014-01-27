#!/usr/bin/python

import paramiko
import subprocess
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
    parser.add_argument('-p', '--port', type=int,help='The Port no to connect', default=6789)
    parser.add_argument('-u', '--username', type=str, help='The username for the server', default='ceph')
    
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    
    osd_group.add_argument('-d', '--device', help='Device to be used')

    try:
        args = parser.parse_args()
    except ArgumentError, exc:
        print exc.message, '\n', exc.argument
        
    if args.server:
        server = args.server
        
    if args.device:
        device = args.device

    if args.port:
        port_no = args.port    
        
   
    
#    print "The status of osd is: ", args.osd
#    print "The status of mon is: " ,args.monitor
#    print "The ip_addr of the server is: ", args.server
#    print "The port no to connect is: ", args.port
#    print "The device to be used as OSD is: ", args.device
#########TODO : Check for the presence of server    



    ## Create the OSD. If no UUID is given, it will be set automatically when the OSD starts up
    osd_create_command='sudo ceph osd create'
    osd_no = execute_shell_command(osd_create_command)
    
    ##Create the default directory on your new OSD.    
    osd_dir = 'sudo mkdir -p /var/lib/ceph/osd/ceph-%s' %(osd_no)
    remote_ssh(server, args.username, osd_dir) 
    
    ##If the OSD is for a drive other than the OS drive, prepare it for use with Ceph, and mount it to the directory you just created
    
    ##Create and mount the device
    format_system = 'sudo mkfs -t xfs -f /dev/%s' %(device)
    remote_ssh(server, args.username, format_system)
    mount_command = 'sudo mount  /dev/%s /var/lib/ceph/osd/ceph-%s' %(device, osd_no)
    remote_ssh(server, args.username, mount_command)
    
    ##Initialize the OSD data directory.
    init_command = 'ceph-osd -i %s --mkfs --mkkey' %(osd_no)
    remote_ssh(server, args.username, init_command)
    
    
    ### Register ceph osd key
    
    register_command = 'ceph auth add osd.%s osd "allow *" mon "allow rwx" -i /var/lib/ceph/osd/ceph-%s/keyring' %(osd_no, osd_no)
    remote_ssh(server, args.username, register_command)

    ### Add OSD to crush map

    command = 'ceph osd crush add osd.%s' %(osd_no)  ## may need to change
    
    
    #### Start the OSD
    start_command = 'sudo start ceph-osd id=%s' %(osd_no)


    
def execute_shell_command(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output,err = p.communicate()
    print output
    return output    
    
def remote_ssh(server, username, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username)
    stdin, stdout, stderr = ssh.exec_command(command)
    for line in stdout.readlines():
        print line

    stdin, stdout, stderr = ssh.exec_command("uptime")
    stdout.readlines()

if __name__ =="__main__":
    main()
