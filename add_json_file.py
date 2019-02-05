import ftplib
import argparse
import sys, os
import subprocess
import json
import urllib2, base64

def add_to_json(**kwargs):
    update = False
    data = {}
    json_file = kwargs['json_file']
    component = kwargs['component']
    region = kwargs['region']
    new_version = kwargs['new_version']
    release_number = kwargs['b_release_version']
    commit_code = kwargs['commit_code']
    b_version_id= kwargs['b_version_id']
    try:
        with open(json_file) as f:
            data = json.load(f)
        for reg in data:
            if reg in region:
                if component in data[reg]:
                    for ver in data[reg][component]:
                        data[reg][component]["versions"][new_version] = {"release": release_number,"commit": commit_code, "versionid": str(b_version_id)}
                        update = True
                else:
                    print 'component not found-',component

        if update:
            try:
                with open(json_file, 'w') as f:
                    f.write(json.dumps(data, f, indent=4, sort_keys=True))
                print json_file, 'has been updated'
                return True
            except:
                print 'writing', json_file, 'failed:', sys.exc_info()[0]
                return False
            else:
                print 'not added'
    except:
        print 'opening/loading',json_file,'failed:',sys.exc_info()[0]
        return False
    

def get_release_id (**kwargs):

    get_url = kwargs['get_url']
    b_user = kwargs['b_user']
    b_password = kwargs['b_password']
    new_version= kwargs['new_version']
    b_release_version=kwargs['b_release_version']

    try:
        request = urllib2.Request(get_url)
        base64string = base64.b64encode('%s:%s' % (b_user, b_password))
        request.add_header("Authorization", "Basic %s" % base64string)
        result = urllib2.urlopen(request)
        data = json.loads(result.read())
        b_version_id=0
        if "results" in data:
            for ver in data["results"]:
                if ver["deploymentVersion"]["name"] == b_release_version:
                    b_version_id=ver["deploymentVersion"]["id"]
                    return b_version_id
    except:
        print 'opening/loading',get_url,'failed:',sys.exc_info()[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add new release version to JSON file.')
    # parser.add_argument('--version',help="Release Version you are going to deploy")
    parser.add_argument('--json_file', help="Json file to update", required=True)
    parser.add_argument('--component', help="Component name", required=True)
    parser.add_argument('--region', help="Environment region - DEV/QA/PROD", required=True)
    parser.add_argument('--new_version', help="Release version", required=True)
    parser.add_argument('--commit_code', help="GIT commit code", required=True)
    parser.add_argument('--get_url', help="URL to hit", required=True)
    parser.add_argument('--username', help="bamboo username", required=True)
    parser.add_argument('--password', help="bamboo user password", required=True)
    parser.add_argument('--b_release_version', help="Bamboo Release version", required=True)

    vars = parser.parse_args()
    component = vars.component.strip()
    region = vars.region.strip()
    new_version = vars.new_version .strip()
    commit_code = vars.commit_code.strip()
    json_file = vars.json_file.strip()
    get_url = vars.get_url.strip()
    b_user = vars.username.strip()
    b_password = vars.password.strip()
    b_release_version = vars.b_release_version.strip()
#to get the bamboo release version ID
    b_version_id=get_release_id(get_url=get_url, b_user=b_user, b_password=b_password, new_version=new_version, b_release_version=b_release_version )
# to update the JSON file 
    add_to_json(component=component, region=region, new_version=new_version, b_release_version=b_release_version,commit_code=commit_code, json_file=json_file, b_version_id=b_version_id)
