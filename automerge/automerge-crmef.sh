#!/bin/bash
# Log Location on Server
LOG_LOCATION=/opt/CICD/logs
LOG_FILE="CRMPlus_automerge_$(date +"%Y_%m_%d_%I_%M_%p").log"
exec > >(tee -i $LOG_LOCATION/$LOG_FILE)
exec 2>&1
echo "Log file Location: [ $LOG_LOCATION/$LOG_FILE ]"

# script start
echo "Running CRM Plus automerge script"
#----------core branch merge started-------------
# connect to sFTP and download the release files in sFTP Production_Latest folder
SFTP_FOLDER=$1
COMPONENT_NAME=$2
PROTOCOL="sftp"
URL="83.244.146.5" 
LOCALDIR="/opt/CICD"
REMOTEDIR="/Production_Latest/"
USER="columbus"
PASS="bowser"
CERILLION_GIT_FOLDER="/opt/CICD/git/cerillion-baseline"
cd $SFTP_FOLDER
#rm -rf Production_Latest
#mkdir Production_Latest
if [  ! $? -eq 0 ]; then
    echo "$(date "+%d/%m/%Y-%T") Cant cd to $SFTP_FOLDER. Please make sure this directory is valid"
    exit 1 
fi


#lftp sftp://columbus:bowser@$URL <<EOF

#mirror --verbose --use-pget-n=8 -c /Production_Latest/ /opt/CICD/
#exit
#EOF


#if [ ! $? -eq 0 ]; then
#    echo "$(date "+%d/%m/%Y-%T") Cant download files. Make sure the credentials and server information are correct"
#else
cd ..
rm -rf ftp_latest_release
mkdir ftp_latest_release
echo "change the file permission"

# copy release files to temp folder
if [ ! "$(ls -A $SFTP_FOLDER)" ]; then
echo "**********************************************"
echo "Release folder $SFTP_FOLDER is empty"
echo "**********************************************"
    exit 1
fi
cp -r $SFTP_FOLDER/* ftp_latest_release
chmod -R 777 *
#: <<'END'
#END

#------------------
connect to WIN server and extract the msi file.

#------------------
cd ftp_latest_release
echo " inside ftp_latest_release"
# get the first folder name
dir1=$(find . -name \*C\* -type d -maxdepth 1 -print -quit)
# get Cerillion release version from the folder name
cerillionVersion=$(cut -d'_' -f3 <<< "$(find . -name \*C\* -type d -maxdepth 1 -print -quit)")
cerillionVersionHF=$(cut -d'_' -f4 <<< "$(find . -name \*C\* -type d -maxdepth 1 -print -quit)")
if [ -z "$cerillionVersionHF" ]
then
cersllioniFullVersionTemp="$cerillionVersion"
cersllioniFullVersionUpper=$(echo $cersllioniFullVersionTemp | tr 'a-z' 'A-Z')
cersllioniFullVersion="${cersllioniFullVersionUpper/-HOTFIX-/HF}"
else
cersllioniFullVersionTemp=$cerillionVersion$cerillionVersionHF
cersllioniFullVersionUpper=$(echo $cersllioniFullVersionTemp | tr 'a-z' 'A-Z')
cersllioniFullVersion="${cersllioniFullVersionUpper/HOTFIX-/HF}"
fi
cd "$dir1"
#go to CRM Plus folder


if [ ! -d "$dir1"/CRM_64bit/CRMPortal ]; 
then 
echo "CRM Plus folder is not found in "$dir1"/CRM_64bit"
crmplusFolder=$(find -type d -iname "$COMPONENT_NAME")
else 
crmplusFolder="$dir1"/CRM_64bit
fi 

echo "CRM Plus folder is found in $crmplusFolder"



if [ ! -d "$crmplusFolder" ]; then
echo "**********************************************"  
echo "CRM Plus release folder not found for this release."
echo "**********************************************"
  exit 0
elif [ ! "$(ls -A $crmplusFolder)" ]; then
echo "**********************************************"  
echo "CRM Plus release folder is empty for this release."
echo "**********************************************"
  exit 1

else
#echo "$crmplusFolder"
cd "$crmplusFolder"
#inside CRM_64bit folder

#go to CRM Plus msi file folder
crmplusInstall=$(find -type d -iname '*CRMPortal*')

if [ ! -d "$crmplusInstall" ]; then
  echo "**********************************************"
echo "CRM Plus install file not found for this release."
echo "**********************************************"
  exit 1
else
#echo "$crmplusInstall"
cd "$crmplusInstall"
pwd
# echo "inside crmplusInstall folder"
rm *.msi
#find CRMPlus folder to get the extracted files
crmplusbinary=$(find -type d -iname '*CRMPlus*')
#echo "$crmplusbinary"
cd "$crmplusbinary"
# echo "inside crmplusbinary folder"

cd *

crmplus_extracted=$(pwd)
#: <<'END'

# go the GIT cerillion-baseline directory
cd /opt/CICD/git/cerillion-baseline/
#switch to core branch
git pull --all
git clean -fd
git checkout -f core-crmplus
git clean -fd
git pull --all
git branch | grep '*'
#replace all files in GIT folder with the CRM Plus extracted files
rm -r *
mkdir crmplus
cp -r "$crmplus_extracted"/* /opt/CICD/git/cerillion-baseline/crmplus/
#update the CeCoreCRMPlus.properties files
echo crmversion="$cersllioniFullVersion" > core.properties
commit_message="$cersllioniFullVersion"
git add . -A
git commit -m "$commit_message"
git push
git pull
git log -1 --pretty=%B

echo "**********************************************"
echo "CRM Plus release components moved to GIT branch core-crmplus in cerillion-baseline GIT repo." 
echo "**********************************************"

#END
#----------core branch merge completed-------------
#----------update temp core branch to create pull request to merge the release files with full-crmplus server-------------
#----------update core temp branch-------------
#switch to core temp branch

cd /opt/CICD/git/cerillion-baseline/
git checkout -f master
git pull --all
git fetch --all
git checkout -f temp-full-build-crmplus
git clean -fd
git pull --all

#replace all files in GIT folder with the crm plus extracted files

cd /opt/CICD/git/cerillion-baseline/crmplus/
#echo "inside crm plus version binary folder"
#-----------------------#code merge part----------------
cp -r "$crmplus_extracted"/* /opt/CICD/git/cerillion-baseline/crmplus/


#------------------------------------code merge-----------------------------------------------------------------------------

for f in  "$crmplus_extracted"/ConfigFiles/*.*;do
#echo "core"
#echo "$f"
#filename= ${f##*/}
#echo "filename is - ""${f##*/}"
echo "----------------------------"

cd /opt/CICD/git/cerillion-baseline/crmplus/SiteSpecific
#echo "CWC files"
for file1 in $(find -type f -iname "${f##*/}");do

echo "${file1##*/}"

find . -name "${file1##*/}" -exec cp /opt/CICD/git/cerillion-baseline/crmplus/SiteSpecific/"${file1}" {} \;

done
#echo "----------------"
done
#update the CeCoreCRMPlus.properties files
cd /opt/CICD/git/cerillion-baseline/
echo crmversion="$cersllioniFullVersion" > core.properties
commit_message="$cersllioniFullVersion"
git add . -A
git commit -m "$commit_message"
git push origin temp-full-build-crmplus
git pull
git log -1 --pretty=%B
#END
echo "**********************************************"
echo "CRM Plus release components moved to GIT branch temp-full-build-crmplus in cerillion-baseline GIT repo." 
echo "**********************************************"



#------------------------------------code merge-----------------------------------------------------------------------------


echo "----------raise pull request to merge core temp branch with full-build branch--------------"

generate_post_data()
{
  cat <<EOF
{
	"title": "$cersllioniFullVersion",
	"description": "$cersllioniFullVersion",
	"fromRef": {
		"id": "refs/heads/temp-full-build-crmplus",
		"repository": {
			"slug": "cerillion-baseline",
			"name": null,
			"project": {
				"key": "CERDEMO"
			}
		}
	},
	"toRef": {
		"id": "refs/heads/full-build-crmplus",
		"repository": {
			"slug": "cerillion-baseline",
			"name": null,
			"project": {
				"key": "CERDEMO"
			}
		}
	}
}
EOF
}

curl -u adminuser:we1come -H "Content-Type: application/json" http://192.168.44.84:7990/rest/api/1.0/projects/CERDEMO/repos/cerillion-baseline/pull-requests -X POST --data "$(generate_post_data)"
echo "----------Check cerillion-baseline pull requests page.--------------"

fi
fi