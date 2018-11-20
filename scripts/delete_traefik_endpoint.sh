
#!/bin/bash

set -e

ZKCLI=/usr/share/zookeeper/bin/zkCli.sh

ENDPOINT_NAME=$1

cmds="
rmr /traefik/backends/${ENDPOINT_NAME}
rmr /traefik/frontends/${ENDPOINT_NAME}
create /traefik/alias ''
delete /traefik/alias
"
echo "$cmds" | $ZKCLI

