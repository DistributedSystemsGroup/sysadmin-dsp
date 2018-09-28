#!/bin/bash

GITLAB_API_TOKEN=`cat /mnt/cephfs/admin/gitlab_api_token.txt`

PROJECT_ID=1538

## Find the latest pipeline ID
PIPELINE_ID=`curl -s --header "PRIVATE-TOKEN: ${GITLAB_API_TOKEN}" "https://gitlab.eurecom.fr/api/v4/projects/${PROJECT_ID}/pipelines" | json_pp | grep \"id\" | head -n1 | sed -E 's/ +"id" : ([0-9]+),?/\1/'`

## Pull images on the hosts
for image in zapps/base zapps/java zapps/python; do
  echo "Pulling image $image:${PIPELINE_ID}"
  ansible -m docker_image -a "name=$image:${PIPELINE_ID} pull=yes force=yes" zoe-workers
done

