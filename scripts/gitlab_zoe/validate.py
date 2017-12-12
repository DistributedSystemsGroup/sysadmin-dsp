#!/usr/bin/python

import json
import sys
import requests

URL = sys.argv[1]
files = sys.argv[2:]

for f in files:
    data = json.load(open(f, encoding="utf-8"))
    data_req = { "application": data }
    r = requests.post(URL, json=data_req)
    if r.status_code != 200:
        rep = r.json()
        print(rep['message'])
        sys.exit(1)

