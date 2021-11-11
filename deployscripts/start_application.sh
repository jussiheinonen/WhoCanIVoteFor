#!/usr/bin/env bash
set -xeE

# enabling will allow the services to start if the instance reboots
systemctl enable wcivf_db_replication.service
systemctl enable wcivf_gunicorn.socket

systemctl start wcivf_db_replication.service
systemctl start wcivf_gunicorn.socket
