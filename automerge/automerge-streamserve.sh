#!/bin/bash
# Log Location on Server
LOG_LOCATION=/opt/CICD/logs
LOG_FILE="streamserve_automerge_$(date +"%Y_%m_%d_%I_%M_%p").log"
exec > >(tee -i $LOG_LOCATION/$LOG_FILE)
exec 2>&1
echo "Log file Location: [ $LOG_LOCATION/$LOG_FILE ]"

# script start
echo "Running stream serve automerge script"
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
chmod -R 777 *
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

#go to stream serve folder

if [ ! -d "$dir1"/$COMPONENT_NAME ]; 
then 
echo "stream serve folder is not found in "$dir1"/$COMPONENT_NAME"
streamserveFOlder=$(find -type d -iname "$COMPONENT_NAME")
else 
streamserveFOlder="$dir1"/$COMPONENT_NAME
fi 

echo "stream serve folder is found in $streamserveFOlder"

if [ ! -d "$streamserveFOlder" ]; then
echo "**********************************************"  
echo "stream serve release folder not found for this release."
echo "**********************************************"
  exit 0
elif [ ! "$(ls -A $streamserveFOlder)" ]; then
echo "**********************************************"  
echo "stream serve release folder is empty for this release."
echo "**********************************************"
  exit 1


else
echo "$streamserveFOlder"
cd "$streamserveFOlder"
pwd
#inside stream serve folder and extract all the files into respective folders


echo "**********unzipping files in stream serve folder - started**********"

if [ $(find . -maxdepth 1 -name "*CWC*") ]; then
cwc_file=$(find . -maxdepth 1 -name "*CWC*")
echo "$cwc_file file exist"
mkdir CWC
mv "$cwc_file" CWC

else
echo "CWC file not exist."
fi

for f in $(find -name "*gz")
do

echo $f
newFolder=$(echo "$f" | sed -e 's/\.[^.]*$//') 
mkdir "$newFolder"
tar -xzvf "$f" -C "$newFolder"
chmod -R 777 *
cd "$newFolder"
mkdir tempexport
find export -type f -name "*.*" -exec cp -R {} tempexport \;
cd tempexport
#remove tbl files and zip files
rm -R *.tbl
rm -R *.zip

for e in *
do


if [ ${e##*.} = "dux" ]; then
echo "$e"
mkdir -p exported_configurations
mv "$e" exported_configurations
fi

if [ ${e##*.} = "dua" ]; then
echo "$e"
mkdir -p exported_platforms
mv "$e" exported_platforms
fi

if [ ${e##*.} = "fcn" ]; then
echo "$e"
mkdir -p data/function_file
mv "$e" data/function_file
fi


if [ ${e##*.} = "jpg" ] || [ ${e##*.} = "JPG" ] || [ ${e##*.} = "jpeg" ] || [ ${e##*.} = "JPEG" ] || [ ${e##*.} = "png" ] || [ ${e##*.} = "PNG" ]  || [ ${e##*.} = "tif" ] || [ ${e##*.} = "TIF" ]; then
echo "$e"
mkdir -p data/images
mv "$e" data/images
fi

if [ ${e##*.} = "ttf" ] || [ ${e##*.} = "TTF" ]; then
echo "$e"
mkdir -p data/fonts
mv "$e" data/fonts
fi


if [ ${e##*.} = "drs" ] || [ ${e##*.} = "DRS" ]; then
echo "$e"
mkdir -p drivers
mv "$e" drivers
fi

done

cd ..
rm -rf export
rm -rf *.zip
mv tempexport export

cd $SFTP_FOLDER
cd ..
cd ftp_latest_release/"$dir1"/"$streamserveFOlder"
rm $f

done



echo "**********unzipping files in stream serve folder - completed**********"
streamserve_extracted=$(pwd)
echo "$streamserve_extracted"


cd /opt/CICD/git/cerillion-baseline/
git pull --all
git clean -fd
git checkout -f core-streamserve
git pull --all
#replace all files in GIT folder with the stream serve extracted files
rm -r *
cp -rf "$streamserve_extracted"/* /opt/CICD/git/cerillion-baseline/
releaseRegion=$(ls -dm */ | tr -d ' '///)
echo CerillionCoreSSVersion="$cersllioniFullVersion" > CeCoreSS.properties
echo ReleaseRegion="$releaseRegion" >> CeCoreSS.properties

commit_message="$cersllioniFullVersion"
git add . -A
git commit -m "$commit_message"
git push
git pull
git log -1 --pretty=%B

echo "**********************************************"
echo "stream serve release files are moved to Core branch. "
echo "**********************************************"



fi