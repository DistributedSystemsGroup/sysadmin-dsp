#!/bin/bash
zcat /var/log/apache2/access.log*.gz | goaccess /var/log/apache2/access.log /var/log/apache2/access.log.1 -o /var/www/html/goaccess/index.html --no-progress -

