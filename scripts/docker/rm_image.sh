#!/bin/bash

if [ -z $1 ]; then
    echo "Missing image name"
    exit
fi

ansible -b -a "docker rmi $1" docker

#for host in $HOSTS; do
#    echo "Deleting image on $host"
#    sudo docker --tlsverify -H ${host}.containers.bigfoot.eurecom.fr rmi $1
#done

