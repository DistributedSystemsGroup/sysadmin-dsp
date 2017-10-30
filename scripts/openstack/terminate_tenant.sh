#!/bin/bash

. ~/keystonerc

if [ -z "$1" ]; then
	echo "specify tenant to terminate"
	exit
fi

export OS_TENANT_NAME=$1

for uuid in `nova list | grep -v +-- | grep -v ID | cut -f2 -d\| | tr -d \ `
do
	echo "Terminating $uuid"
	nova delete $uuid
done

