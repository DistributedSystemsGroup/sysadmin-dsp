#!/bin/sh

export PYTHONPATH=/home/venzano/vcs/pyostack
cd /home/venzano/vcs/openstack_docs/scripts/dashboard_generator/
./per_tenant.py
./wasted_tenant.py

