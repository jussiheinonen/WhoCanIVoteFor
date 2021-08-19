import boto3


client = boto3.client("ssm", region_name="eu-west-2")


def get_parameter_names():
    response = client.describe_parameters()
    return [param["Name"] for param in response["Parameters"]]


def write_parameters_to_envfile():
    names = get_parameter_names()
    response = client.get_parameters(Names=names)
    with open("/var/www/wcivf/code/.env", "w") as f:
        for parameter in response["Parameters"]:
            key = parameter["Name"]
            value = parameter["Value"]
            f.write(f"{key}={value}\n")


if __name__ == "__main__":
    write_parameters_to_envfile()
