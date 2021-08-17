import os
import boto3
import time

COMMIT_SHA = os.environ.get("COMMIT_SHA")

client = boto3.client("codedeploy")


def create_deployment():
    """
    Create a new deployment and return deploy ID
    """
    deployment = client.create_deployment(
        applicationName="WCIVFCodeDeploy",
        deploymentGroupName="WCIVF-BlueGreen-DepGrp-asg",
        revision={
            "revisionType": "GitHub",
            "gitHubLocation": {
                "repository": "DemocracyClub/WhoCanIVoteFor",
                "commitId": COMMIT_SHA,
            },
        },
    )
    return deployment["deploymentId"]


def check_deployment(deployment_id):
    """
    Checks the status of the deploy every 5 seconds,
    returns a success or error code
    """
    deployment = client.get_deployment(deploymentId=deployment_id)[
        "deploymentInfo"
    ]

    if deployment["status"] == "Succeeded":
        print("SUCCESS")
        exit(0)

    if deployment["status"] == "Failed":
        print("FAIL")
        # could delete the failed ASG before exit?
        exit(1)

    print(deployment["status"])
    time.sleep(10)
    check_deployment(deployment_id=deployment_id)


deployment_id = create_deployment()
check_deployment(deployment_id=deployment_id)
