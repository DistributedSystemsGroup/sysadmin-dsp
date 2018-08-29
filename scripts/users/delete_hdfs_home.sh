#!/bin/sh

if [ -z $1 ]; then
    echo "Usage: $0 <username>"
    exit
fi

HADOOP_USER_NAME=root hdfs dfs -rm -skipTrash -r /user/$1

