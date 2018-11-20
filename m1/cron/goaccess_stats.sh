#!/bin/bash
zcat /var/log/apache2/access_traefik.log*.gz | goaccess /var/log/apache2/access_traefik.log /var/log/apache2/access_traefik.log.1 -o /var/www/html/goaccess/index.html --no-progress -

