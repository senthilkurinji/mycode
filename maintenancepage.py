import json
import argparse
import paramiko
import sys,os,re
import datetime
import re

todo =[]
done=[]
password=''

def maintainence_page(**kwargs):
    todo=kwargs['make_json']
    password=kwargs['password']
    is_start=kwargs['is_start']
    tasks(lines = todo, password = password, is_start = is_start)

def tasks(**kwargs):
    hosts=kwargs['lines']
    password=kwargs['password']
    is_start=kwargs['is_start']
    tasks=hosts
    print tasks
    #val_new = [i['ipAddress'] for i in tasks if 'ipAddress'in i]
    machines=[i['ipAddress'] for i in tasks if 'ipAddress'in i]
    user=[i['bambooServiceAccount'] for i in tasks if 'bambooServiceAccount'in i]
    try:
        if is_start == True:
            print ("{}****maintenence page enabled in webserver {} by {}".format(datetime.datetime.now(),machines,user))
        else:
            print ("{}****maintenence page disabled in webserver {} by {}".format(datetime.datetime.now(),machines,user))
    except Exception as e:
        print (e)


