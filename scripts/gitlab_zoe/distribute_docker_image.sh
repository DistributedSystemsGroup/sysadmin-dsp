#!/bin/sh

# This script is run by GitLab CI in a container

HOSTS="bf5 bf7 bf8 bf9 bf10 bf12 bf13 bf14 bf15 bf16 bf17 bf18 bf19 bf20 bf21 bf22 deepfoot1"
DOCKER_PORT=2375

DOCKER_TLS_VERIFY=1
DOCKER_CERT_PATH=${DOCKER_CERT_PATH:-/certs}
DOCKER_OPTS="--tlsverify --tlscacert $DOCKER_CERT_PATH/ca.pem --tlscert $DOCKER_CERT_PATH/cert.pem --tlskey $DOCKER_CERT_PATH/key.pem"

if [ -z "$1" ]; then
    echo "Missing image name"
    exit
fi

docker save $1 > img.tar
for host in ${HOSTS}; do
    echo "Sending image to host $host..."
    cat img.tar | docker ${DOCKER_OPTS} -H ${host}.containers.bigfoot.eurecom.fr:${DOCKER_PORT} load
done
rm -f img.tar

