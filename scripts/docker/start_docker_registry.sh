#!/bin/sh

sudo docker run -d -p 5000:5000 --name registry --restart=always -v /mnt/docker/registry-data:/var/lib/registry -e REGISTRY_STORAGE_DELETE_ENABLED=True registry:2

