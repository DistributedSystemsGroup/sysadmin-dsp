#!/bin/sh

if [ -z $1 ]; then
    echo "Usage: $0 <username>"
    exit
fi

HADOOP_USER_NAME=root hdfs dfs -mkdir /user/$1
HADOOP_USER_NAME=root hdfs dfs -chown $1 /user/$1
HADOOP_USER_NAME=root hdfs dfs -chmod 750 /user/$1

