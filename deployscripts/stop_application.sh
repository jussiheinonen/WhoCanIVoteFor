#!/usr/bin/env bash
set -xeE

service wcivf_gunicorn stop
service wcivf_db_replication stop
