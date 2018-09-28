#!/bin/sh

exec /usr/lib/zabbix/externalscripts/zbxApacheStatusCheck -c m1 --url=https://cloud-platform.eurecom.fr/server-status?auto

