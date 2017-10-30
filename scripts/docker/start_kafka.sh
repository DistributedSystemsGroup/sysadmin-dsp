#!/bin/bash

docker run -d -e KAFKA_HEAP_OPTS="-Xmx4G -Xms1G" -e KAFKA_BROKER_ID=1 -e KAFKA_ZOOKEEPER_CONNECT=bf1:2181,bf5:2181,bf11:2181 -v /mnt/kafka:/kafka -p 9092:9092 -p 9999:9999 -e KAFKA_ADVERTISED_HOST_NAME=bf5 -e KAFKA_ADVERTISED_PORT=9092 -e KAFKA_DELETE_TOPIC_ENABLE=true --restart=always --name kafka-1 wurstmeister/kafka:0.9.0.1

docker -H bf5:2380 run -d -e constraint:node==bf12 -e KAFKA_HEAP_OPTS="-Xmx4G -Xms1G" -e KAFKA_BROKER_ID=2 -e KAFKA_ZOOKEEPER_CONNECT=bf1:2181,bf5:2181,bf11:2181 -v /mnt/kafka:/kafka -p 9092:9092 -p 9999:9999 -e JMX_PORT=9999 -e KAFKA_ADVERTISED_HOST_NAME=bf12 -e KAFKA_ADVERTISED_PORT=9092 -e KAFKA_DELETE_TOPIC_ENABLE=true --restart=always --name kafka-2 wurstmeister/kafka:0.9.0.1

docker -H bf5:2380 run -d -e constraint:node==bf13 -e KAFKA_HEAP_OPTS="-Xmx4G -Xms1G" -e KAFKA_BROKER_ID=3 -e KAFKA_ZOOKEEPER_CONNECT=bf1:2181,bf5:2181,bf11:2181 -v /mnt/kafka:/kafka -p 9092:9092 -p 9999:9999 -e JMX_PORT=9999 -e KAFKA_ADVERTISED_HOST_NAME=bf13 -e KAFKA_ADVERTISED_PORT=9092 -e KAFKA_DELETE_TOPIC_ENABLE=true --restart=always --name kafka-3 wurstmeister/kafka:0.9.0.1


