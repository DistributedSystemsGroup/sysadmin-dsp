#!/bin/sh

wget --quiet 'https://cloud-platform.eurecom.fr/grafana/render/dashboard-solo/db/platform-overview?refresh=1m&orgId=1&panelId=4&width=500&height=300' -O /var/www/html/dokuwiki/data/media/platform-overview.png

