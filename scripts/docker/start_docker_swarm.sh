#!/bin/bash

#TOKEN=7a0702eed4e52485e7768ca06d8a5cda

#for h in 1 2 3 4 5 6 7 8 9 10 11; do
#	ssh bf$h sudo docker run -d --name swarm-join-bf$h --restart=always swarm join --advertise=bf$h:2375 zk://bf1:2181,bf5:2181,bf11:2181/swarm
#done

docker run -d --name swarm-manager-master --restart=always -p 2380:2375 swarm manage --replication --advertise bf5:2380 --discovery-opt kv.path=docker/nodes zk://bf1:2181,bf5:2181,bf11:2181/docker
#ssh bf6 sudo docker run -d --name swarm-manager-master --restart=always -p 2380:2375 swarm manage --replication --advertise bf6:2380 zk://bf1:2181,bf5:2181,bf11:2181/swarm
#ssh bf10 sudo docker run -d --name swarm-manager-master --restart=always -p 2380:2375 swarm manage --replication --advertise bf10:2380 zk://bf1:2181,bf5:2181,bf11:2181/swarm

