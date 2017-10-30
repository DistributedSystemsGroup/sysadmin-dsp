#!/bin/sh

NAMES=$(ls -1d /mnt/logs/collectd/* | grep -v -E 'instance-[0-9]+|bigfoot.*\.eurecom\.fr')
REPORTS=$(cd /var/www/reports;ls -1d */*)

DATE=$(date)
cat >/var/www/index.html <<EOF
<html>
<head><title>Bigfoot monitoring resources</title></head>
<body>
<h1>Bigfoot monitoring resources</h1>
<p>This page contains links to all monitoring resources available on Bigfoot.</p>
<h2>Event monitoring</h2>
<ul>
	<li><a href="http://bigfoot-m1.eurecom.fr/nagios3/">Nagios</a></li>
</ul>

<h2>Reports</h2>
<ul>
EOF
for r in $REPORTS; do
	echo "<li><a href=\"http://192.168.104.241/reports/$r\">$r</a></li>" >> /var/www/index.html
done
cat >>/var/www/index.html <<EOF
</ul>

<h2>Dashboards</h2>
<ul>
	<li><a href="http://192.168.104.241/kibana/index.html#/dashboard/elasticsearch/Bigfoot%20errors">Kibana (logs)</a></li>
	<li><a href="http://192.168.104.241/">Graphite</a></li>
	<li><a href="http://192.168.104.241/grafana/#/dashboard/file/bigfoot_overview.json">Bigfoot overview</a></li>
	<li><a href="http://192.168.104.241/grafana/#/dashboard/file/bigfoot_systems.json">Bigfoot systems</a></li>
	<li><a href="http://192.168.104.241/grafana/#/dashboard/file/bigfoot_network.json">Bigfoot network</a></li>
	<li><a href="http://192.168.104.241/grafana/#/dashboard/file/bigfoot_server_details.json">Bigfoot server details</a></li>
	<li><a href="http://192.168.104.241/grafana/#/dashboard/file/bigfoot_compute_details.json">Bigfoot compute details</a></li>
</ul>

<h3>Automatically generated dashboards (hourly)</h3>
<ul>
	<li><a href="http://192.168.104.241/grafana/#/dashboard/file/tenants.json">All projects overview (tenants)</a></li>
EOF

rm -f /var/www/grafana/src/app/dashboards/gen_*.json
for n in $NAMES; do
	n=$(basename $n)
	cltd_n=$(echo $n | tr . _)
	fname_n=$(echo $cltd_n | tr - _)
	cat template.json | sed -e "s/XXX/$cltd_n/g" > /var/www/grafana/src/app/dashboards/gen_$fname_n.json
	echo "<li>VM: <a href=\"http://192.168.104.241/grafana/#/dashboard/file/gen_$fname_n.json\">$n</a></li>" >> /var/www/index.html
done

cat >>/var/www/index.html <<EOF
</ul>

<h5>Last generation: $DATE</h5>
</body>
</html>
EOF

./per_tenant.py

