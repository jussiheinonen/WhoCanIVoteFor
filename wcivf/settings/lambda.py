import os

from .base import *  # noqa


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("RDS_DB_NAME"),
        "USER": "wcivf",
        "PASSWORD": os.environ.get("RDS_DB_PASSWORD"),
        "HOST": os.environ.get("RDS_HOST"),
        "PORT": os.environ.get("RDS_DB_PORT", "5432"),
    }
}
