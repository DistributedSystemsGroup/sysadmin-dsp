#!/bin/bash

SCRIPT_BASE=/mnt/cephfs/admin/sysadmin-dsp/scripts/postgres
DATASET_PATH=/mnt/cephfs/datasets/platform/postgres/
TEMP_DIR=/srv/logs/temp

cd $TEMP_DIR

$SCRIPT_BASE/flush.py

mv percore* $DATASET_PATH/cpu
mv total* $DATASET_PATH/cpu

mv kafkapost* $DATASET_PATH/kafkapost

mv diskio* $DATASET_PATH/diskio

mv docker_container_cpu* $DATASET_PATH/docker_container_cpu
mv docker_container_mem* $DATASET_PATH/docker_container_mem
mv docker_container_net* $DATASET_PATH/docker_container_net
mv docker_container_blkio* $DATASET_PATH/docker_container_blkio
mv docker* $DATASET_PATH/docker

mv mem* $DATASET_PATH/mem
mv netstat* $DATASET_PATH/netstat
mv net* $DATASET_PATH/net
mv ping* $DATASET_PATH/ping
mv swap* $DATASET_PATH/swap

