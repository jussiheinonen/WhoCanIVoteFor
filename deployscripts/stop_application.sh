#!/usr/bin/env bash
set -xeE

service wcivf_gunicorn stop
service wcivf_db_replication stop

# delete all code including hidden files
rm -rf /var/www/wcivf/code/* /var/www/wcivf/code/.* 2> /dev/null || true
