#!/usr/bin/python

import json
import pyostack
from pprint import pprint

DISK_TMPL = "alias(sumSeries({}.virt-{}.disk_octets-*.*),{})"
NET_TMPL = "alias(sumSeries({}.virt-{}.if_octets-*.*),{})"
CPU_TMPL = "alias(scale({}.virt-{}.virt_cpu_total,1e-9),{})"
MEM_TMPL = "alias(sumSeries({}.virt-{}.memory-unused), {})"

template = json.load(open("/home/venzano/vcs/openstack_docs/scripts/dashboard_generator/tenant_template.json"))

plot_id = 4

def per_tenant_sums(tenants, servers):
    global plot_id
    row_template = json.load(open("/home/venzano/vcs/openstack_docs/scripts/dashboard_generator/tenant_row_template.json"))
    row_template["title"] = "Per tenant summaries"

    DISK_BASE = '{}.{}.disk_octets-*.*'
    CPU_BASE = '{}.{}.virt_cpu_total'
    NET_BASE = '{}.{}.if_octets-*.*'
    MEM_BASE = '{}.{}.memory-unused'

    for p in row_template["panels"]:
        if p["title"] == "Disk throughput":
            for t in tenants:
                s = ''
                t_i = [x for x in servers if x.tenant_id == t["id"]]
                if len(t_i) == 0:
                    continue
                for i in t_i:
                    name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"] + "_" + i.__dict__["OS-EXT-SRV-ATTR:host"]
                    inst_name = "virt-" + i.__dict__["OS-EXT-SRV-ATTR:instance_name"]
                    s += DISK_BASE.format(name, inst_name) + ','
                s = s[:-1] # last comma
                target = "alias(sumSeries(" + s + '),"' + t["name"] + '")'
                p["targets"].append({"target": target})
                p["id"] = plot_id
                plot_id += 1
        elif p["title"] == "Used VCores":
            for t in tenants:
                s = ''
                t_i = [x for x in servers if x.tenant_id == t["id"]]
                if len(t_i) == 0:
                    continue
                for i in t_i:
                    name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"] + "_" + i.__dict__["OS-EXT-SRV-ATTR:host"]
                    inst_name = "virt-" + i.__dict__["OS-EXT-SRV-ATTR:instance_name"]
                    s += CPU_BASE.format(name, inst_name) + ','
                s = s[:-1] # last comma
                target = "alias(scale(sumSeries(" + s + '),1e-9),"' + t["name"] + '")'
                p["targets"].append({"target": target})
                p["id"] = plot_id
                plot_id += 1
        elif p["title"] == "Network traffic":
            for t in tenants:
                s = ''
                t_i = [x for x in servers if x.tenant_id == t["id"]]
                if len(t_i) == 0:
                    continue
                for i in t_i:
                    name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"] + "_" + i.__dict__["OS-EXT-SRV-ATTR:host"]
                    inst_name = "virt-" + i.__dict__["OS-EXT-SRV-ATTR:instance_name"]
                    s += NET_BASE.format(name, inst_name) + ','
                s = s[:-1] # last comma
                target = "alias(sumSeries(" + s + '),"' + t["name"] + '")'
                p["targets"].append({"target": target})
                p["id"] = plot_id
                plot_id += 1
        elif p["title"] == "Free memory":
            for t in tenants:
                s = ''
                t_i = [x for x in servers if x.tenant_id == t["id"]]
                if len(t_i) == 0:
                    continue
                for i in t_i:
                    name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"] + "_" + i.__dict__["OS-EXT-SRV-ATTR:host"]
                    inst_name = "virt-" + i.__dict__["OS-EXT-SRV-ATTR:instance_name"]
                    s += MEM_BASE.format(name, inst_name) + ','
                s = s[:-1] # last comma
                target = "alias(sumSeries(" + s + '),"' + t["name"] + '")'
                p["targets"].append({"target": target})
                p["id"] = plot_id
                plot_id += 1



    return row_template

def new_row(tenant, servers):
    global plot_id
    row_template = json.load(open("tenant_row_template.json"))
    row_template["title"] = tenant["name"]

    # Detailed rows
    for i in servers:
        name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"] + "_" + i.__dict__["OS-EXT-SRV-ATTR:host"]
        inst_name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"]

#        try:
#            cpu_count = compute.get_vcpu_count(i)
#        except:
#            print("Warning, instance {} has an unknown flavor".format(i.name))
#            cpu_count = 1
        for p in row_template["panels"]:
            if p["title"] == "Disk throughput":
                tmp = {}
                tmp["target"] = DISK_TMPL.format(name, inst_name, '"' + i.name + '"')
                p["targets"].append(tmp)
                p["id"] = plot_id
                plot_id += 1
            elif p["title"] == "Network traffic":
                tmp = {}
                tmp["target"] = NET_TMPL.format(name, inst_name, '"' + i.name + '"')
                p["targets"].append(tmp)
                p["id"] = plot_id
                plot_id += 1
            elif p["title"] == "Used VCores":
                tmp = {}
                tmp["target"] = CPU_TMPL.format(name, inst_name, '"' + i.name + '"')
                p["targets"].append(tmp)
                p["id"] = plot_id
                plot_id += 1
            elif p["title"] == "Free memory":
                tmp = {}
                tmp["target"] = MEM_TMPL.format(name, inst_name, '"' + i.name + '"')
                p["targets"].append(tmp)
                p["id"] = plot_id
                plot_id += 1

    return row_template

conf = pyostack.init("config.ini")
identity = pyostack.Identity(conf)
compute = pyostack.Compute(conf)
tenants = identity.list_tenants()
servers = compute.server_list(all_tenants=True)

# A row with global summries is included in the template

# A row with per tenant sums
r = per_tenant_sums(tenants, servers)
template["rows"].append(r)

for t in tenants:
    t_i = [x for x in servers if x.tenant_id == t["id"]]
    if len(t_i) == 0:
        continue
    r = new_row(t, t_i)
    template["rows"].append(r)

json.dump(template, open("/mnt/cephfs/dashboards/tenants.json", "w"))
