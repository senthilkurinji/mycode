import json
import argparse
import paramiko
import sys,os,re
import datetime
import re

todo =[]
done=[]
password=''


def stop_start_beserver(**kwargs):
    todo=kwargs['make_json']
    password=kwargs['password']
    is_start=kwargs['is_start']
    tasks(lines=todo, password=password, is_start=is_start)
    
def tasks(**kwargs):
    hosts=kwargs['lines']
    password=kwargs['password']
    is_start=kwargs['is_start']
    tasks=hosts
    #machines = [i['ipAddress'] for i in tasks if 'ipAddress' in i]
    ip = "192.168.44.84"
    print ip
    #user = [i['bambooServiceAccount'] for i in tasks if 'bambooServiceAccount' in i]
    user = "ubuntu"
    automation_path=[i['automationPath'] for i in tasks if 'automationPath' in i]
    automation_file=[i['automationFile'] for i in tasks if 'automationFile' in i]
    #print ("machin:{},use:{},automation_pa:{},automation_fi:{} ".format(machines,user,automation_path,automation_file))
    #for machine in machines:



    #print ("machin:{},use:{},automation_pa:{},automation_fi:{} ".format(machines, user, automation_path,automation_file))
    if is_start == True:
            print "{}****starting Sanity Test on backend server {}".format(datetime.datetime.now(), ip)
            print "{}****Sanity success on backend {}".format(datetime.datetime.now(), ip)

    else:
        #print (machine, password)
        print "myyyyyyyyyyyyyyyyyyyyyyyyyyy {}".format(ip)
        print user
        print password
        ssh=ssh_instance(ip,user,password)
        if ssh==0:
            #print ("{}****SSH success in backend server {}".format(datetime.datetime.now(), machine))
            print "{}****stopped backend on {}".format(datetime.datetime.now(), ip)
        if ssh == 1:
            #print ("{}****SSH failure in backend server {}".format(datetime.datetime.now(), machine))
            print ("{}****stop attempt failure in backend server {}".format(datetime.datetime.now(), ip))
            done.append(ip)


def ssh_instance(ip,username,password):
    try:
        print "****check check"
        print ip
        print username
        print password
        ssh = paramiko.SSHClient()
        print "****check check checky"
        print ip
        print username
        print password
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print "****check check checkm"
        ssh.connect(ip, username=username, password=password)
        print "****check check checkllllllllllll"
        ssh.invoke_shell()
        print "****check sjshs"
        print ip
        print username
        print password
        print ("Connected")
        return 0
    except Exception as e:
        print (e)
        return 1

