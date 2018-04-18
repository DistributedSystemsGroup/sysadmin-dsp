#!/bin/bash

if [ -z $1 -o -z $2 ]; then
    echo "Usage: $0 <username> <expiration>"
    exit
fi

sudo adduser --home /mnt/cephfs/zoe-workspaces/prod/$1 --shell /usr/bin/rssh --ingroup zoe $1
sudo usermod -e $2 $1

