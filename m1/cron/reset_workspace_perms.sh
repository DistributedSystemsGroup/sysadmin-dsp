#!/bin/bash

cd /mnt/cephfs/zoe-workspaces/prod

for d in *; do
	chmod 755 $d
done

IFS=$'\n'
for cmd in `ls -l /mnt/cephfs/zoe-workspaces/prod/ | grep -v total | awk '{ print "setfacl -R -m u:"$3":rwx " $9 }'`; do
	eval $cmd
done

