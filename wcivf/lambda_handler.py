import json
import sentry_sdk

import django
from django.core.management import call_command


def handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    cmd = event["command"]
    args = event.get("args", [])

    sentry_sdk.set_context("event", event)

    django.setup()

    print(f"Calling {cmd} with args {args}")
    call_command(cmd, *args)

    arg_str = " ".join(args)
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"{cmd} {arg_str} completed",
            }
        ),
    }
