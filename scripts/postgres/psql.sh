#!/bin/bash

if [ -z $1 ]; then
    echo "Runs some SQL taken from a file on the metrics database"
    exit
fi

export PGPASSFILE=/mnt/cephfs/admin/sysadmin-dsp/scripts/postgres/pgpass

psql -f $1 -d metrics -h bf11 -U postgres

