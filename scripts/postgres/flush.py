#!/usr/bin/env python3

import csv
from datetime import date, timedelta
import gzip
import os.path
import sys

from dateutil import parser
import psycopg2
import psycopg2.extras

def dump_table(table_name, where_clause, outfile_base, days):
    print('Dumping table {} with criteria {}'.format(table_name, where_clause))
    if where_clause is not None:
        q = "SELECT date_trunc('day', timestamp) as oldest_day FROM {} WHERE {} ORDER BY timestamp ASC LIMIT 1".format(table_name, where_clause)
    else:
        q = "SELECT date_trunc('day', timestamp) as oldest_day FROM {} ORDER BY timestamp ASC LIMIT 1".format(table_name)

    cur.execute(q)
    oldest_day = cur.fetchone()['oldest_day'].date()

    while oldest_day < date.today() - timedelta(days=days):
        print('Dumping {}'.format(oldest_day))
        outfile = '{}_{}.csv.gz'.format(outfile_base, oldest_day)
        current_file = gzip.open(outfile, mode='at', encoding='utf-8', newline='')
        newfile = True

        if where_clause is not None:
            q = "SELECT * FROM {} WHERE {} AND DATE(timestamp) = %s ORDER BY timestamp ASC".format(table_name, where_clause)
        else:
            q = "SELECT * FROM {} WHERE DATE(timestamp) = %s ORDER BY timestamp ASC".format(table_name)

        cur.execute(q, (oldest_day,))
        count = 0
        for row in cur:
            row = dict(row)
            if newfile:
                writer = csv.DictWriter(current_file, row.keys())
                writer.writeheader()
                newfile = False
            writer.writerow(row)
            count += 1
            # sys.stderr.write('Wrote {} lines\r'.format(count))
        print('Wrote {} lines'.format(count))
        print('Deleting rows for {}'.format(oldest_day))
        if where_clause is not None:
            q = "DELETE FROM {} WHERE {} AND DATE(timestamp) = %s".format(table_name, where_clause)
        else:
            q = "DELETE FROM {} WHERE DATE(timestamp) = %s".format(table_name)
        cur.execute(q, (oldest_day,))
        dbconn.commit()
        oldest_day += timedelta(days=1)


dbpass = open('/mnt/cephfs/admin/postgresql.pass', 'r').read().strip()

dsn = 'dbname=metrics user=postgres password={} host=bf11 port=5432'.format(dbpass)
dbconn = psycopg2.connect(dsn)

cur = dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# cleanup useless data
print('Deleting metrics about single disk partitions older than 4 days')
q = "DELETE FROM diskio WHERE name LIKE 'sd__' AND timestamp < (now() - interval '4d')"
cur.execute(q)
dbconn.commit()

dump_table('cpu', "cpu != 'cpu-total'", '/srv/logs/temp/percore', 4)
dump_table('cpu', "cpu = 'cpu-total'", '/srv/logs/temp/total', 15)
dump_table('diskio', None, '/srv/logs/temp/diskio', 15)
dump_table('docker', None, '/srv/logs/temp/docker', 15)
dump_table('docker_container_cpu', None, '/srv/logs/temp/docker_container_cpu', 15)
dump_table('docker_container_blkio', None, '/srv/logs/temp/docker_container_blkio', 15)
dump_table('docker_container_mem', None, '/srv/logs/temp/docker_container_mem', 15)
dump_table('docker_container_net', None, '/srv/logs/temp/docker_container_net', 15)
dump_table('kafkapost', None, '/srv/logs/temp/kafkapost', 7)
dump_table('mem', None, '/srv/logs/temp/mem', 15)
dump_table('net', None, '/srv/logs/temp/net', 15)
dump_table('netstat', None, '/srv/logs/temp/netstat', 15)
dump_table('ping', None, '/srv/logs/temp/ping', 15)
dump_table('swap', None, '/srv/logs/temp/swap', 15)

