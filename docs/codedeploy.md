# CodeDeploy

We use CodeDeploy to automate deployments. In its current configuration, it will:
- Create new EC2 instances and pull the latest code changes to them from our GitHub repository
- Run a series of installation and startup scripts on the instance as defined in [appspec.yml](/appspec.yml)
- Validate the instances are healthy and allow traffic to them
- Tear down old instances

[See the AWS docs for more information about the lifecycle event hooks and the appspec.yml configuration.](https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file-structure-hooks.html#appspec-hooks-server)

## Initial setup
Our CodeDeploy Application `WCIVFCodeDeployApp` is defined in [`sam-template.yaml`](/sam-template.yaml). This is essentially just a container, that everything else in code deploy hangs off, and will be created by CloudFormation as part of the `sam_deploy` jobs in [`.circleci/config.yml`](/.circleci/config.yml).

There is a python script to [create a deployment group](/deployscripts/create_deployment_group.py) on the initial deploy. On subsequent deploys this will check the deployment group still exists but otherwise do nothing, as we only require one persistent deployment group.

There is also a python script to [create a new deployment](/deployscripts/create_deployment.py), which creates a new CodeDeploy deployment with a unique ID for each deploy job triggered by our [CircleCI `code_deploy` jobs](/.circleci/config.yml). Both these scripts use `boto3` and should not need amending currently, but take a look at the scripts to familiarize yourself with the steps taken.

However, before the first deploy you must connect CodeDeploy with the github repository, which is done via the AWS console. [See the AWS documentation for full steps to take](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployments-create-cli-github.html). This is already configured for each WCIVF environment but would need setting up if initialising a new environment or project.

## Deployment options
We have configured CodeDeploy to use the [blue/green](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-bluegreen.html) deployment type, with the default AllAtOnce deployment configuration. This means that for each deploy, new instances are initialized to pull the latest code from github, and after succesfully completing startup tasks, are registered with our load balancer to serve traffic. The final step it to block traffic from the old instances and terminate them.

The alternative is to use the 'in-place' deployment type, which does not create new instances but updates the existing ones. However with a single instance, this will result in downtime as the instance needs to be stopped so that the latest code can be pulled and the startup jobs are run. If using more than one instance, then there are alternative [deployment configurations](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html) such as `OneAtATime` that would allow us to avoid downtime between deploys.

## Troubleshooting/known bugs
- If a deployment fails for some reason, the CircleCI job should catch this and fail. To get details of the failure reason log in to the AWS console and click through CodeDeploy > Deployments > Deployment ID. From here you can see at which stage the deployment failed, and potentially which startup script caused the failure.
- One thing to be aware of is that CodeDeploy will report a deployment as "Successful" if just one instance is successfully deployed. From the docs:
> _The status of the overall deployment is displayed as Failed if the application revision is not deployed to any of the instances. Using an example of nine instances, CodeDeployDefault.AllAtOnce attempts to deploy to all nine instances at once. The overall deployment succeeds if deployment to even a single instance is successful. It fails only if deployments to all nine instances fail._
- This is of particular relevance when a deployment increases/decreases the number of EC2 instance, as it can mean that when viewing a deployment via the CircleCI workflow it appears as successfully completed, but unbeknownst to you not all instances were deployed. Therefore, when deploying changes that increase or decrease the number of instances it is recommended that you check progress via the "deployments" section of CodeDeploy in the AWS console.
