#!/usr/bin/env python3

import csv
from dateutil import parser
import gzip
import os.path
import sys

try:
    input_file = sys.argv[1]
except:
    print('Usage: {} <input csv file>'.format(sys.argv[0]))
    sys.exit(1)

if not os.path.exists(input_file):
    print('Input file does not exists')
    sys.exit(0)

outfile_base = '.'.join(input_file.split('.')[:-1])

with open(input_file) as csvfile:
    reader = csv.DictReader(csvfile)
    current_day = None
    current_file = None
    writer = None
    for row in reader:
#        timestamp = parser.parse(row['timestamp'])
        timestamp = row['timestamp'][:10]
        if current_day is None or current_day != timestamp:
            print(timestamp)
            current_day = timestamp
            if current_file is not None:
                current_file.close()
            if os.path.exists('{}_{}.csv.gz'.format(outfile_base, timestamp)):
                new_file = False
            else:
                new_file = True
            current_file = gzip.open('{}_{}.csv.gz'.format(outfile_base, timestamp), mode='at', encoding='utf-8', newline='')
            writer = csv.DictWriter(current_file, row.keys())
            if new_file:
                writer.writeheader()
        writer.writerow(row)

