#!/usr/bin/python

# Script to add or remove OSD from fully functional ceph cluster

import os
import paramiko
import subprocess
import sys

from argparse import ArgumentParser, ArgumentError


#TODO : Validate passed arguments to the script
def validate_args(args):
    pass

def execute_shell_command(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    while True:
        out = p.stdout.read(1)
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            return out   
       
def remote_ssh(server, username, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username)
    stdin, stdout, stderr = ssh.exec_command(command)
    for line in stdout.readlines():
        print line    

def main():
    parser = ArgumentParser(description="OSD Operations")
      
    main_group = parser.add_mutually_exclusive_group(required=True)      
    main_group.add_argument('-A', '--add_osd', action='store_true', help ='Add New OSDS')
    main_group.add_argument('-R', '--remove_osd', action='store_true', help ='Remove OSDs')
         
    parser.add_argument('-s', '--server',type=str, help='The ip-address of the server', required=True)
    parser.add_argument('-u', '--username', type=str, help='The username for the server', default='ceph')
    parser.add_argument('-f', '--fs_type', type=str, help='The file_system to be used', default='xfs')
    parser.add_argument('-d', '--device', help='Device to be used', required=True)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-c', '--conf_dir', help='Ceph home directory', required=True)  

    try:
        args = parser.parse_args()
    except ArgumentError, exc:
        print exc.message, '\n', exc.argument
        
    if args.server:
        server = args.server
        
    if args.device:
        device = args.device  
        
    if args.fs_type:
        fs_type = args.fs_type
   
    if args.conf_dir:
        home_dir = args.conf_dir
    
    print "The ip_addr of the server is: ", server
    print "The device to be used as OSD is: ", device
    print "The file system to be used is: ", fs_type
   
    validate_args(args)

    '''
        Create the OSD. If no UUID is given, it will be set automatically
        when the OSD starts up
    '''

    osd_create_command='ceph osd create'
    osd_no = execute_shell_command(osd_create_command)
    
    '''
       Create the default directory on your new OSD.
    '''
    
    osd_dir = 'sudo mkdir -p /var/lib/ceph/osd/ceph-%s' %(osd_no)
    remote_ssh(server, args.username, osd_dir) 
    
    '''
        If the OSD is for a drive other than the OS drive, prepare it for use 
        with Ceph, and mount it to the directory you just created
       
        Create and mount the device
    '''   
    
    format_system = 'sudo mkfs -t %s -f /dev/%s' %(fs_type, device)
    remote_ssh(server, args.username, format_system)
    mount_command = 'sudo mount  /dev/%s /var/lib/ceph/osd/ceph-%s' %(device, osd_no)
    remote_ssh(server, args.username, mount_command)
    
    '''
       Install ceph on the new node and copy configurations file
       from admin node in /etc/ceph directory
    '''   
    os.chdir(home_dir)
    command = 'ceph-deploy install %s' %(server)
    execute_shell_command(command)
    
    '''
       Copy configurations file to a new node using ceph-deploy
    '''
    
    command = 'ceph-deploy admin %s' %(server)
    execute_shell_command(command)
    
    
    '''
       Initialize the OSD data directory.
    '''
    init_command = 'sudo ceph-osd -i %s --mkfs --mkkey' %(osd_no)
    remote_ssh(server, args.username, init_command)
    
    '''
       Register ceph osd key
    '''
    
    register_command = 'sudo ceph auth add osd.%s osd "allow *" mon "allow rwx" -i /var/lib/ceph/osd/ceph-%s/keyring' %(osd_no, osd_no)
    remote_ssh(server, args.username, register_command)
    
    '''
       Add node to the bucket
    '''
    
    command = 'ceph osd crush add-bucket %s host' %(server)
    remote_ssh(server, args.username, command)
    
    command = 'ceph osd crush move %s root=default' %(server)
    remote_ssh(server, args.username, command)
    
    '''
       Add OSD to crush map
    '''
    
    command = 'ceph osd crush add osd.%s 1.0 host=%s' %(osd_no, server)  ## may need to change
    remote_ssh(server, args.username, command)
    
    '''
       Start the OSD
    '''
    
    start_command = 'sudo start ceph-osd id=%s' %(osd_no)
    remote_ssh(server, args.username, start_command)
        


if __name__ =="__main__":
    main()
