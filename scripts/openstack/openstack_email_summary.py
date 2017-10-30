#!/usr/bin/python
import math
from email.mime.text import MIMEText
import smtplib
import subprocess
import sys
from pprint import pprint

vms_cmd = ['nova', 'list', '--all-tenants', '--fields', 'name,flavor,user_id']
users_cmd = ['keystone', 'user-list']
flavors_cmd = ['nova', 'flavor-list', '--all']

print("Getting list of VMs...")
vms_str = subprocess.check_output(vms_cmd)
print("Getting list of users...")
users_str = subprocess.check_output(users_cmd)
print("Getting list of flavors...")
flavor_str = subprocess.check_output(flavors_cmd)

print("Parsing...")

vms = vms_str.split("\n")[3:-2]
vms = [ x.split("|") for x in vms ]
tmp = {}
for vm in vms:
    id = vm[1].strip()
    name = vm[2].strip()
    flavor = vm[3].strip()
    user = vm[4].strip()
    if user in tmp:
        tmp[user].append([id, name, flavor])
    else:
        tmp[user] = [[id, name, flavor]]
vms = tmp

users = users_str.split("\n")[3:-2]
users = [ x.split("|") for x in users ]
tmp = {}
for user in users:
    id = user[1].strip()
    name = user[2].strip()
    email = user[4].strip()
    tmp[id] = (name, email)
users = tmp

flavors = flavor_str.split("\n")[3:-2]
flavors = [ x.split("|") for x in flavors ]
tmp = {}
for f in flavors:
    id = f[1].strip()
    name = f[2].strip()
    ram = int(f[3].strip())
    disk = int(f[4].strip()) + int(f[5].strip())
    cores = int(f[7].strip())
    tmp[id] = (ram, disk, cores, name)
flavors = tmp

#pprint(vms)
#pprint(users)
#pprint(flavors)

out = {}
for user_id in vms:
    total_ram = 0
    total_disk = 0
    total_cores = 0
    vm_names = []
    for vm in vms[user_id]:
        vm_names.append(vm[1])
        try:
            total_ram += flavors[vm[2]][0]
        except KeyError:
            print("Cannot find flavor %s for vm %s (%s)" % (vm[2], vm[1], vm[0]))
            continue
        total_disk += flavors[vm[2]][1]
        total_cores += flavors[vm[2]][2]
    out[user_id] = {'vm_names': vm_names, 'name': users[user_id][0], 'email': users[user_id][1], 'total_ram': total_ram * 1024 * 1024, 'total_disk': total_disk * 1024 * 1024 * 1024, 'total_cores': total_cores}

#pprint(out)

def format_bytes(bytes):
    if bytes == 0:
        return '0 Byte'
    k = 1000
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    i = math.floor(math.log(bytes) / math.log(k))
    val = bytes / math.pow(k, i);
    return ("%.1f" % val) + ' ' + sizes[int(i)]

def send_email(address, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'noreply@bigfoot.eurecom.fr'
    msg['To'] = address
    s = smtplib.SMTP('smtp.gmail.com')
    s.ehlo()
    s.starttls()
    s.login('bigfoot.data@gmail.com', 'Daicu2Ze')
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

print("Sending emails")

for user_id in out:
    subject = "Bigfoot platform resource usage weekly report"
    body = """Resource usage summary for virtual machines running on the Bigfoot platform for user {name}.
    
    VMs: {vm_names}

    For a total of {ram} RAM, {disk} disk and {cores} cores.

    Please be friendly to your fellow users and terminate all the VMs you no longer need."""

    t = out[user_id]
    t['count'] = len(t['vm_names'])
    t['vm_names'] = ", ".join(t['vm_names'])
    t['ram'] = format_bytes(t['total_ram'])
    t['disk'] = format_bytes(t['total_disk'])
    t['cores'] = t['total_cores']

    body = body.format(**t)

#    if t['email'] == "daniele.venzano@eurecom.fr":
    if len(sys.argv) == 1:
        send_email(t['email'], subject, body)

body = """Bigfoot platform summary usage.

Name            VM #   Cores  RAM       Disk
"""
for user_id in out:
    s = "{name:15} {count:<6} {cores:<6} {ram:<9} {disk:<9}\n".format(**out[user_id])
    body += s

subject = "Bigfoot platform resource usage general overview"

if len(sys.argv) == 1:
    send_email("daniele.venzano@eurecom.fr", subject, body)
    send_email("pietro.michiardi@eurecom.fr", subject, body)
else:
    print(body)

