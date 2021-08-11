#!/usr/bin/env bash

source /var/www/wcivf/env/bin/activate
python /var/www/wcivf/code/manage.py collectstatic --noinput --clear
