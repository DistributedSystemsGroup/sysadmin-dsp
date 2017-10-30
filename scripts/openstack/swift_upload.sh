#!/bin/bash

set -e

if [ -z $1 ]; then
	echo "Usage: $0 <log nr>"
	exit
fi

cd /mnt/logs/syslog

NR=$1

if [ ! -f bigfoot.log.$NR.gz ]; then
	exit
fi

source /home/venzano/keystonerc
OS_TENANT_NAME=bigdoop

NEW_NAME=bigfoot-`stat -c '%Y' bigfoot.log.$NR.gz`.log.gz

mv bigfoot.log.$NR.gz $NEW_NAME

swift upload bigfoot_syslog $NEW_NAME

rm $NEW_NAME
