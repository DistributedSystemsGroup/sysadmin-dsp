#!/bin/bash

NETWORK_NAME=zoe

VOLUME=/mnt/hdfs/datanode

SWARM=bf5:2380

IMAGE=docker-registry:5000/zapps/hadoop-datanode

NODES="bf12 bf13 bf14 bf15 bf16 bf17 bf18 bf19 bf20 bf21"
#NODES="bf19 bf20 bf21"

for node in $NODES; do

docker -H $SWARM run -i -t -d --name hdfs-datanode-$node \
                              -h hdfs-datanode-$node \
                              -e NAMENODE_HOST=hdfs-namenode \
                              -e constraint:node==$node \
                              -m 2g \
                              --net $NETWORK_NAME \
                              -v $VOLUME:/mnt/datanode \
                              --restart=always \
                               $IMAGE

done

