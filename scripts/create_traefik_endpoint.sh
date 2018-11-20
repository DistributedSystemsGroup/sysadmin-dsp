#!/bin/bash

set -e

ZKCLI=/usr/share/zookeeper/bin/zkCli.sh

ENDPOINT_NAME=$1
BACKEND_URL=$2
PATH_PREFIX=$3

cmds="
create /traefik/backends/${ENDPOINT_NAME} ''
create /traefik/backends/${ENDPOINT_NAME}/servers ''
create /traefik/backends/${ENDPOINT_NAME}/servers/server ''
create /traefik/backends/${ENDPOINT_NAME}/servers/server/url '${BACKEND_URL}'

create /traefik/frontends/${ENDPOINT_NAME} ''
create /traefik/frontends/${ENDPOINT_NAME}/routes ''
create /traefik/frontends/${ENDPOINT_NAME}/routes/path ''
create /traefik/frontends/${ENDPOINT_NAME}/routes/path/rule 'PathPrefix:${PATH_PREFIX}'
create /traefik/frontends/${ENDPOINT_NAME}/backend '${ENDPOINT_NAME}'
create /traefik/alias ''
delete /traefik/alias
"
echo "$cmds" | $ZKCLI

