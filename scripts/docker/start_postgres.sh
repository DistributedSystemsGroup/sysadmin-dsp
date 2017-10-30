#!/bin/sh

docker run --name postgres --hostname postgres -v /mnt/cephfs/docker-volumes/postgres:/var/lib/postgresql/data -e POSTGRES_PASSWORD=zoepostgres --restart=always -p 5432:5432 -d postgres

