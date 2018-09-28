#!/bin/bash
set -e 

GREEN=$'\e[32;01m'
RED=$'\e[31;01m'
NORMAL=$'\e[0m'
YELLOW=$'\e[33;01m'
WHITE=$'\e[37;01m'
BLUE=$'\e[34;01m'
CYAN=$'\e[36;01m'
PURPLE=$'\e[35;01m'
RESTORE=$'\e[00;00m'

function error {
    echo "${RED}AN ERROR OCCURRED - RESTORING A SAFE STATE${RESTORE}"
    echo "${PURPLE}Line number: $@ ${RESTORE}"
    /sbin/iptables -I OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT && echo "${YELLOW}Do not drop existing connections${RESTORE}"
    /sbin/iptables -I INPUT -p tcp --dport 22 -j ACCEPT && echo "${YELLOW}Ssh access enabled${RESTORE}"
    /sbin/iptables -I OUTPUT -p tcp --dport 22 -j ACCEPT && echo "${YELLOW}Ssh access enabled${RESTORE}"
    # We cannot fail, otherwise ifup script aborts
    exit 0
}
trap 'error ${LINENO}' ERR

case "$1" in
start)
#    echo "${BLUE}ENABLING BIGFOOT FORWARDING RULES${CYAN}"
#    echo "${BLUE}    FORWARD TABLE${RESTORE}"
#    /sbin/iptables -N bf-fwd
#    /sbin/iptables -A FORWARD -j bf-fwd
#    /sbin/iptables -A bf-fwd -m state --state ESTABLISHED,RELATED -j ACCEPT
#    /sbin/iptables -A bf-fwd -i eth0.46 -s 192.168.46.0/24 -o eth0.304 -j ACCEPT

    # Clamp MSS to get aroung Eurecom's blocking of ICMP
    /sbin/iptables -t mangle -A POSTROUTING -p tcp --tcp-flags SYN,RST SYN -o eth0.304 -j TCPMSS --set-mss 1400

    #nat
    echo "${BLUE}    NAT TABLE${RESTORE}"
    /sbin/iptables -t nat -N bf-nat-prerouting
    /sbin/iptables -t nat -A PREROUTING -j bf-nat-prerouting
    /sbin/iptables -t nat -N bf-nat-postrouting
    /sbin/iptables -t nat -A POSTROUTING -j bf-nat-postrouting

#    /sbin/iptables -t nat -A bf-nat-prerouting -i eth0.46 -p udp --dport 53 -j DNAT --to-destination 192.168.106.12
#    /sbin/iptables -t nat -A bf-nat-prerouting -i br-ex -p udp --dport 53 -j DNAT --to-destination 192.168.45.1
    /sbin/iptables -t nat -A bf-nat-postrouting -s 192.168.46.0/24 -o eth0.304 -j SNAT --to-source 192.168.104.218
    /sbin/iptables -t nat -A bf-nat-postrouting -s 192.168.45.0/24 -o eth0.304 -j SNAT --to-source 192.168.104.218
    /sbin/iptables -t nat -A bf-nat-postrouting -s 192.168.47.0/24 -o eth0.304 -j SNAT --to-source 192.168.104.218
    /sbin/iptables -t nat -A bf-nat-postrouting -d 192.168.47.0/24 -j SNAT --to-source 192.168.47.1
    /sbin/iptables -t nat -A bf-nat-postrouting -d 192.168.45.0/24 -j SNAT --to-source 192.168.45.1
    /sbin/iptables -t nat -A bf-nat-postrouting -d 192.168.46.0/24 -j SNAT --to-source 192.168.46.1
    echo "${GREEN}ROUTING STARTED${RESTORE}"
    ;;
stop)
    echo "${BLUE}DISABILING ROUTING${RESTORE}"
    /sbin/iptables -D FORWARD -j bf-fwd || true
    /sbin/iptables -F bf-fwd  || true
    /sbin/iptables -X bf-fwd  || true

    /sbin/iptables -t mangle -D POSTROUTING -p tcp --tcp-flags SYN,RST SYN -o eth0.304 -j TCPMSS --set-mss 1400

    #NAT
    /sbin/iptables -t nat -D PREROUTING -j bf-nat-prerouting  || true
    /sbin/iptables -t nat -F bf-nat-prerouting  || true
    /sbin/iptables -t nat -X bf-nat-prerouting  || true
    /sbin/iptables -t nat -D POSTROUTING -j bf-nat-postrouting  || true
    /sbin/iptables -t nat -F bf-nat-postrouting  || true
    /sbin/iptables -t nat -X bf-nat-postrouting  || true
    echo "${YELLOW}ROUTING DISABLED${RESTORE}"
    ;;

restart)
    shift
    echo $0
    /usr/bin/env bash $0 stop ${@}
    /bin/sleep 1
    /usr/bin/env bash $0 start ${@}
    ;;
*)
    echo "Usage: $0 {start|stop|restart}" >&2
    exit 1
    ;;

esac

