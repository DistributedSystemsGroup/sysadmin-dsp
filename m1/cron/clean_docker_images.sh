#!/bin/sh

ansible -u deploy -b -a 'docker rmi $(docker images --filter "dangling=true" -q --no-trunc)' -m shell docker

