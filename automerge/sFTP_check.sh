#!/bin/bash
# Log Location on Server
LOG_LOCATION=/opt/CICD/logs
LOG_FILE="automerge_check_$(date +"%Y_%m_%d_%I_%M_%p").log"
exec > >(tee -i $LOG_LOCATION/$LOG_FILE)
exec 2>&1
echo "Log file Location: [ $LOG_LOCATION/$LOG_FILE ]"

# script start
echo "Running automerge intial check script"

# connect to sFTP and download the release files in sFTP Production_Latest folder
SFTP_FOLDER=$1
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
else

cp -r $SFTP_FOLDER/* ftp_latest_release
chmod -R 777 ftp_latest_release
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
#list the release component folders
for directory in */ ; do
    echo "$directory"
if [ ! "$(ls -A "$directory")" ]; then
echo "**********************************************"  
echo "Directory $directory is empty."
fi
echo "**********************************************"  
	
echo "Release exist for $directory."
done
if [ ! -d "Documentation" ]; then
echo "**********************************************"  
echo "Documentation folder not found for this release."
echo "**********************************************"
else

cd Documentation || documentation
doc_extracted=$(pwd)

# go the GIT cerillion-baseline directory
cd /opt/CICD/git/cerillion-baseline/
#switch to MDP branch
git pull --all
git clean -fd
git checkout -f cerillion-mdp-config
git clean -fd
git pull --all
git branch | grep '*'
cd Release_Documentation
pwd
mkdir "$cersllioniFullVersion"
cp -r "$doc_extracted"/* /opt/CICD/git/cerillion-baseline/Release_Documentation/"$cersllioniFullVersion"/
commit_message="$cersllioniFullVersion"
git add . -A
git commit -m "$commit_message"
git push
git pull
git log -1 --pretty=%B

echo "**********************************************"  
echo "Release Documentation updated in GIT branch."
echo "**********************************************"

fi
fi
