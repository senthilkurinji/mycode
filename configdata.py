import json
import sys,os
import argparse

# parser = argparse.ArgumentParser(description='Deploy script for deploying servers')
# parser.add_argument('--config_file', help="Json file containing environment details",required=True)
# parser.add_argument('--env', help="Environment to be deployed",required=True)
# parser.add_argument('--region', help="Region to be deployed",required=True)
# parser.add_argument('--version', help="Version of cerillion to be deployed",required=True)

# values = parser.parse_args()
# component = values.component.strip()
# environment = values.env.strip()
# country = values.region.strip()
# config_file = values.config_file.strip()
# new_version = values.version.strip()
# print ("the version is {}".format(new_version))


def get_config_data(**kwargs):
    country=kwargs['country']
    print "kwargs --> {}".format(country)
    config_file=kwargs['input_file']
    environment=kwargs['env']
    release_component=kwargs['release_component']
    temp_json = {}
    res_json = kwargs['res_json']
    temp_dict = kwargs['temp_dict']
    try:
        with open(config_file,"rb") as prop:
            properties=json.load(prop)
            #print properties
            for env in properties:
                #print env
                if environment in env:
                    #print environment
                    for reg in properties[env]:
                        print "reg, country {} {}".format(reg, country)
                        if reg in country:
                            print reg
                            for comp in properties[env][reg]:
                                if comp in release_component:
                                    temp_json[comp] = properties[env][reg][comp]
                                    #print "temp json new {}".format(temp_json)
                                    temp_dict.append(temp_json)
                            #print "temp_dict new loop {}".format(temp_dict)
                            res_json[reg] = temp_dict
                            #print "res_json --> {}".format(res_json)
            print "res_json final value --> {}".format(res_json)
            return res_json
    except IOError as ioerror:
        print ("File Open Error: due to {}".format(ioerror))
        return -1
    except Exception as exception:
        print ("Exception: due to {}".format(exception))
        return -1
