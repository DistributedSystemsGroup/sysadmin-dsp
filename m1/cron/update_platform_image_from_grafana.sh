#!/bin/sh

wget --quiet 'http://bigfoot-m2.eurecom.fr/grafana/render/dashboard-solo/db/platform-overview?refresh=1m&orgId=1&panelId=4&width=500&height=300' -O /var/www/html/data/media/platform-overview.png

