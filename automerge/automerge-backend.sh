#!/bin/bash
# Log Location on Server
LOG_LOCATION=/opt/CICD/logs
LOG_FILE="be_automerge_$(date +"%Y_%m_%d_%I_%M_%p").log"
exec > >(tee -i $LOG_LOCATION/$LOG_FILE)
exec 2>&1
echo "Log file Location: [ $LOG_LOCATION/$LOG_FILE ]"

# script start
echo "Running Backend automerge script"
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
chmod -R 777 *
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
pwd 
ls -ltr
rm -rf ftp_latest_release
mkdir ftp_latest_release
echo "change the file permission"
chmod -R 777 *
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
pwd
ls -ltr
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

#go to backend folder

if [ ! -d "$dir1"/Cerillion/BackEnd ]; 
then 
echo "backend folder is not found in "$dir1"/Cerillion/BackEnd"
backendFOlder=$(find -type d -iname "$COMPONENT_NAME")
else 
backendFOlder="$dir1"/Cerillion/BackEnd
fi 

echo "backend folder is found in $backendFOlder"

if [ ! -d "$backendFOlder" ]; then
echo "**********************************************"  
echo "Backend release folder not found for this release."
echo "**********************************************"
  exit 0
elif [ ! "$(ls -A $backendFOlder)" ]; then
echo "**********************************************"  
echo "Backend release folder is empty for this release."
echo "**********************************************"
  exit 1


else
#echo "$backendFOlder"
cd "$backendFOlder"
#inside backend folder and extract all the files into respective folders
echo "**********unzipping files in backend folder - started**********"
for f in *.gz
do
newFolder=$(echo "$f" | sed -e 's/\.[^.]*$//') 
mkdir "$newFolder"
tar -xzvf "$f" -C "$newFolder"
done
echo "**********unzipping files in backend folder - completed**********"

# remove the orifinal compressed files
rm -r *.gz
backend_extracted=$(pwd)
# go the GIT cerillion-baseline directory
cd /opt/CICD/git/cerillion-baseline/
#switch to core branch
git pull -all
git clean -fd
git checkout -f core-backend
git clean -fd
git pull --all
git branch | grep '*'
#replace all files in GIT folder with the backend extracted files
rm -rf *
cp -r "$backend_extracted"/* /opt/CICD/git/cerillion-baseline/
#update the CeCoreBE.properties files
echo CerillionCoreBEVersion="$cersllioniFullVersion" > CeCoreBE.properties
commit_message="$cersllioniFullVersion"
git add . -A
git commit -m "$commit_message"
git push
git pull
git log -1 --pretty=%B

echo "**********************************************"
echo "backend release files are moved to Core branch. Check GIT branch core-backend in cerillion-baseline GIT repo. "
echo "**********************************************"


#----------core branch merge completed-------------
echo "----------update temp core branch to create pull request to merge the release files with full-build-backend server-------------"
#----------update core temp branch-------------
#switch to core temp branch
cd "$backend_extracted"
#remove the release version in all the folders
dirs=(/opt/CICD/git/cerillion-baseline/*/)

for dir in /opt/CICD/git/cerillion-baseline/*
do
folder1=$(cut -d'_' -f1 <<< "$(basename $dir)")
folder2=$(cut -d'_' -f2 <<< "$(basename $dir)")
foldername=$folder1'_'$folder2
#echo $foldername
mv "$(basename $dir)" $foldername
done

cd /opt/CICD/git/cerillion-baseline/
git pull --all
git clean -fd
git checkout -f temp-full-build-backend
git pull --all
#replace all files in GIT folder with the backend extracted files
#rm -r *
cp -r "$backend_extracted"/* /opt/CICD/git/cerillion-baseline/
rm CeCoreBE.properties
echo CerillionCoreBEVersion="$cersllioniFullVersion" > CeCoreBE.properties
commit_message="$cersllioniFullVersion"
git add . -A
git commit -m "$commit_message"
git push
git pull
git log -1 --pretty=%B

echo "**********************************************"
echo "backend release files are moved to Core branch. Check GIT branch temp-full-build-backend in cerillion-baseline GIT repo. "
echo "**********************************************"

echo "----------raise pull request to merge core temp branch with full-build branch--------------"

generate_post_data()
{
  cat <<EOF
{
	"title": "$cersllioniFullVersion",
	"description": "$cersllioniFullVersion",
	"fromRef": {
		"id": "refs/heads/temp-full-build-backend",
		"repository": {
			"slug": "cerillion-baseline",
			"name": null,
			"project": {
				"key": "CERDEMO"
			}
		}
	},
	"toRef": {
		"id": "refs/heads/full-build-backend",
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

rm -rf ftp_latest_release
#fi