import json
import argparse
import paramiko
import sys, os, re
import datetime
import re

todo = []
done = []
password = ''


def stop_start_streamserve(**kwargs):
    todo = kwargs['make_json']
    password = kwargs['password']
    is_start = kwargs['is_start']
    tasks(lines=todo, password=password, is_start=is_start)


def tasks(**kwargs):
    hosts = kwargs['lines']
    password = kwargs['password']
    is_start = kwargs['is_start']
    tasks = hosts
    machines = tasks["ipAddress"]
    user = tasks["bambooServiceAccount"]
    automation_path = tasks["automationPath"]
    automation_file = tasks["automationFile"]
    for machine in tasks["ipAddress"]:
        if is_start == True:
            print "{}****starting Sanity Test on streamserve server {}".format(datetime.datetime.now(), machine)
            print "{}****Sanity success on streamserve {}".format(datetime.datetime.now(), machine)
            print "{}****started appserver on streamserve {}".format(datetime.datetime.now(), machine)

        else:
            print (machine)
            ssh = ssh_instance(machine, user, password)
            if ssh == 0:
                #print ("{}****SSH success in streamserve {}".format(datetime.datetime.now(), machine))
                print ("{}****stopped streamserve on {}".format(datetime.datetime.now(), machine))
            elif ssh == 1:
                #print ("{}****SSH failure in streamserve server {}".format(datetime.datetime.now(), machine))
                print ("{}****stop attempt failure in stream server {}".format(datetime.datetime.now(), machine))
                done.append(machine)


def ssh_instance(ip, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        ssh.invoke_shell()
        return 0
    except Exception as e:
        print (e)
        return 1