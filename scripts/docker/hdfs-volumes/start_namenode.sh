#!/bin/bash

NETWORK_NAME=zoe

VOLUME_PATH=/mnt/hdfs/namenode

SWARM=bf5:2380

IMAGE=docker-registry:5000/zapps/hadoop-namenode

docker -H $SWARM run -i -t -d --name hdfs-namenode \
                              -h hdfs-namenode \
                              -e NAMENODE_HOST=hdfs-namenode \
                              -e constraint:node==bf12 \
                              -m 1g \
                              -p 8020:8020 \
                              -p 50070:50070 \
                              -v $VOLUME_PATH:/mnt/namenode \
                              --net $NETWORK_NAME \
                              --restart=always \
                              $IMAGE

