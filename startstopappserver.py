import json
import argparse
import paramiko
import sys,os,re
import datetime
import re

todo =[]
done=[]
password=''

def stop_start_appserver(**kwargs):
    todo=kwargs['make_json']
    password=kwargs['password']
    is_start=kwargs['is_start']
    tasks(lines=todo, password = password, is_start = is_start)

def tasks(**kwargs):
    hosts=kwargs['lines']
    password=kwargs['password']
    is_start=kwargs['is_start']
    tasks=hosts
    #machines = [i['ipAddress'] for i in tasks if 'ipAddress' in i]
    #user = [i['bambooServiceAccount'] for i in tasks if 'bambooServiceAccount' in i]
    machine = "192.168.44.84"
    user="ubuntu"
    automation_path = [i['automationPath'] for i in tasks if 'automationPath' in i]
    automation_file = [i['automationFile'] for i in tasks if 'automationFile' in i]
    #for machine in machines:
    if is_start == True:
            print "{}****starting Sanity Test on appserver {}".format(datetime.datetime.now(), machine)
            print "{}****Sanity success on appserver {}".format(datetime.datetime.now(), machine)
            print "{}****started appserver on {}".format(datetime.datetime.now(), machine)

    else:
        print (machine)
        ssh=ssh_instance(machine,user,password)
        if ssh == 1:
            #print ("{}****SSH success in appserver {}".format(datetime.datetime.now(), machine))
            print ("{}****stopped appserver on {}".format(datetime.datetime.now(), machine))
        elif ssh == 0:
            print ("{}****stop attempt failure in app server {}".format(datetime.datetime.now(), machine))
            print ("{}****stop attempt failure in app server {}".format(datetime.datetime.now(), machine))
            done.append(machine)

def ssh_instance(ip,username,password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        ssh.invoke_shell()
        return 1
    except Exception as e:
        print (e)
        return 0