#!/bin/sh

ansible -b -a 'docker rmi $(docker images --filter "dangling=true" -q --no-trunc)' -m shell docker
