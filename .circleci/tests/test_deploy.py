import json
import os

import boto3
import pytest
from tomlkit.toml_file import TOMLFile


@pytest.fixture(scope="session")
def sam_cli_configuration():
    """
    Reads from the sam config file
    """
    config_file_path = "samconfig.toml"
    assert os.path.exists(config_file_path)
    config = TOMLFile(config_file_path).read()

    config_env = os.environ.get("DC_ENVIRONMENT", "development")
    assert config.get(config_env)
    return config[config_env]


@pytest.fixture(scope="session")
def deployed_cfn_stack(sam_cli_configuration):
    """
    Returns deployed cloudformation stack
    """
    deploy = sam_cli_configuration.get("deploy")
    assert deploy
    params = deploy.get("parameters")
    assert params
    stack_name = params.get("stack_name")
    assert stack_name

    # 'region' /can/ be absent from the config file, in which case it'll
    # need to be present in the env (AWS_DEFAULT_REGION) or the user's AWS config files
    stack = boto3.resource(
        "cloudformation", region_name=params.get("region")
    ).Stack(stack_name)
    assert (
        stack.stack_status
    )  # 'assert stack' doesn't actually check stack presence!
    return stack


def get_output_value(stack, output_key):
    """
    Get the value of a CloudFormation stack output
    """
    for output in stack.outputs:
        if output["OutputKey"] == output_key:
            # Cloudformation Outputs have unique per-stack names
            return output["OutputValue"]


@pytest.fixture
def lambda_function_arn(deployed_cfn_stack):
    """
    Returns the ARN for the Lamdbda function
    """
    return get_output_value(
        stack=deployed_cfn_stack, output_key="WCIVFControllerFunctionArn"
    )


def test_check_succeeds(lambda_function_arn, sam_cli_configuration):
    """
    Tests that the deployed lambda function can run djangos check
    management command
    """
    region = sam_cli_configuration["deploy"]["parameters"]["region"]
    lambda_client = boto3.client("lambda", region_name=region)
    response = lambda_client.invoke(
        FunctionName=lambda_function_arn,
        InvocationType="RequestResponse",
        Payload='{"command": "check"}',
    )
    payload = json.loads(response["Payload"].read())
    assert payload.get("errorMessage") is None
    assert payload["statusCode"] == 200


def test_makemigrations_check_succeeds(
    lambda_function_arn, sam_cli_configuration
):
    """
    Tests that the deployed lambda function can run djangos
    makemigrations --check command
    """
    region = sam_cli_configuration["deploy"]["parameters"]["region"]
    lambda_client = boto3.client("lambda", region_name=region)
    response = lambda_client.invoke(
        FunctionName=lambda_function_arn,
        InvocationType="RequestResponse",
        Payload='{"command": "makemigrations", "args": ["--check", "--no-input", "--dry-run"]}',
    )
    payload = json.loads(response["Payload"].read())
    assert payload.get("errorMessage") is None
    assert payload["statusCode"] == 200
