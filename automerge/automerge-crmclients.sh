#!/bin/bash
# Log Location on Server
LOG_LOCATION=/opt/CICD/logs
LOG_FILE="crm_vdi_automerge_$(date +"%Y_%m_%d_%I_%M_%p").log"
exec > >(tee -i $LOG_LOCATION/$LOG_FILE)
exec 2>&1
echo "Log file Location: [ $LOG_LOCATION/$LOG_FILE ]"

# script start
echo "Running CRM VDI automerge script"
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
admin_count=0
client_count=0
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
cd $LOCALDIR
rm -rf ftp_latest_release
mkdir ftp_latest_release
echo "change the file permission"
#chmod -R 777 *
# copy release files to temp folder
if [ ! "$(ls -A $SFTP_FOLDER)" ]; then
echo "**********************************************"
echo "Release folder $SFTP_FOLDER is empty"
echo "**********************************************"    
exit 1
fi
cp -r $SFTP_FOLDER/* ftp_latest_release

#: <<'END'
#END
cd $LOCALDIR/ftp_latest_release
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
#go to CRM VDI

if [ ! -d "$COMPONENT_NAME"/Administrator ]; 
then 
echo "CRM Admin folder is not found in "$dir1"/"$COMPONENT_NAME""
crm_admin="$(find -type d -iname "Administrator")"
echo "CRM Admin folder is found in $dir1/$crm_admin"
else 
crm_admin="$COMPONENT_NAME"/Administrator
echo "CRM Admin folder is found in $dir1/$crm_admin"

fi 



if [ ! -d "$crm_admin" ]; then
echo "**********************************************"  
echo "CRM Admin release folder not found for this release."
echo "**********************************************"
admin_count=0
elif [ ! "$(ls -A $crm_admin)" ]; then
echo "**********************************************"  
echo "CRM Admin release folder is empty for this release."
echo "**********************************************"
admin_count=0
exit 1
else
admin_count=1
fi

if [ ! -d "$crm_client" ]; then
echo "**********************************************"  
echo "CRM Client release folder not found for this release."
echo "**********************************************"
client_count=0
elif [ ! "$(ls -A $crm_client)" ]; then
echo "**********************************************"  
echo "CRM Client release folder is empty for this release."
echo "**********************************************"
client_count=0
exit 1
else
client_count=1
fi


if [ ! -d "$COMPONENT_NAME"/CRMPortal ]; 
then 
echo "CRM Client folder is not found in "$dir1"/"$COMPONENT_NAME""
if [ $admin_count -eq 1 ]; then
crm_client=${crm_admin/Administrator/CRMPortal}
echo "CRM Client folder is found in $dir1/$crm_client"
fi
else
crm_client="$COMPONENT_NAME"/CRMPortal
echo "CRM Client folder is found in $dir1/$crm_client"
fi 





if [ $client_count -eq 0 ] && [ $admin_count -eq 0 ]; then
echo "do nothing - exit"
echo "**********************************************"  
echo "No release for CRM Client and Admin."
echo "**********************************************"
exit 0


elif [ $client_count -eq 1 ] || [ $admin_count -eq 1 ]; then
echo "do something"

# go the GIT cerillion-baseline directory
cd /opt/CICD/git/cerillion-baseline/
#switch to core branch
git pull --all
git clean -fd
git checkout -f core-crmclients
git clean -fd
git pull --all
git branch | grep '*'


if [ $client_count -eq 1 ]; then
echo "do client"

rm -rf /opt/CICD/git/cerillion-baseline/CRMPortal/*.msi
cp -r $LOCALDIR/ftp_latest_release/$dir1/$crm_client/* /opt/CICD/git/cerillion-baseline/CRMPortal
echo CerillionCRMVersion="$cersllioniFullVersion" > CeCRMCore.properties
commit_message="$cersllioniFullVersion"
else
echo "**********************************************"  
echo "No release for CRM Client."
echo "**********************************************"
fi
if [ $admin_count -eq 1 ]; then
echo "do admin"

rm -rf /opt/CICD/git/cerillion-baseline/Administrator/*.msi
cp -r $LOCALDIR/ftp_latest_release/$dir1/$crm_admin/* /opt/CICD/git/cerillion-baseline/Administrator
echo CerillionCRMVersion="$cersllioniFullVersion" > CeCRMCore.properties
commit_message="$cersllioniFullVersion"
else
echo "**********************************************"  
echo "No release for CRM Admin."
echo "**********************************************"
fi

git add . -A
git commit -m "$commit_message"
git push
git pull
git log -1 --pretty=%B
#----------core branch merge completed-------------
echo "**********************************************"
echo "CRM Clients release files are moved to Core branch. Check GIT branch core-crmclients in cerillion-baseline GIT repo. "
echo "**********************************************"

else
echo "error"

fi
#fi
