#!/bin/bash

if [ -z $1 ]; then
    echo "Usage: $0 <gitlab project name (e.g. pydatasci)>"
    exit 1
fi

rawurlencode() {
  local string="${1}"
  local strlen=${#string}
  local encoded=""
  local pos c o

  for (( pos=0 ; pos<strlen ; pos++ )); do
     c=${string:$pos:1}
     case "$c" in
        [-_.~a-zA-Z0-9] ) o="${c}" ;;
        * )               printf -v o '%%%02x' "'$c"
     esac
     encoded+="${o}"
  done
  echo "${encoded}"    # You can either set a return variable (FASTER) 
  REPLY="${encoded}"   #+or echo the result (EASIER)... or both... :p
}

GITLAB_API_TOKEN=`cat /mnt/cephfs/admin/gitlab_api_token.txt`

PROJECT_NAME_ENC=`rawurlencode zoe-apps/$1`

## Populate the ZApp Shop
curl --header "PRIVATE-TOKEN: $GITLAB_API_TOKEN" "https://gitlab.eurecom.fr/api/v4/projects/${PROJECT_NAME_ENC}/jobs/artifacts/master/download?job=test:json" -o /tmp/artifacts.zip

rm -Rf /mnt/cephfs/zoe-apps/$1
mkdir /mnt/cephfs/zoe-apps/$1

unzip -d /mnt/cephfs/zoe-apps/$1 /tmp/artifacts.zip

rm /tmp/artifacts.zip

## Pull images on the hosts
for image in `cat /mnt/cephfs/zoe-apps/$1/images`; do
  echo "Pulling image $image"
  if [[ $image =~ gpu ]]; then
    sudo -u venzano ansible -m docker_image -a "name=$image pull=yes" zoe-workers-gpu
  else
    sudo -u venzano ansible -m docker_image -a "name=$image pull=yes" zoe-workers
  fi
done

