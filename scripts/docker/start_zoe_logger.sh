#!/bin/sh

docker run -d -e ZOE_LOGGER_DEBUG=true -e ZOE_LOGGER_KAFKA-BROKER=bf5:9092 -p 12201:12201/udp --name log-producer --restart always docker-logger

#docker run -d -e PQ_CONSUMER_DEBUG=true \
#	      -e PQ_CONSUMER_KAFKA-BROKER=192.168.45.252:9092 \
#	      -e PQ_CONSUMER_DB_NAME=docker_logs \
#	      -e PQ_CONSUMER_DB_USER=postgres \
#	      -e PQ_CONSUMER_DB_PASS=zoepostgres \
#	      -e PQ_CONSUMER_DB_HOST=192.168.45.252 \
#	      --restart always \
#	      --name log-consumer docker-logger python3 /opt/zoe-logger/pq-consumer.py
#
#docker run -d -e ZOE_WEB_DEBUG=true \
#	      -e ZOE_WEB_DB_NAME=docker_logs \
#	      -e ZOE_WEB_DB_HOST=192.168.45.252 \
#	      -e ZOE_WEB_DB_PASS=zoepostgres \
#	      -p 6577:6577 \
#	      --restart always \
#	      --name log-web docker-logger python3 /opt/zoe-logger/web.py
#
