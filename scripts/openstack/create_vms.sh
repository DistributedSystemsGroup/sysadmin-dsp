#!/bin/bash

set -e
set -x

# flavor-list
# +--------------------------------------+----------------+-----------+------+-----------+------+-------+-------------+-----------+-------------+
# | ID                                   | Name           | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor | Is_Public | extra_specs |
# +--------------------------------------+----------------+-----------+------+-----------+------+-------+-------------+-----------+-------------+
# | 0b09b6dd-2487-4c43-b9a6-c72ae3845810 | bigfoot.master | 16384     | 100  | 100       |      | 4     | 1.0         | True      | {}          |
# | 1                                    | m1.tiny        | 512       | 0    | 0         |      | 1     | 1.0         | True      | {}          |
# | 2                                    | m1.small       | 2048      | 20   | 0         |      | 1     | 1.0         | True      | {}          |
# | 27def4d8-eb0e-4aa0-9708-094a4f582079 | bigfoot.worker | 8192      | 300  | 300       |      | 4     | 1.0         | True      | {}          |
# | 3                                    | m1.medium      | 4096      | 40   | 0         |      | 2     | 1.0         | True      | {}          |
# | 4                                    | m1.large       | 8192      | 80   | 0         |      | 4     | 1.0         | True      | {}          |
# | 5                                    | m1.xlarge      | 16384     | 160  | 0         |      | 8     | 1.0         | True      | {}          |
# +--------------------------------------+----------------+-----------+------+-----------+------+-------+-------------+-----------+-------------+

# image-list
# +--------------------------------------+-----------------------------+--------+--------+
# | ID                                   | Name                        | Status | Server |
# +--------------------------------------+-----------------------------+--------+--------+
# | 879c8003-0dbd-4ad7-bc94-5e81dd8a22c8 | CLOUDERA                    | ACTIVE |        |
# | fe5da187-1595-4fdb-a67f-485e5aeb59d2 | Cirros                      | ACTIVE |        |
# | fd02e6e8-48fe-4a05-8abc-ac34bfc7ce28 | Ubuntu                      | ACTIVE |        |
# | 357449d9-a9be-44f0-a17d-a1aee73c41e2 | Ubuntu + Java + Hadoop      | ACTIVE |        |
# | 58f7a0a4-85dd-45ba-9da4-c57d4eff6e74 | Ubuntu with Hadoop packages | ACTIVE |        |
# +--------------------------------------+-----------------------------+--------+--------+

. ~/keystonerc

export OS_TENANT_NAME=bigdoop

for i in {1..20}
do
	ID=$(nova boot --flavor bigfoot.worker --image fd02e6e8-48fe-4a05-8abc-ac34bfc7ce28 --key-name bigdoop --availability-zone zone_perf worker$i | grep -e '\<id\>' | cut -d\| -f3)
	while true; do
		st=$(nova list | grep $ID | cut -f4 -d\| | tr -d \ )
		echo "worker$1 is in status $st"
		if [ $st != "BUILD" ]; then
			break
		else
			sleep 5
		fi
	done
done

ID=$(nova boot --flavor bigfoot.master --image fd02e6e8-48fe-4a05-8abc-ac34bfc7ce28 --key-name bigdoop --availability-zone zone_perf master | grep -e '\<id\>' | cut -d\| -f3)
while true; do
	st=$(nova list | grep $ID | cut -f4 -d\| | tr -d \ )
	echo "master is in status $st"
	if [ $st != "BUILD" ]; then
		break
	else
		sleep 5
	fi
done

#nova boot --flavor bigfoot.master --image 357449d9-a9be-44f0-a17d-a1aee73c41e2 --key-name bigdoop --availability-zone zone_test client
#sleep 5
ID=$(nova boot --flavor m1.large --image fd02e6e8-48fe-4a05-8abc-ac34bfc7ce28 --key-name bigdoop --availability-zone zone_perf cdhmanager | grep -e '\<id\>' | cut -d\| -f3)
while true; do
	st=$(nova list | grep $ID | cut -f4 -d\| | tr -d \ )
	echo "cdhmanager is in status $st"
	if [ $st != "BUILD" ]; then
		break
	else
		sleep 5
	fi
done

#COUNT=22

#echo "Waiting for all of the $COUNT machines to be in ACTIVE state"
#while true; do
#	num=`nova list | grep 10.10 | wc -l`
#	if [ $num != $COUNT ]; then
#		echo "Got $num ip addresses"
#		sleep 2
#	else
#		echo "Got all of them!"
#		break
#	fi
#done

echo "Setting up floating IPs"
#CLIENTIP=`nova list | grep client | cut -f 5 -d\| | cut -f2 -d\= | tr -d ' '`
#CLIENTPORT=`quantum port-list | grep -e "\<$CLIENTIP\>" | cut -f2 -d\| | tr -d ' '`
#quantum floatingip-associate c2d0d4b1-8da5-4a93-ac52-a5685e1c4657 $CLIENTPORT
MASTERIP=`nova list | grep master | cut -f 5 -d\| | cut -f2 -d\= | tr -d ' '`
MASTERPORT=`quantum port-list | grep -e "\<$MASTERIP\>" | cut -f2 -d\| | tr -d ' '`
quantum floatingip-associate cb9cf57d-aca9-40dd-a66e-1b15b9d5e3da $MASTERPORT
CDHIP=`nova list | grep cdhmanager | cut -f 5 -d\| | cut -f2 -d\= | tr -d ' '`
CDHPORT=`quantum port-list | grep -e "\<$CDHIP\>" | cut -f2 -d\| | tr -d ' '`
quantum floatingip-associate 532d695d-9c96-44bf-9c66-f764e9633847 $CDHPORT

echo "Fixing hosts file"

echo "127.0.0.1	localhost" > /tmp/tmp_hosts

nova list | grep 10.10 | cut -f5,3 -d \| | sed "s/${OS_TENANT_NAME}_net=//" | tr -d ' ' | cut -f1 -d, | awk 'BEGIN { FS = "|" }; { printf("%s\t%s\n", $2, $1); }' >> /tmp/tmp_hosts

NS=qrouter-`quantum router-list | grep ext_router | cut -f2 -d\| | tr -d \ `

TESTIPS=`nova list | grep 10.10 | cut -f5 -d \| | cut -f2 -d= | cut -f1 -d, | tr -d \ `

echo "Will need the sudo password to use namespace $NS"
for ip in $TESTIPS; do
	sudo ip netns exec $NS ping -c1 $ip
done

for ip in `nova list | grep 10.10 | cut -f5 -d \| | cut -f2 -d= | cut -f1 -d, | tr -d \  `; do
	echo "Fixing hosts file on VM $ip..."
	sudo ip netns exec $NS scp -i ~/.ssh/bigdoop -o StrictHostKeyChecking=false /tmp/tmp_hosts ubuntu@$ip:/tmp
	sudo ip netns exec $NS ssh -i ~/.ssh/bigdoop -o StrictHostKeyChecking=false ubuntu@$ip "sudo mv /tmp/tmp_hosts /etc/hosts"
done

