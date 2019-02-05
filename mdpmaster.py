import json
import sys
import os
import argparse
import datetime
import paramiko
import requests
import componentbuild as cb
import configdata as cd
#import scpcomponent as scp
import deploycomponent as dc
import startstopappserver as sapp
import startstopbackendserver as sbe
import startstopstreamserve as sss
import maintenancepage as mpage

parser = argparse.ArgumentParser(
    description='Deploy script for deploying servers')
parser.add_argument('--mdp_config_file',
                    help="Json file containing environment details", required=True)
parser.add_argument('--build_component_file',
                    help="config file containing environment details", required=True)
parser.add_argument('--reg_env_file',
                    help="config file containing environment id's", required=True)
parser.add_argument('--env', help="Environment to be deployed", required=True)
parser.add_argument('--region', help="Region to be deployed", required=True)
parser.add_argument(
    '--version', help="Version of cerillion to be deployed", required=True)



values = parser.parse_args()
environment = values.env.strip()
country = values.region.strip()
reg_env_file=values.reg_env_file.strip()
mdp_config_file = values.mdp_config_file.strip()
build_component_file = values.build_component_file.strip()
new_version = values.version.strip()

updated = {}
envidmake_json = {}
global beversionid
global appversionid
global crmplusversionid
print (" environment id's file {}".format(reg_env_file))
print (" build_component_file {}".format(build_component_file))
#print ("the version is {}".format(new_version))
#convert reg to list
Region = country.split(",")
print Region

print ("get release component start")

release_component, comp_to_be_deployed,new_versionid,new_versionid1,new_versionid2 = cb.get_releases(region=country, input_file=build_component_file, new_version=new_version)
print "backend versionid {}".format (new_versionid)
print "app versionid {}".format(new_versionid1)
print "crmplus versionid {}".format(new_versionid2)
print country
res_json = {}
temp_json = {}
temp_dict = []
make_json = {"data": {}}


for items in Region:
    print(items)
    #items = deploy_region
    #env_idapp, env_idbe, env_idcrmplus = cb.deploy_recur(country=items, envidinputfile=reg_env_file,env=environment)
    #print " ddddddddddddddddddddddddd{} {} {}".format(env_idapp, env_idbe,env_idcrmplus)
    #envidmake_json_temp = {items:{"beversionid":new_versionid,"appversionid":new_versionid1,"crmplusversionid":new_versionid2}}
    #envidmake_json.update(envidmake_json_temp)
    #print "envidjson {}".format (envidmake_json)
    print " releasewwwwww{} {}".format (release_component,comp_to_be_deployed)
    print "*****Region for Deploy {}".format(items)


    if release_component != -1 and release_component != {} and release_component[new_version] != []:
        temp_dict = []
        for comp in release_component[new_version]:
            #print "vvvvvvvvvvvvvvvv {}".format(make_json["data"])
            make_json["data"].update(cd.get_config_data(country=items, input_file=mdp_config_file,
                                     env=environment, release_component=comp,res_json=res_json,temp_dict=temp_dict))

            print "some {}".format(make_json)

    # for compo in release_component[new_version]:
    #     if "crmplus" in compo:
    #         config_data = make_json["data"].get("crmplus")
    #         scp.scp_component(make_json=config_data,
    #                           password='we1c@me', is_start=False)
    #     elif "backend" in compo:
    #         config_data = make_json["data"].get("backend")
    #         #scp.scp_component(make_json=config_data,password='we1c@me', is_start=False)
    #         if environment == "qa":
    #             if country == "barbados":
    #                 params = (('environmentId', '5144592'), ('versionId', new_versionid))
    #                 response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/",
    #                                          params=params,
    #                                          auth=('root', 'we1c@me'))
    #                 print "api response {}".format(response)
    #             if country == "curacao":
    #                 params = (('environmentId', '5144584'), ('versionId', new_versionid))
    #                 response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/",
    #                                          params=params,
    #                                          auth=('root', 'we1c@me'))
    #                 print "api response {}".format(response)
    #     elif "app" in compo:
    #         config_data = make_json["data"].get("app")
    #         scp.scp_component(make_json=config_data,
    #                           password='we1c@me', is_start=False)
    #     elif "streamServe" in compo:
    #         config_data = make_json["data"].get("streamServe")
    #         scp.scp_component(make_json=config_data,
    #                           password='we1c@me', is_start=False)
    #     elif "database" in compo:
    #         config_data = make_json["data"].get("database")
    #         scp.scp_component(make_json=config_data,
    #                           password='we1c@me', is_start=False)

    print("put maintenance page start")
    if ("crmplus" in release_component[new_version] and [i['crmplus'] for i in make_json["data"][items] if 'crmplus' in i]!= None):
        config_data = [i['crmplus'] for i in make_json["data"][items]  if 'crmplus' in i]
        print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm {}".format(config_data)
        mpage.maintainence_page(make_json=config_data,password='we1c@me', is_start=True)
        print("maintainence page enabled for {}".format(items))
        print("put maintainence page end")

    print("stop backend server start")
    if ("backend" in release_component[new_version] and [i['backend'] for i in make_json["data"][items] if 'backend' in i]!= None):
        config_data = [i['backend'] for i in make_json["data"][items] if 'backend' in i]
        print config_data
        sbe.stop_start_beserver(make_json=config_data, password='we1c@me', is_start=False)
        print("stop backend server end")

    print("stop app server start")
    if ("app" in release_component[new_version] and [i['app'] for i in make_json["data"][items] if 'app' in i]!= None):
        config_data = [i['app'] for i in make_json["data"][items] if 'app' in i]
        #print config_data
        sapp.stop_start_appserver(make_json=config_data, password='we1c@me', is_start=False)
    print ("stop app server end")

    # DB server publish start
    # if ("database" in release_component[new_version] and make_json["data"].get("database") != None):
    #     config_data = make_json["data"].get("database")
    #     #print config_data
    #     #dc.deploy_component(make_json=config_data,password='we1c@me', new_value=comp_to_be_deployed)
    # # sDB server publish end

    print ("Publish backend server start")
    if ("backend" in release_component[new_version] and [i['backend'] for i in make_json["data"][items] if 'backend' in i]!= None):
        #config_data = [i['backend'] for i in make_json["data"][items] if 'backend' in i]
        #print config_data
        #dc.deploy_component(make_json=config_data,password='we1c@me', new_value=comp_to_be_deployed)
        # Define cURL process with correct arguments.
        print "region of deployment {}".format(items)
        print "environment {}".format(environment)
        #for reg in country:
            #new_versionidbe = region_env[env][reg]["backend"][envid]
        if environment == "qa":
            if items == "barbados":
                #envidmke_json = envidmake_json["barbados"]["beversionid"]
                #print "env ID Backend.{}".format(envidmke_json)
                print "version ID Backend.{}".format(new_versionid)
                params = (('environmentId', '2261001'), ('versionId', new_versionid))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)


            if items == "curacao":
                #envidmke_json = envidmake_json["curacao"]["beversionid"]
                #print "env ID Backend.{}".format(envidmke_json)
                print "version ID Backend.{}".format(new_versionid)
                params = (('environmentId','5144584' ), ('versionId', new_versionid))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                          auth=('root', 'we1c@me'))
                print "api response {}".format(response)

        if environment == "prod":
            if items == "barbados":
                print "version ID Backend.{}".format(new_versionid)
                params = (('environmentId', '5144578'), ('versionId', new_versionid))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)
            if items == "curacao":
                print "version ID Backend.{}".format(new_versionid)
                params = (('environmentId', '5144583'), ('versionId', new_versionid))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)
    # Publish backend  end

    # Publish app server start
    if ("app" in release_component[new_version] and [i['app'] for i in make_json["data"][items] if'app' in i] != None):
        #config_data = [i['app'] for i in make_json["data"][items] if'app' in i]
        #print config_data
        #dc.deploy_component(make_json=config_data,password='we1c@me', new_value=comp_to_be_deployed)
        if environment == "qa":
            if items == "barbados":
                #envidmke_json = envidmake_json["barbados"]["appversionid"]
                #print "env ID App.{}".format(envidmke_json)
                print "version ID App.{}".format(new_versionid1)
                params = (('environmentId', '5144581'), ('versionId', new_versionid1))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)

            if items == "curacao":
                #envidmke_json = envidmake_json["curacao"]["appversionid"]
                #print "env ID App.{}".format(envidmke_json)
                print "version ID App.{}".format(new_versionid1)
                params = (('environmentId', '5144588'), ('versionId', new_versionid1))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                          auth=('root', 'we1c@me'))
                print "api response {}".format(response)

        if environment == "prod":
            if items == "barbados":
                params = (('environmentId', '5144582'), ('versionId', new_versionid1))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)
            if items == "curacao":
                params = (('environmentId', '5144587'), ('versionId', new_versionid1))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)

    # Publish app server end

    # Publish crmplus start
    if ("crmplus" in release_component[new_version] and [i['crmplus'] for i in make_json["data"][items] if 'crmplus' in i] != None):
        #config_data = [i['crmplus'] for i in make_json["data"][items] if 'crmplus' in i]
        #print config_data
        #dc.deploy_component(make_json=config_data,password='we1c@me', new_value=comp_to_be_deployed)
        if environment == "qa":
            if items == "barbados":
                #print "env ID crmplus.{}".format(new_versionid2)
                print "version ID crmplus{}".format(new_versionid1)
                params = (('environmentId', '5144579'), ('versionId', new_versionid2))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)
            if items == "curacao":
                print "version ID crmplus{}".format(new_versionid1)
                params = (('environmentId', '5144586'), ('versionId', new_versionid2))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                          auth=('root', 'we1c@me'))
                print "api response {}".format(response)

        if environment == "prod":
            if items == "barbados":
                print "version ID crmplus{}".format(new_versionid1)
                params = (('environmentId', '5144580'), ('versionId', new_versionid2))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)
            if items == "curacao":
                print "version ID crmplus{}".format(new_versionid1)
                params = (('environmentId', '5144585'), ('versionId', new_versionid2))
                response = requests.post("http://192.168.44.84:8085/rest/api/latest/queue/deployment/", params=params,
                                     auth=('root', 'we1c@me'))
                print "api response {}".format(response)
    # Publish crmplus end

    ##print("stop streamserves server start")
    # if ("streamServe" in release_component[new_version] and make_json["data"].get("streamServe") != None):
    #     config_data = make_json["data"].get("streamServe")
    #     #print config_data
    #     #sss.stop_start_streamserve(make_json=config_data, password='we1c@me', is_start=False)
    # # stop streamserve end
    #
    # # Publish streamserve start
    # if ("streamServe" in release_component[new_version] and make_json["data"].get("streamServe") != None):
    #     config_data = make_json["data"].get("streamServe")
    #     #print config_data
    #     #dc.deploy_component(make_json=config_data,password='we1c@me', new_value=comp_to_be_deployed)
    # # Publish streamserve end
    #
    # # start streamserve start
    # if ("streamServe" in release_component[new_version] and make_json["data"].get("streamServe") != None):
    #     config_data = make_json["data"].get("streamServe")
    #     #print config_data
    #     #sss.stop_start_streamserve(make_json=config_data, password='we1c@me', is_start=True)
    # # start streamserve end

    # start Backend server start
    if ("backend" in release_component[new_version] and [i['backend'] for i in make_json["data"][items] if 'backend' in i]!= None):
        config_data = [i['backend'] for i in make_json["data"][items] if 'backend' in i]
        #print config_data
        sbe.stop_start_beserver(make_json=config_data, password='we1c@me', is_start=True)
    # start appserver server end

    # start appserver server start
    print("stop app server start")
    if ("app" in release_component[new_version] and [i['app'] for i in make_json["data"][items] if 'app' in i] != None):
        config_data = [i['app'] for i in make_json["data"][items] if 'app' in i]
        #print config_data
        sapp.stop_start_appserver(make_json=config_data, password='we1c@me', is_start=True)
    # start appserver server end

    if ("crmplus" in release_component[new_version]):
        print "{}****Sanity success on crmplus {}".format(datetime.datetime.now(), "192.168.44.84")
        #print "{}****started crmplus {}".format(datetime.datetime.now(), "192.168.44.84")
    # put maintianence page start
    print("Remove maintenance page start")
    if ("crmplus" in release_component[new_version] and [i['crmplus'] for i in make_json["data"][items] if 'crmplus' in i] != None):
        config_data = [i['crmplus'] for i in make_json["data"][items] if 'crmplus' in i]
        print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm {}".format(config_data)
        mpage.maintainence_page(make_json=config_data, password='we1c@me', is_start=False)
    # put maintianence page end
    # get release component end