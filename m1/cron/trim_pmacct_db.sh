#!/bin/bash

echo "delete from acct where stamp_updated < now() - interval '1 month';" | psql -h bf11 -U postgres -w pmacct

