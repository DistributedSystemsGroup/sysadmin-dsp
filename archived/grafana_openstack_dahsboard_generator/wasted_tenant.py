#!/usr/bin/python

import json
import pyostack
from pprint import pprint

template = json.load(open("/home/venzano/vcs/openstack_docs/scripts/dashboard_generator/wasted_template.json"))

plot_id = 3

ABC = "ABCDEFGHIJKLMNOPQRSTUVWYZ"

def per_tenant_sums(tenants, servers):
    global plot_id
    row_template = json.load(open("/home/venzano/vcs/openstack_docs/scripts/dashboard_generator/wasted_row_template.json"))
    row_template["title"] = "Per tenant summaries"

    CPU_BASE = '{}.{}.virt_cpu_total'
    MEM_BASE = '{}.{}.memory-unused'

    for p in row_template["panels"]:
        if p["title"] == "Unused allocated cores":
            metric_count = 1
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
                target = "alias(offset(scale(asPercent(scale(sumSeries(" + s + "), 1e-9), #" + ABC[metric_count] + "), -1), 100), \"" + t["name"] + "\")"
                p["targets"].append({"target": target, "hide": False})
                target = "m1.openstack-nova-tenant-" + t["name"] + ".gauge-limits-totalCoresUsed"
                p["targets"].append({"target": target, "hide": True})
                p["id"] = plot_id
                plot_id += 1
                metric_count += 2
        if p["title"] == "Unused allocated memory":
            metric_count = 1
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
                target = "alias(asPercent(sumSeries(" + s + "), #" + ABC[metric_count] + "), \"" + t["name"] + "\")"
                p["targets"].append({"target": target, "hide": False})
                target = "m1.openstack-nova-tenant-" + t["name"] + ".gauge-limits-totalRAMUsed"
                p["targets"].append({"target": target, "hide": True})
                p["id"] = plot_id
                plot_id += 1
                metric_count += 2

    return row_template

CPU_TMPL = "alias(offset(scale(asPercent({}.{}.virt_cpu_total, {}), -1), 100), {})"
MEM_TMPL = "alias(asPercent(sumSeries({}.{}.memory-unused), {}), {})"

def new_row(tenant, servers):
    global plot_id
    row_template = json.load(open("wasted_row_template.json"))
    row_template["title"] = tenant["name"]

#    print "Using tenant {}".format(tenant["name"])
    conf.set('environment', 'OS_TENANT_NAME', tenant["name"])
    compute = pyostack.Compute(conf)

    # Detailed rows
    metric_count = 1
    for i in servers:
        name = i.__dict__["OS-EXT-SRV-ATTR:instance_name"] + "_" + i.__dict__["OS-EXT-SRV-ATTR:host"]
        inst_name = "virt-" + i.__dict__["OS-EXT-SRV-ATTR:instance_name"]

        try:
            cpu_count = compute.get_vcpu_count(i)
        except:
            print("Warning, instance {} has an unknown flavor".format(i.name))
            cpu_count = 1

        try:
            mem_size = compute.get_mem_size(i)
        except:
            print("Warning, instance {} has an unknown flavor".format(i.name))
            mem_size = 4 * (1024*1024*1024)

        for p in row_template["panels"]:
            if p["title"] == "Unused allocated cores":
                target = CPU_TMPL.format(name, inst_name, cpu_count*1e9, '"' + i.name + '"')
                p["targets"].append({"target": target, "hide": False})
                p["id"] = plot_id
                plot_id += 1
            elif p["title"] == "Unused allocated memory":
                target = MEM_TMPL.format(name, inst_name, mem_size, '"' + i.name + '"')
                p["targets"].append({"target": target, "hide": False})
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

json.dump(template, open("/mnt/cephfs/dashboards/wasted.json", "w"))
