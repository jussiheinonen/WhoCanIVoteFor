#!/usr/bin/env bash
set -xeE

# could drop db and run DB replication script?
source /var/www/wcivf/env/bin/activate
python /var/www/wcivf/code/manage.py migrate --noinput
