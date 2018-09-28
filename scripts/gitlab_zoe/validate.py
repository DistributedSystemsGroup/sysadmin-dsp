#!/usr/bin/python

import json
import sys
import requests

URL = sys.argv[1]
files = sys.argv[2:]

for f in files:
    data = json.load(open(f, encoding="utf-8"))
    r = requests.post(URL, json=data)
    if r.status_code != 200:
        print(r.text)
        sys.exit(1)

