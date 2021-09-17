# Automated deployments from CircleCI in a new environment

This process has been tested in the `development` and `staging` environments.

## Prerequisites

Before following these instructions you should have:

- Created an S3 bucket as per the [S3 documentation](/docs/s3.md)
- Created the required IAM entities as per the [IAM documentation](/docs/iam.md) - although you may want to wait until after creating the "Context" before completing the final step to create the the CircleCI user. This is because you will need to use the AWS access and store them in .
- Created the relevant secrets in AWS Parameter Store as per the [Parameter Store documentation](/docs/parameterstore.md)
- Created an SSL certificate as per the [SSL documentation](/docs/sslcertificate.md)

## In CircleCI web UI

You will need to create a new CircleCI deployment "Context". This is done in the Circle CI Web UI, under Organization Settings < Contexts. 

A good initial topology is one Context per AWS account. The suggested naming convention for this project is `deployment-ENVIRONMENT-PROJECTNAME` e.g. `deployment-production-wcivf`.

You will need to set a number of variables in the context so that these are used in the lambda function deploymenet. The variables to set are:

- `AWS_ACCESS_KEY_ID` - this the access key for the CircleCI user
- `AWS_SECRET_ACCESS_KEY` - the secret accrss key of the CircleCI user
- `AWS_DEFAULT_REGION` - this should generally be 'eu-west-2'
- `RDS_DB_NAME` - the name of the database your lambda function will connect to
- `RDS_DB_PASSWORD` - the password for the database your lambda function will connect to
- `RDS_HOST` - the rds endpoint value
- `SECRET_KEY` - a long random string. [A handy way of using Django to generate one can be found in this blog post](https://humberto.io/blog/tldr-generate-django-secret-key/).
- `SENTRY_DSN` - from the project in Sentry

## In the WCIVF codebase

### In `.circleci/config.yml`

Clone the staging or production `sam_deploy` workflow job and alter the keys as appropriate. You'll definitely need to amend `name` and `dc-environment`.

Change `context` to the name of the new Context you created above, if you created one. If you're deploying into an already-deployed-into-by-Circle AWS account, reuse the existing Context.

You may want to change the `requires` prerequisites to change this deployment's prerequisites.

### In `samconfig.toml`

Copy one of the existing environment configurations, changing them slightly to use the new environment name and values for each setting.

NB the `s3_bucket` setting is *per-AWS account*, so you should make sure it matches the name of the already-created (as per the [AWS account setup document](docs/s3.md#)) deployment-assets bucket in the AWS account.

### AMI access

One final step to check before attempting to deploy is that the account you are deploying to (development/staging/production) has access to the AMI image that is specified as the `ImageId` for the `WCIVFLaunchTemplate` in `sam-template.yml`. To check this, in the account that the image was build, go to the AWS Console:

- Got to EC2
- Under 'Images' select 'AMIs'
- Select the image with the corresponding AMI ID, click the 'Actions' button, and select 'Modify Image Permissions'
- Check that the AWS account ID that you are deploying to is listed. If it is missing, enter the ID and click 'Add Permission'

### Create the deployment

Deployments are triggered by CircleCI. Have a look at the `.circleci/config.yml` for further details about jobs and workflows, as well as which circumstances a deployment is triggered under the `requires` and `filters` section of a job under the workflows section. 

When you are ready to start a deployment, commit and push all the changes you've made. Create a pull request and merge when changes have been reviewed and you are happy with them. Assuming the conditions for a deploy workflow have been met, CI will deploy your new enviroment. 

NB If this is the first time deployment to a new environment, it is likely that the workflow will fail on the first attempt at the code deploy step. If this occurs, you can go to CodeDeploy in the AWS Console to view the errors. It is very likely will be "The deployment failed because no instances were found in your blue fleet." This is because as part of the initial deployment, a new "default" Auto Scaling Group is created. This will in turn provision the initial instance(s). However, before enough time has passed for the instance to complete initialisation, CodeDeploy has attempted a deployment, which fails because it expects to find some existing instances already running. If you wait a short while for the instances to be ready, then rerun this step in CircleCI it should succeed.

If the CircleCI job times out, check the CloudFormation Stack's progress in [the AWS web UI](https://console.aws.amazon.com/cloudformation) before re-running the job. It may be that the Stack is still being created, and runs to the end successfully, in which case a job rerun will also succeed.

However, if the Stack has failed to create and is in a "CREATE_FAILED" state then you'll have to manually delete the Stack in the UI before rerunning the CircleCI job. This is an intentional CloudFormation feature that allows you to view the underlying reason that Stack creation failed, and fix it, before deleting the Stack and losing that failure-related insight. See [the AWS docs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-describing-stacks.html#w2ab1c23c15c17c11) for more information on potential failure causes.

## Debugging CI failures

A common cause of problems is environment variables. You might have entered them subtly wrongly, or some part of the CI process might be distorting or passing them around in a modified form - but this is most likely to be the deployment scripts, not behind-the-scenes CircleCI breakage.

Here are some techniques for figuring out if you've encountered any of these kinds of problems.

### CircleCI masks environment variables' values

Once you've inserted an environment variable into CircleCI's per-project or per-Context settings, it won't allow that string to be echoed during test/build/deploy/etc workflows. You can think of the CircleCI product as wrapping the entire output of all executed jobs and workflows in a big `sed` wrapper that looks for the variables' values and swaps them out for asterisks. They describe the feature [on their blog](https://circleci.com/blog/keep-environment-variables-private-with-secret-masking/), and mention a few "gotchas":

- Secrets below 4 characters will not be masked.
- Secrets with the values true, TRUE, false, FALSE will not be masked.
- This does not prevent secrets from being displayed when you SSH into a build.

Presumably the 4-character limit is because, otherwise, if one created a variable with the value "a", then the entire CI output would become increasingly useless, being littered with single-character redactions wherever an "a" was output!

One way to use this feature for debugging is to look at the outputs of your jobs where you might expect non-secrets that are stored as environment variables (e.g. FQDNs, debug settings, etc) and are echoed during deployment. If the values are **not** masked, then your expectation of what's in the environment variable might not match what's actually there.

### Deployment jobs show you their deployment variables

In this project's CircleCI configuration file, a safe way of printing environment variables is using `printenv`. Currently this is not being used in this project, but see the [Aggregator API Docs](https://github.com/DemocracyClub/aggregator-api/blob/master/docs/new-ci-deployment.md#deployment-jobs-show-you-their-deployment-variables) for further information and examples of using this to help with debugging