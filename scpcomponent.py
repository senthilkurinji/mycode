import json
import argparse
import paramiko
import sys,os,re
import datetime
import re

# parser = argparse.ArgumentParser(description='Deploy script for deploying servers')
# parser.add_argument('--jsonfile',help="Json file containing environment details",required=True)
# parser.add_argument('--password',help="password of Deploy servers")
# parser.add_argument("--env",help="path to look for",required=True)

# values=parser.parse_args()
# jsonfile= values.jsonfile
# password=values.password.strip()
# environment=values.env

done=[]
password=''

def scp_component(**kwargs):
    todo=kwargs['make_json']
    password=kwargs['password']
    #print  todo
    tasks(lines = todo, password = password)

def tasks(**kwargs):
    hosts=kwargs['lines']
    password=kwargs['password']
    #print hosts
    tasks=hosts
    machines=tasks["ipAddress"]
    user=tasks["bambooServiceAccount"]
    automation_path=tasks["automationPath"]
    automation_file=tasks["automationFile"]
    deployment_path = tasks["deploymentPath"]
    #print ("machin:{},use:{},automation_pa:{},automation_fi:{} ".format(machines,user,automation_path,automation_file))
    for machine in machines:
        print (machine)
        ssh=ssh_instance(machine,user,automation_path,automation_file,password,deployment_path)
        # if ssh == 1:
        #     print ("{}****ssh failure in {}".format(datetime.datetime.now(), os.path.splitext(automation_file)[0]))
        # elif ssh == 0:
        #     print ("{}****deployment failure in  {}".format(datetime.datetime.now(), os.path.splitext(automation_file)[0]))
        #     done.append(machine)
        # else:
        #     print ("{}****Deployment success in {}".format(datetime.datetime.now(), os.path.splitext(automation_file)[0]))

def ssh_instance(ip,username,automation_path,automation_file,password,deployment_path):
    try:
        #print "fdsghghghghghghghghghghghghghghghghghghghghghghghghghghghghghghhfgfhfg"
        ssh = paramiko.SSHClient()
        #print ssh
        ##print "ghfdggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
        #print "fdsfdsfsd"
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #print "sdfdsf"
        ssh.connect(ip, username=username, password=password)
        #print "fsdFdsfdsf"
        ssh.invoke_shell()
        print ("Connected")
        scp_stat = scp(ssh, username,automation_path,automation_file,deployment_path)
        if scp_stat == 0:
            print "[Deployment_s1]Copy the artifacts :: success"
        elif scp_stat == 1:
            print "[Deployment_SCP_STAT]SCP Failure"
    except Exception as e:
        print (e)
        return 1
    finally:
        if ssh:
            ssh.close()


def scp(ssh, username,automation_path,automation_file,deployment_path):
    copy_path = automation_path + automation_file
    transport = ssh.get_transport()
    session = transport.open_session()
    print "[File_transfer]SFTP Session creating from SSH connection transport"
    sftp = paramiko.SFTPClient.from_transport(transport)
    print "[File_transfer]SFTP Connection successul....."
    files_copied = True
    print files_copied
    #print("llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll")
    try:
        cmd = 'cp -r {}; '.format(automation_path)
        # print ("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx{}".format(cmd))
        stdin, stdout, stderr = ssh.exec_command(cmd)
        #cwd = os.getcwd()
        #print (cwd)
        #print(stdin)
        #print(stdout)
        #print(stderr)
        for line in stdout.readlines():
            print (line)
            #cwd = os.getcwd()
            #print (cwd)
            print ("gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg{}".format(line))
            return 0
        for line in stderr.readlines():
            print ("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx{}".format(line))
            return 1
    except Exception as e:
        print ("****command exec failure in  {}".format(e))


    #os.chdir(automation_path)
    #print os.path.abspath(os.curdir)
        # for file in automation_path:
        # if file == automation_file:
        #     try:
        #         print "[File_transfer]Copying File {}".format(file)
        #         status = sftp.put(deployment_path)
        #         files_copied = True
        #     except Exception as e:
        #         files_copied = False
        #         print "[File_transfer]Error in copying File {}".format(file)
        #         break
    if files_copied:
        return 0
    else:
        return 1

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description='Download Files from FTP and Push to stash')
#     parser.add_argument(
#         '--config_file', help="release config file", required=True)
#     parser.add_argument(
#         '--region', help="release region", required=True)
#     parser.add_argument(
#         '--env', help="release env", required=True)
#     parser.add_argument(
#         '--password', help="password for the component", required=True)
#
#
#
#     vars = parser.parse_args()
#     mdp_config_file = vars.config_file.strip()
#     region = vars.region.strip()
#     env = vars.env.strip()
#     password = vars.password.strip()



















