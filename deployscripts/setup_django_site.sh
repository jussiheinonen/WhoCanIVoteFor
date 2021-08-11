#!/usr/bin/env bash

# not sure this is necessary anymore with DB replication?
source /var/www/wcivf/env/bin/activate
python /var/www/wcivf/code/manage.py setup_django_site
