#!/bin/sh

docker run -d --restart=always -p 8880:8080 -e ZK=bf1:2181,bf5:2181,bf11:2181 --name kafka-monitor jpodeszwik/kafka-offset-monitor:0.2.1

