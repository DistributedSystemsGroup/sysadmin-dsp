#!/bin/bash

docker run --rm -it -v /mnt/cephfs/zoe-workspaces/prod/venzano:/mnt/workspace -e ZOE_UID=10000 -e ZOE_USER=venzano -e ZOE_GID=345 -e ZOE_WORKSPACE=/mnt/workspace $@
