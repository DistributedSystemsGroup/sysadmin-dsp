from collections import Counter
from datetime import datetime, timedelta, date, time
import sys
import socket
from typing import Dict
import os

import geoip2.database
from jinja2 import Environment, FileSystemLoader, select_autoescape
import psycopg2

OUTPUT_BASE_DIR = '/mnt/cephfs/datasets/reports'
PW_FILE = '/mnt/cephfs/admin/postgresql.pass'
GEOIP_DB = '/mnt/cephfs/admin/sysadmin-dsp/scripts/dp_reports/GeoLite2-City.mmdb'
TEMPLATE_PATH = '/mnt/cephfs/admin/sysadmin-dsp/scripts/dp_reports/templates'


def db_conn(dbname):
    pw = open(PW_FILE).read().strip()
    return psycopg2.connect(dbname=dbname, user='postgres', host='192.168.46.31', password=pw)


def dns_by_hand(ip):
    if ip == '192.168.46.31':
        return 'SSH GW'
    elif ip == '192.168.46.21':
        return 'bf1'
    elif ip == '192.168.46.22':
        return 'bf2'
    elif ip == '192.168.46.23':
        return 'bf3'
    elif ip == '192.168.46.24':
        return 'bf4'
    elif ip == '192.168.46.25':
        return 'bf5'
    elif ip == '192.168.46.26':
        return 'bfeb'
    elif ip == '192.168.46.27':
        return 'bf7'
    elif ip == '192.168.46.28':
        return 'bf8'
    elif ip == '192.168.46.29':
        return 'bf9'
    elif ip == '192.168.46.30':
        return 'bf10'
    elif ip == '192.168.46.32':
        return 'bf12'
    elif ip == '192.168.46.33':
        return 'bf13'
    elif ip == '192.168.46.34':
        return 'bf14'
    elif ip == '192.168.46.35':
        return 'bf15'
    elif ip == '192.168.46.36':
        return 'bf16'
    elif ip == '192.168.46.37':
        return 'bf17'
    elif ip == '192.168.46.38':
        return 'bf18'
    elif ip == '192.168.46.39':
        return 'bf19'
    elif ip == '192.168.46.40':
        return 'bf20'
    elif ip == '192.168.46.41':
        return 'bf21'
    elif ip == '192.168.46.42':
        return 'bf22'
    elif ip == '192.168.46.50':
        return 'deepfoot1'
    elif '.47.' in ip or '.45.' in ip:
        cursor = db_conn('neutron').cursor()
        cursor.execute('SELECT dns_name FROM portdnses JOIN ipallocations ON portdnses.port_id=ipallocations.port_id WHERE ip_address=%s', (ip,))
        ret = cursor.fetchone()
        if ret is not None:
            return ret[0]
        else:
            return ip
    else:
        return ip


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


def zoe_users_running_executions(data):
    q = "select prod.user.username, count(prod.execution.id) from prod.execution JOIN prod.user on prod.execution.user_id=prod.user.id where time_start BETWEEN %s AND %s group by prod.user.username"
    cursor = db_conn("zoe").cursor()
    usernames = []
    counts = []
    cursor.execute(q, (data['time_start'], data['time_end']))
    for username, count in cursor.fetchall():
        usernames.append(username)
        counts.append(count)
    data['plot_1'] = {
        'title': 'Running executions',
        'usernames': usernames,
        'executions': counts
    }


def zoe_execution_wordcloud(data):
    q = 'select name from prod.execution WHERE time_submit BETWEEN %s AND %s'
    cursor = db_conn("zoe").cursor()
    cursor.execute(q, (data['time_start'], data['time_end']))
    words = [y for x in cursor.fetchall() for y in x[0].split()]
    counts = Counter(words)
    data['plot_2'] = {
        'title': 'Execution names',
        'wordlist': [[x, y] for x, y in counts.items()]
    }


def zoe_queue_time(data):
    q = '''select CASE
            WHEN (time_start - time_submit) < interval '1 second' THEN 'less than 1s'
            WHEN (time_start - time_submit) BETWEEN interval '1 second' AND interval '1 minute' THEN 'between 1s and 1m'
            WHEN (time_start - time_submit) BETWEEN interval '1 minute' AND interval '5 minute' THEN 'between 1m and 5m'
            ELSE 'more than 5m'
        END as queue_time,
        count(*) as count
        from prod.execution
        where time_start is not null AND time_submit BETWEEN %s AND %s
        group by queue_time'''
    cursor = db_conn("zoe").cursor()
    cursor.execute(q, (data['time_start'], data['time_end']))
    queue_times = []
    counts = []
    for bucket, count in cursor.fetchall():
        queue_times.append(bucket)
        counts.append(count)
    data['plot_3'] = {
        'title': 'Queue time',
        'queue_times': queue_times,
        'counts': counts
    }


def zoe_run_time(data):
    q = '''select CASE
                WHEN time_end - time_start BETWEEN interval '1 minute' AND interval '10 minute' THEN 'between 1m and 10m'
                WHEN time_start - time_submit BETWEEN interval '10 minute' AND interval '5 hour' THEN 'between 10m and 5h'
                WHEN time_start - time_submit BETWEEN interval '5 hour' AND interval '1 day' THEN 'between 5h and 1d'
                ELSE 'more than 1d'
            END as execution_time,
            count(*) as count
        from prod.execution
        where time_start is not null and time_end is not null and status = 'terminated' AND time_submit BETWEEN %s AND %s AND time_end - time_start >= interval '1 minute'
        group by execution_time'''
    cursor = db_conn("zoe").cursor()
    cursor.execute(q, (data['time_start'], data['time_end']))
    run_times = []
    counts = []
    for bucket, count in cursor.fetchall():
        run_times.append(bucket)
        counts.append(count)
    data['plot_4'] = {
        'title': 'Run times',
        'run_times': run_times,
        'counts': counts
    }


def platform_ssh_from_outside(data):
    q = '''select
         host(ip_src) as source,
         sum(bytes) as size
     FROM acct
     WHERE
         stamp_inserted BETWEEN %s AND %s AND
         ip_dst = inet '192.168.46.31/32' AND
         NOT (
             ip_src << inet '192.168.0.0/16' OR
             ip_src << inet '172.24.0.0/16' OR
             ip_src << inet '172.17.0.0/16' OR
             ip_src << inet '172.16.0.0/16' OR
             ip_src << inet '224.0.0.0/24'
         ) AND
         ip_proto = 6 and port_dst = 22
     group by ip_src
     order by size desc
     LIMIT 100
    '''
    cur = db_conn("pmacct").cursor()
    cur.execute(q, (data['time_start'], data['time_end']))
    ipdata = cur.fetchall()
    reader = geoip2.database.Reader(GEOIP_DB)
    ips = []
    lats = []
    longs = []
    sizes = []
    count = 0
    reverse_dns = []
    for ip, size in ipdata:
        ips.append(ip)
        lats.append(reader.city(ip).location.latitude)
        longs.append(reader.city(ip).location.longitude)
        sizes.append(int(size))
        if count < 10:
            try:
                reverse_dns.append(socket.gethostbyaddr(ip)[0])
            except socket.herror:
                reverse_dns.append('-')
        count += 1
    data['cp_1'] = {
        'table_rows': range(min(len(ips), 10)),
        'ips': ips,
        'lats': lats,
        'longs': longs,
        'sizes': sizes,
        'reverse_dns': reverse_dns
    }


def platform_to_outside(data):
    q = '''select
         host(ip_dst) as dest,
         sum(bytes) as size,
         array_agg(host(ip_src)) as src
    FROM acct
    WHERE
        stamp_inserted BETWEEN %s AND %s AND
        NOT (
            ip_dst << inet '192.168.0.0/16' OR
            ip_dst << inet '172.24.0.0/16' OR
            ip_dst << inet '172.17.0.0/16' OR
            ip_dst << inet '172.16.0.0/16' OR
            ip_dst << inet '224.0.0.0/24' OR
            ip_dst = '0.0.0.0/32' OR
            ip_dst = '255.255.255.255/32' OR 
            ip_dst << inet '169.254.0.0/16'
        ) AND
        ip_src <> '192.168.104.218/32'
    group by ip_dst
    order by size desc
    LIMIT 100
    '''
    cur = db_conn("pmacct").cursor()
    cur.execute(q, (data['time_start'], data['time_end']))
    ipdata = cur.fetchall()
    reader = geoip2.database.Reader(GEOIP_DB)
    ips = []
    lats = []
    longs = []
    sizes = []
    count = 0
    reverse_dns = []
    sources = []
    for ip, size, source in ipdata:
        ips.append(ip)
        lats.append(reader.city(ip).location.latitude)
        longs.append(reader.city(ip).location.longitude)
        sizes.append(int(size))
        if count < 10:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                if 'github.com' in hostname:
                    hostname = 'GitHub'
                reverse_dns.append(hostname)
            except socket.herror:
                reverse_dns.append('-')
        count += 1
        sources.append(" ".join([dns_by_hand(x) for x in list(set(source))]))
    data['cp_2'] = {
        'table_rows': range(min(len(ips), 10)),
        'ips': ips,
        'lats': lats,
        'longs': longs,
        'sizes': sizes,
        'reverse_dns': reverse_dns,
        'sources': sources
    }


def os_volumes_by_user(data):
    q = 'SELECT user_id, SUM(size) FROM volumes WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY user_id'
    cur = db_conn("cinder").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for user_id, size in cur.fetchall():
        sizes.append(size * (1024**3))
        users.append(openstack_user_id(user_id))
    data['os_1'] = {
        'sizes': sizes,
        'users': users
    }


def os_disk_by_user(data):
    q = 'SELECT user_id, SUM(root_gb + ephemeral_gb) FROM instances WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY user_id'
    cur = db_conn("nova").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for user_id, size in cur.fetchall():
        sizes.append(size * (1024**3))
        users.append(openstack_user_id(user_id))
    data['os_2'] = {
        'sizes': sizes,
        'users': users
    }


def os_memory_by_user(data):
    q = 'SELECT user_id, SUM(memory_mb) FROM instances WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY user_id'
    cur = db_conn("nova").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for user_id, size in cur.fetchall():
        sizes.append(size * (1024**2))
        users.append(openstack_user_id(user_id))
    data['os_3'] = {
        'sizes': sizes,
        'users': users
    }


def os_vcpus_by_user(data):
    q = 'SELECT user_id, SUM(vcpus) FROM instances WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY user_id'
    cur = db_conn("nova").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for user_id, size in cur.fetchall():
        sizes.append(size)
        users.append(openstack_user_id(user_id))
    data['os_4'] = {
        'sizes': sizes,
        'users': users
    }


def os_volumes_by_project(data):
    q = 'SELECT project_id, SUM(size) FROM volumes WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY project_id'
    cur = db_conn("cinder").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for project_id, size in cur.fetchall():
        sizes.append(size * (1024**3))
        users.append(openstack_project_id(project_id))
    data['osp_1'] = {
        'sizes': sizes,
        'users': users
    }


def os_disk_by_project(data):
    q = 'SELECT project_id, SUM(root_gb + ephemeral_gb) FROM instances WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY project_id'
    cur = db_conn("nova").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for user_id, size in cur.fetchall():
        sizes.append(size * (1024**3))
        users.append(openstack_project_id(user_id))
    data['osp_2'] = {
        'sizes': sizes,
        'users': users
    }


def os_memory_by_project(data):
    q = 'SELECT project_id, SUM(memory_mb) FROM instances WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY project_id'
    cur = db_conn("nova").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for user_id, size in cur.fetchall():
        sizes.append(size * (1024**2))
        users.append(openstack_project_id(user_id))
    data['osp_3'] = {
        'sizes': sizes,
        'users': users
    }


def os_vcpus_by_project(data):
    q = 'SELECT project_id, SUM(vcpus) FROM instances WHERE (created_at <= %(time_end)s AND deleted_at IS NULL) OR (deleted_at BETWEEN %(time_start)s AND %(time_end)s) OR (created_at BETWEEN %(time_start)s AND %(time_end)s) AND (created_at <= %(time_start)s AND deleted_at >= %(time_end)s) GROUP BY project_id'
    cur = db_conn("nova").cursor()
    cur.execute(q, data)
    users = []
    sizes = []
    for user_id, size in cur.fetchall():
        sizes.append(size)
        users.append(openstack_project_id(user_id))
    data['osp_4'] = {
        'sizes': sizes,
        'users': users
    }


def build_data(mode: str) -> Dict:
    data = {}
    ref_date = date.today() - timedelta(days=1)
    if mode == 'daily':
        data['time_start'] = datetime.combine(ref_date, time.min)
        data['time_end'] = datetime.combine(ref_date, time.max)
    elif mode == 'weekly':
        data['time_end'] = datetime.combine(ref_date, time.max)
        data['time_start'] = datetime.combine(ref_date, time.min) - timedelta(days=7)
    elif mode == 'monthly':
        data['time_end'] = datetime.combine(ref_date, time.max)
        data['time_start'] = datetime.combine(ref_date, time.min) - timedelta(days=30)

    zoe_users_running_executions(data)
    zoe_execution_wordcloud(data)
    zoe_queue_time(data)
    zoe_run_time(data)
    platform_ssh_from_outside(data)
    platform_to_outside(data)
    os_volumes_by_user(data)
    os_disk_by_user(data)
    os_memory_by_user(data)
    os_vcpus_by_user(data)
    os_volumes_by_project(data)
    os_disk_by_project(data)
    os_memory_by_project(data)
    os_vcpus_by_project(data)
    return data


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ['daily', 'weekly', 'monthly']:
        print('Usage: {} <daily|weekly|monthly>'.format(sys.argv[0]))
        sys.exit(1)
    else:
        mode = sys.argv[1]
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_PATH), autoescape=select_autoescape(['html', 'xml']))
    template = jinja_env.get_template('index.jinja2')
    template_vars = build_data(mode)
    with open(os.path.join(OUTPUT_BASE_DIR, mode, 'report-{}.html'.format(date.today().isoformat())), 'w') as fp:
        fp.write(template.render(**template_vars))
