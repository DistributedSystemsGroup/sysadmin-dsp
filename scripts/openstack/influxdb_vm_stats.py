#!/usr/bin/python3

import json
import re
import subprocess
from typing import Dict

import psycopg2
import requests
import libvirt

PW_FILE = '/mnt/cephfs/admin/postgresql.pass'


def db_conn(dbname):
    pw = open(PW_FILE).read().strip()
    return psycopg2.connect(dbname=dbname, user='postgres', host='192.168.46.31', password=pw)


def openstack_user_id(user_id: str) -> str:
    cursor = db_conn('keystone').cursor()
    cursor.execute('SELECT name FROM local_user WHERE user_id=%s', (user_id,))
    ret = cursor.fetchone()
    if ret is not None:
        return ret[0]
    else:
        return user_id


def openstack_project_id(group_id: str) -> str:
    cursor = db_conn('keystone').cursor()
    cursor.execute('SELECT name FROM project WHERE id=%s', (group_id,))
    ret = cursor.fetchone()
    if ret is not None:
        return ret[0]
    else:
        return group_id


def openstack_image_id(image_id: str) -> str:
    cursor = db_conn('glance').cursor()
    cursor.execute('SELECT name FROM images WHERE id=%s', (image_id,))
    ret = cursor.fetchone()
    if ret is not None:
        return ret[0]
    else:
        return image_id


def volumes_usage(data):
    cp = subprocess.run(["rbd", "du", "-p", "volumes", "--format", "json"], stdout=subprocess.PIPE)
    vols = json.loads(cp.stdout.decode('utf-8'))['images']
    for volume in data['volumes']:
        for v in vols:
            if volume['id'] in v['name']:
                volume['used'] = v['used_size']


def os_volumes_by_user(data):
    q = 'SELECT id, user_id, project_id, size FROM volumes WHERE deleted_at IS NULL'
    cur = db_conn("cinder").cursor()
    cur.execute(q)
    volumes = []
    for uuid, user_id, project_id, size in cur.fetchall():
        volume = {
            'id': uuid,
            'user': openstack_user_id(user_id).replace(' ', '\ '),
            'project': openstack_project_id(project_id).replace(' ', '\ '),
            'size': size * (1024**3)
        }
        volumes.append(volume)
    data['volumes'] = volumes


def os_vms(data):
    q = 'SELECT id, uuid, display_name, user_id, project_id, vcpus, memory_mb, root_gb + ephemeral_gb as disk_gb, node, image_ref FROM instances WHERE deleted_at IS NULL'
    cur = db_conn("nova").cursor()
    cur.execute(q, data)
    vms = []
    for table_id, vm_id, name, user_id, project_id, vcpus, memory_mb, disk_gb, node, image_ref in cur.fetchall():
        vm = {
            'id': vm_id,
            'table_id': table_id,
            'name': name.replace(' ', '\ '),
            'user': openstack_user_id(user_id).replace(' ', '\ '),
            'project': openstack_project_id(project_id).replace(' ', '\ '),
            'vcpus': vcpus,
            'memory': memory_mb * (1024**2),
            'disk': disk_gb * (1024**3),
            'node': node,
            'image': openstack_image_id(image_ref).replace(' ', '\ ')
        }
        vms.append(vm)
    data['vms'] = vms


def os_usage(data):
    for vm in data['vms']:
        usage = {}
        vm_id = 'instance-%08x' % vm['table_id']
        host = vm['node']
        conn = libvirt.openReadOnly('remote+tcp://{}'.format(host))
        dom = conn.lookupByName(vm_id)
        vcpu_time = 0
        net_rx_pkts = 0
        net_rx_errs = 0
        net_rx_drop = 0
        net_rx_bytes = 0
        net_tx_pkts = 0
        net_tx_errs = 0
        net_tx_drop = 0
        net_tx_bytes = 0
        block_capacity = 0
        block_physical = 0
        block_allocation = 0
        block_rd_bytes = 0
        block_rd_times = 0
        block_rd_reqs = 0
        block_wr_bytes = 0
        block_wr_times = 0
        block_wr_reqs = 0
        for k, v in conn.domainListGetStats([dom])[0][1].items():
            if re.match('vcpu\.[0-9]+\.time', k):
                vcpu_time += v
            elif re.match('net\.[0-9]+\.rx\.pkts', k):
                net_rx_pkts += v
            elif re.match('net\.[0-9]+\.rx\.errs', k):
                net_rx_errs += v
            elif re.match('net\.[0-9]+\.rx\.drop', k):
                net_rx_drop += v
            elif re.match('net\.[0-9]+\.rx\.bytes', k):
                net_rx_bytes += v
            elif re.match('net\.[0-9]+\.tx\.pkts', k):
                net_tx_pkts += v
            elif re.match('net\.[0-9]+\.tx\.errs', k):
                net_tx_errs += v
            elif re.match('net\.[0-9]+\.tx\.drop', k):
                net_tx_drop += v
            elif re.match('net\.[0-9]+\.tx\.bytes', k):
                net_tx_bytes += v
            elif re.match('block\.[0-9]+\.capacity', k):
                block_capacity += v
            elif re.match('block\.[0-9]+\.physical', k):
                block_physical += v
            elif re.match('block\.[0-9]+\.allocation', k):
                block_allocation += v
            elif re.match('block\.[0-9]+\.rd\.bytes', k):
                block_rd_bytes += v
            elif re.match('block\.[0-9]+\.rd\.times', k):
                block_rd_times += v
            elif re.match('block\.[0-9]+\.rd\.reqs', k):
                block_rd_reqs += v
            elif re.match('block\.[0-9]+\.wr\.bytes', k):
                block_wr_bytes += v
            elif re.match('block\.[0-9]+\.wr\.times', k):
                block_wr_times += v
            elif re.match('block\.[0-9]+\.wr\.reqs', k):
                block_wr_reqs += v
            elif re.match('balloon\.(unused|maximum|rss|available|usable|current|swap_in|swap_out)', k):
                usage[k] = v

        usage['vcpu_time'] = vcpu_time
        usage['net_rx_pkts'] = net_rx_pkts 
        usage['net_rx_errs'] = net_rx_errs 
        usage['net_rx_drop'] = net_rx_drop 
        usage['net_rx_bytes'] = net_rx_bytes
        usage['net_tx_pkts'] = net_tx_pkts 
        usage['net_tx_errs'] = net_tx_errs 
        usage['net_tx_drop'] = net_tx_drop 
        usage['net_tx_bytes'] = net_tx_bytes
        usage['block_capacity'] = block_capacity
        usage['block_physical'] = block_physical
        usage['block_allocation'] = block_allocation
        usage['block_rd_bytes'] = block_rd_bytes
        usage['block_rd_times'] = block_rd_times
        usage['block_rd_reqs'] = block_rd_reqs
        usage['block_wr_bytes'] = block_wr_bytes
        usage['block_wr_times'] = block_wr_times
        usage['block_wr_reqs'] = block_wr_reqs

        usage_data = 'openstack_vm_usage,name={},user={},project={},id={},node={} '.format(vm['name'], vm['user'], vm['project'], vm['id'], host)
        for k, v in usage.items():
            usage_data += "{}={},".format(k, v)
        usage_data = usage_data[:-1]
        requests.post('http://bf5:8086/write?db=telegraf', data=usage_data)


def build_data() -> Dict:
    data = {}
    os_volumes_by_user(data)
    volumes_usage(data)
    for volume in data['volumes']:
        influx_data = 'openstack_volumes,id={},user={},project={} size={},used={}'.format(volume['id'], volume['user'], volume['project'], volume['size'], volume['used'])
        requests.post('http://bf5:8086/write?db=telegraf', data=influx_data)

    data = {}
    os_vms(data)
    for vm in data['vms']:
        vm_data = 'openstack_vm,id={},name={},user={},project={},node={},image={} vcpus={},memory={},disk={}'.format(vm['id'], vm['name'], vm['user'], vm['project'], vm['node'], vm['image'], vm['vcpus'], vm['memory'], vm['disk'])
        requests.post('http://bf5:8086/write?db=telegraf', data=vm_data)

    os_usage(data)
    return data


if __name__ == '__main__':
    raw_data = build_data()
    #print(raw_data)

