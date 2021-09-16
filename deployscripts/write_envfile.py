import boto3


client = boto3.client("ssm", region_name="eu-west-2")


def get_parameter_names():
    response = client.describe_parameters(MaxResults=50)
    return [param["Name"] for param in response["Parameters"]]


def write_parameters_to_envfile():
    names = get_parameter_names()
    with open("/var/www/wcivf/code/.env", "w") as f:
        for name in names:
            response = client.get_parameter(Name=name)
            key = response["Parameter"]["Name"]
            value = response["Parameter"]["Value"]
            f.write(f"{key}={value}\n")


if __name__ == "__main__":
    write_parameters_to_envfile()
