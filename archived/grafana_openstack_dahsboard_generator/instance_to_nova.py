#!/usr/bin/python

import json
import pyostack
from pprint import pprint

DISK_TMPL = "alias(sumSeries({}.libvirt.disk_octets-*.*),{})"
NET_TMPL = "alias(sumSeries({}.libvirt.if_octets-*.*),{})"
CPU_TMPL = "alias(scale({}.libvirt.virt_cpu_total,1e-7),{})"

template = json.load(open("tenant_template.json"))

def new_row(tenant, servers):
    row_template = json.load(open("tenant_row_template.json"))
    row_template["title"] = tenant["name"]
    for i in servers:
        name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"]
#        try:
#            cpu_count = compute.get_vcpu_count(i)
#        except:
#            print("Warning, instance {} has an unknown flavor".format(i.name))
#            cpu_count = 1
        for p in row_template["panels"]:
            if p["title"] == "Disk usage":
                tmp = {}
                tmp["target"] = DISK_TMPL.format(name, '"' + i.name + '"')
                p["targets"].append(tmp)
            elif p["title"] == "Network usage":
                tmp = {}
                tmp["target"] = NET_TMPL.format(name, '"' + i.name + '"')
                p["targets"].append(tmp)
            elif p["title"] == "CPU":
                tmp = {}
                tmp["target"] = CPU_TMPL.format(name, '"' + i.name + '"')
                p["targets"].append(tmp)

    for p in row_template["panels"]:
        p["title"] = tenant["name"] + " - " + p["title"]
    return row_template

conf = pyostack.init("config.ini")
identity = pyostack.Identity(conf)
compute = pyostack.Compute(conf)
tenants = identity.list_tenants()
servers = compute.server_list(all_tenants=True)

for t in tenants:
    t_i = [x for x in servers if x.tenant_id == t["id"]]
    if len(t_i) == 0:
        continue
    r = new_row(t, t_i)
    template["rows"].append(r)

json.dump(template, open("/var/www/grafana/src/app/dashboards/tenants.json", "w"))
