import os

from .base import *  # noqa
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "wcivf",
        "USER": "wcivf",
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[AwsLambdaIntegration(timeout_warning=True)],
    environment="lambda",
)
