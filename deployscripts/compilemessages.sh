#!/usr/bin/env bash
set -xeE

source /var/www/wcivf/env/bin/activate
cd /var/www/wcivf/code/
python manage.py compilemessages
