#!/usr/bin/env bash
set -xeE

# delete all code including hidden files
rm -rf /var/www/wcivf/code/* /var/www/wcivf/code/.* 2> /dev/null || true

