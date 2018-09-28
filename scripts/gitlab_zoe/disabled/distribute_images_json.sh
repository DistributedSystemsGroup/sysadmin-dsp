#!/bin/sh

set -x

apk update
apk add jq

for json in *.json; do
    if [ $json = "manifest.json" ]; then
        continue
    fi
    for image in `cat $json | jq .services[].image`; do
        echo $image
#        docker pull $image
#        /scripts/distribute_docker_image.sh $image
    done
done

