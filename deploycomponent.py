import json
import argparse
import paramiko
import sys,os,re
import datetime
import re
import componentbuild as cb
import configdata as cd

done=[]
password=''
is_not_mdp = 'true'
workdir = ''
res_json = {}
temp_dict =[]
make_json_new = {"data": {}}
def deploy_component(**kwargs):
    todo=kwargs['make_json_new']
    password=kwargs['password']
    release_component=kwargs["release_component"]
    print region
    print "make_ json file {}".format(todo)
    tasks(lines = todo, password = password, release_component=release_component)

def tasks(**kwargs):
    hosts=kwargs['lines']
    password=kwargs['password']
    release_component = kwargs["release_component"]
    print hosts
    task=hosts
    valu = (task.values())
    for tasks in valu:
        print tasks
        #print(items["automationPath"])
        # machines = [i['ipAddress'] for i in tasks if 'ipAddress' in i]
        ip = "192.168.44.84"
        print ip
        # user = [i['bambooServiceAccount'] for i in tasks if 'bambooServiceAccount' in i]
        user = "ubuntu"
        print region
        iter = tasks[region]
        print(iter)
        iter_val = (iter[0])
        print iter[0][release_component]["automationPath"]
        automation_path = iter[0][release_component]["automationPath"]
        automation_file = iter[0][release_component]["automationFile"]
    print ("machin:{},use:{},automation_pa:{},automation_fi:{} ".format(ip,user,automation_path,automation_file))
    #for machine in tasks["ipAddress"]:
    #print (machine)
    ssh=ssh_instance(ip,user,automation_path,automation_file,password,workdir)
    if ssh == 0:
        print ("{}****deployment success in {}".format(datetime.datetime.now(), os.path.splitext(automation_file)[0]))
    elif ssh == 1:
        print ("{}****deployment failure in  {}".format(datetime.datetime.now(), os.path.splitext(automation_file)[0]))
        stripped = os.path.splitext(automation_file)[0]
        print ("ccccccccccccccccccccccccccccccc {}".format(stripped))
        done.append(ip)
        #print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
        #print ("wwwwwwwwwwzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz{}".format(release_component))
        #for items in release_component:
            #print "iemssssss {}".format(items)
        if stripped == "backendserver":
            print( "RollBack started for Backend server,inform DBA")
            print("RollBack success for Backend server and informed DBA ")
        elif stripped == "appserve":
            print("RollBack started for Backend server,app server and inform DBA")
            print("RollBack success for Backend server,app server and informed DBA ")
        elif stripped == "database":
            print("inform DBA on failure")
            print("inform DBA on failure ")
        elif stripped == "crmportal":
            print("RollBack started for crmplus")
            print("RollBack success for crmplus")
        elif stripped == "streamserve":
            print("RollBack started for streamServe")
            print("RollBack success for streamServe")
    elif ssh == 0:
        print ("{}****Deployment success in {}".format(datetime.datetime.now(), os.path.splitext(automation_file)[0]))


def scp(ssh, username,automation_path,workdir):
    print (automation_path)
    print (workdir)
    #copy_path = automation_path + automation_file
    transport = ssh.get_transport()
    session = transport.open_session()
    print "[File_transfer]SFTP Session creating from SSH connection transport"
    sftp = paramiko.SFTPClient.from_transport(transport)
    print "[File_transfer]SFTP Connection successul....."
    files_copied = True
    print files_copied
    #print("llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll")
    try:
        print "current directory ()".format (os.getcwd())
        print (automation_path)
        print (workdir)
        cmd = 'cd {}; pwd ; ls ; cp -r src/* {}'.format(workdir,automation_path)
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
            return 0
        for line in stderr.readlines():
            print ("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx{}".format(line))
            return 1
    except Exception as e:
        print ("****command exec failure in  {}".format(e))

def ssh_instance(ip,username,automation_path,automation_file,password,workdir):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        ssh.invoke_shell()
        print ("Connected")
        scp_stat = scp(ssh, username, automation_path,workdir)
        if scp_stat == 0:
            print "[Deployment_s1]Copy the artifacts :: success"
            # try:
            #     cmd = 'cd {};./{} '.format(automation_path, automation_file)
            #     stdin, stdout, stderr = ssh.exec_command(cmd)
            #     #print(stdin)
            #     #print(stdout)
            #     #print(stderr)
            #     for line in stdout.readlines():
            #         print (line)
            #         return 0
            #     for line in stderr.readlines():
            #         print (line)
            #         return 1
            # except Exception as e:
            #     print ("****command exec failure in  {}".format(e))
        elif scp_stat == 1:
            print "[Deployment_SCP_STAT]SCP Failure"

    except Exception as e:
            print ("****ssh failure in  {}".format(e))

    finally:
        if ssh:
            ssh.close()

def deploy_main(env, region, password,mdp_config_file,release_component):
    print "deploy main"
    print region
    print env
    print password
    print mdp_config_file
    print release_component
    make_json_new["data"].update(cd.get_config_data(country=region, input_file=mdp_config_file,env=env, release_component=release_component,res_json=res_json,temp_dict=temp_dict))
    print make_json_new
    print "deploy"
    print region
    deploy_component(make_json_new=make_json_new, password=password, release_component=release_component)

if __name__ == "__main__":
    print "fsdgsfdghsjkfghjksdhgkjshd"
    parser = argparse.ArgumentParser(
        description='Download Files from FTP and Push to stash')
    print "starting parse"
    parser.add_argument(
        '--config_file', help="release config file", required=True)
    parser.add_argument(
        '--region', help="release region", required=True)
    parser.add_argument(
        '--env', help="release env", required=True)
    parser.add_argument(
        '--workdir', help="release workdir", required=True)
    parser.add_argument(
        '--password', help="password for the component", required=True)
    parser.add_argument(
        '--mdpFlag', help="mdl flag for the component", required=True)
    parser.add_argument(
        '--release_component', help="release_component for the deployment", required=True)
    print "ending parse"
    vars = parser.parse_args()
    mdp_config_file = vars.config_file.strip()
    region = vars.region.strip()
    print(region)
    env = vars.env.strip()
    workdir = vars.workdir
    password = vars.password.strip()
    is_not_mdp = vars.mdpFlag.strip()
    release_component = vars.release_component.strip()
    print "is_not_mdp {}".format(is_not_mdp)
    print ("wwwwwwwwwww {}".format(workdir))
    if is_not_mdp != 'true':
        deploy_main(env, region, password,mdp_config_file,release_component)


