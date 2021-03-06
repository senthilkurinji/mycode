#!/bin/bash
# Log Location on Server
LOG_LOCATION=/opt/CICD/logs
LOG_FILE="db_automerge_$(date +"%Y_%m_%d_%I_%M_%p").log"
exec > >(tee -i $LOG_LOCATION/$LOG_FILE)
exec 2>&1
echo "Log file Location: [ $LOG_LOCATION/$LOG_FILE ]"

# script start
echo "Running db server automerge script"
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

#: <<'END'
#END
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
pwd
echo $COMPONENT_NAME
#go to db folder

if [ ! -d "$dir1"/Database ]; 
then 
echo "Database folder is not found in "$dir1"/Database"
dbFOlder=$(find -type d -iname "$COMPONENT_NAME")
else 
dbFOlder="$dir1"/Database
fi 

echo "Database folder is found in $dbFOlder"



if [ ! -d "$dbFOlder" ]; then
echo "**********************************************"  
echo "DB release folder not found for this release."
echo "**********************************************"
  exit 0
elif [ ! "$(ls -A $dbFOlder)" ]; then
echo "**********************************************"  
echo "Database release folder is empty for this release."
echo "**********************************************"
  exit 1

else
#get db folder full path
cd "$dbFOlder"
db_extracted=$(pwd)

# go the GIT cerillion-baseline directory
cd /opt/CICD/git/cerillion-baseline/
#switch to core branch
git pull --all
git clean -fd
git checkout -f core-db-packages
git clean -fd
git pull --all
git branch | grep '*'
#replace all files in GIT folder with the appserver files
#rm -r *
mkdir "$cersllioniFullVersion"
cp -r "$db_extracted"/* /opt/CICD/git/cerillion-baseline/"$cersllioniFullVersion"/
#update the CeCoreBE.properties files
#echo CerillionCoredbVersion="$cersllioniFullVersion" > CeCoredb.properties
commit_message="$cersllioniFullVersion"
git add . -A
git commit -m "$commit_message"
git push
git pull
git log -1 --pretty=%B
#----------core branch merge completed-------------
echo "**********************************************"  
echo "DB release merge completed. Check GIT branch core-db-packages in cerillion-baseline GIT repo."
echo "**********************************************"

fi
#fi
