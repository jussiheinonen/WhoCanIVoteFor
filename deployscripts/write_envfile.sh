#!/usr/bin/env bash
set -xeE

source /var/www/wcivf/env/bin/activate
python /var/www/wcivf/code/deployscripts/write_envfile.py
