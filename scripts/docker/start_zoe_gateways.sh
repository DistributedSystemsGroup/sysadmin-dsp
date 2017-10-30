#!/bin/sh

SWARM="docker -H 192.168.46.25:2380"

$SWARM run -d --restart=always -p 22 -v /mnt/cephfs/zoe-workspaces/prod:/home --name gateway-ssh -h gateway-ssh --net zoe  docker-registry:5000/zoerepo/sshd
$SWARM run -d --restart=always -p 1080 --name gateway-socks -h gateway-socks --net zoe docker-registry:5000/zoerepo/socks-proxy
