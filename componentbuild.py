import json
import sys,os
import argparse

comp_to_be_deployed = []
release_to_comp = {}
global newvalue
newvalue =[]
global new_versionid1,envid
new_versionid1 = []
global new_versionid2
new_versionid2 = []
region_env = {}
#envid = {}

def get_releases(**kwargs):
    """[Get the components applicable for the new release]
    
    Param:
        country - [string] -- [Country/Region to be deployed]
        json_file - [string] -- [Component build matrix to get the releases]
        new_version - [string] -- [New Cerillion Version to be deployed]
    Returns:
        [JSON] -- [The key-value pair with "release" as key and "applicable components" as values(array)]
    """

    country=kwargs['region'].split(",")
    #print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh {}".format(country)
    json_file=kwargs['input_file']
    new_version=kwargs['new_version']
    print "country {}".format(country)
    try:
        with open(json_file,"rb") as prop:
            properties=json.load(prop)
            print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh {}".format(properties)
            for reg in properties:
                #print "countryyyyyyyyy {}".format(reg)
                if reg in country:
                    for comp in properties["dev"]:
                        #print "countryyyyyyyyy {}".format(comp)
                        temp_prop = properties["dev"][comp]["versions"]
                        #print "temp_propy {}".format(temp_prop)
                        if new_version in temp_prop.keys():
                            comp_to_be_deployed.append(comp)
                            #for new in temp_prop:
                            if new_version in temp_prop:
                                print " release version details {}".format(temp_prop[new_version])
                                global new_versionid
                                new_versionid = temp_prop[new_version] ["versionid"]
                                if comp == "backend":
                                    print " backend version ID  {}".format(new_versionid)
                                    print new_versionid
                                if comp == "app":
                                    global new_versionid1
                                    new_versionid1 = temp_prop[new_version]["versionid"]
                                    print "app version ID {}".format(new_versionid1)
                                if comp == "crmplus":
                                    global new_versionid2
                                    new_versionid2 = temp_prop[new_version]["versionid"]
                                    print "crmplus version ID {}".format(new_versionid2)
                    if comp_to_be_deployed != []:
                        release_to_comp[new_version] = comp_to_be_deployed
                        return release_to_comp,comp_to_be_deployed,new_versionid,new_versionid1,new_versionid2
                    else:
                        print "{} Release not found".format(new_version)
                        return {}
    except IOError as ioerror:
        print ("File Open Error: due to {}".format(ioerror))
        return -1
    except Exception as exception:
        print ("Exception: due to {}".format(exception))
        return -1

def deploy_recur(**kwargs):
    envidinputfile= kwargs['envidinputfile']
    print ("ccccc {}".format(envidinputfile))
    country = kwargs['country']
    print ("cvvvvvvvvvvvvvvvv {}".format(country))
    env= kwargs['env']
    print env
    try:
        with open(envidinputfile,"rb") as proper:
            regionenvr = json.load(proper)
            print ("ccccccccccccccccccccccc{}".format(regionenvr))
            if country in regionenvr[env]:
                global envid
                env_idapp = regionenvr[env][country]["app"]["envid"]
                print ("qqqqqqqqqqqqqqqqqq {}".format(env_idapp))
                env_idbe = regionenvr[env][country]["backend"]["envid"]
                print ("zzzzzzzzzzzzzzzz {}".format(env_idbe))
                env_idcrmplus = regionenvr[env][country]["crmplus"]["envid"]
                print ("sssssssssssssssss{}".format(env_idcrmplus))
                return env_idapp,env_idbe,env_idcrmplus

    except IOError as ioerror:
        print ("File Open Error: due to {}".format(ioerror))
        return -1

# def get_newvalue(**Kwargs):
#     country = kwargs['region']
#     json_file = kwargs['input_file']
#     new_version = kwargs['new_version']
#
#     try:
#         with open(json_file,"rb") as prop:
#             properties=json.load(prop)
#             for reg in properties:
#                 if reg in country:
#                     for comp in properties[reg]:
#                         temp_prop = properties[reg][comp]["versions"]
#                         if new_version in temp_prop.keys():
#                             comp_to_be_deployed.append(comp)
#                     if comp_to_be_deployed != []:
#                         release_to_comp[new_version] = comp_to_be_deployed
#                         #print "ppppppppppppppppppppppppppppppppppppppppp"
#                         print release_to_comp
#                         newvalue = release_to_comp.values()
#                         print newvalue
#                     else:
#                         print "{} Release not found".format(new_version)
#                         return {}
#     except IOError as ioerror:
#         print ("File Open Error: due to {}".format(ioerror))
#         return -1
#     except Exception as exception:
#         print ("Exception: due to {}".format(exception))
#         return -1