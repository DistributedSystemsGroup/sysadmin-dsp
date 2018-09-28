#!/usr/bin/python3

import subprocess
import json

import requests

cp = subprocess.run(["openstack", "project", "list", "-f", "json"], stdout=subprocess.PIPE)
tenants = json.loads(cp.stdout.decode('utf-8'))

cp = subprocess.run(["openstack", "user", "list", "-f", "json"], stdout=subprocess.PIPE)
users = json.loads(cp.stdout.decode('utf-8'))

cp = subprocess.run(["openstack", "port", "list", "-f", "json"], stdout=subprocess.PIPE)
ports = json.loads(cp.stdout.decode('utf-8'))

cp = subprocess.run(["openstack", "image", "list", "-f", "json"], stdout=subprocess.PIPE)
images = json.loads(cp.stdout.decode('utf-8'))

cp = subprocess.run(["openstack", "server", "list", "--all-projects", "-f", "json"], stdout=subprocess.PIPE)
servers = json.loads(cp.stdout.decode('utf-8'))

cp = subprocess.run(["openstack", "volume", "list", "--all-projects", "-f", "json"], stdout=subprocess.PIPE)
volumes = json.loads(cp.stdout.decode('utf-8'))

influx_data = 'openstack tenants={},users={},ports={},images={},servers={},volumes={}'.format(len(tenants), len(users), len(ports), len(images), len(servers), len(volumes))

requests.post('http://bf5:8086/write?db=telegraf', data=influx_data)

