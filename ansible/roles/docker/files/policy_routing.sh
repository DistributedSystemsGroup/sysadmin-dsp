#!/bin/sh

ip route del 192.168.45.0/24 dev em3 table net45
ip route del 192.168.46.0/24 dev em1 table net46
ip route del default via 192.168.45.1 table net45
ip route del default via 192.168.46.1 table net46
ip rule del from 192.168.45.0/24 lookup net45
ip rule del from 192.168.46.0/24 lookup net46

