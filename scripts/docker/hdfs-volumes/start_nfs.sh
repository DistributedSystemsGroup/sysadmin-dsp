#!/bin/bash

NETWORK_NAME=hdfs
NETWORK_ID=eeef9754c16790a29d5210c5d9ad8e66614ee8a6229b6dc6f779019d46cec792

SWARM=192.168.45.252:2380

IMAGE=192.168.45.252:5000/zoerepo/hadoop-hdfs-nfs

docker -H $SWARM run -i -t -d --name hdfs-nfs \
                              -h hdfs-nfs \
                              -e NAMENODE_HOST=hdfs-namenode \
                              -e constraint:node==bf12 \
                              -m 2g \
                              --net $NETWORK_NAME \
                              -p 4242:4242 -p 111:111 -p 2049:2049 \
                              $IMAGE

