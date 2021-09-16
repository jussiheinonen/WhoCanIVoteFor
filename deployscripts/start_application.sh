#!/usr/bin/env bash
set -xeE

service wcivf_db_replication start
service wcivf_gunicorn start
