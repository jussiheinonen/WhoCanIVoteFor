## Troubleshooting

### Deploys

You can monitor a deploy via the [CircleCI dashboard](https://app.circleci.com/pipelines/github/DemocracyClub/WhoCanIVoteFor). 

If a `sam_deploy` job of a build fails, the deploy will not proceed to the `code_deploy` job. An error at this stage is likely to be the result of an error in a change to the sam-template.yaml. In this circumstance, the cloudformation stack will rollback to its previous state and the original EC2 instance will remain with the code from the last successfully completed build, and so no downtime should occur.

If a `code_deploy` job fails, this is likely to be as a result of one of the Code Deploy hooks failing. You can find out more information about the error via the AWS console in the 'Deployments' section of CodeDeploy. In this circumstance, the Cloudformation stack will have been updated, but the original instance will remain from the last successful deploy. No downtime should occur.

In the event of a failed build, you can restart the deployment via the CircleCI job or push changes to trigger a new attempt. Concurrent deployments to the development and staging environment have to succeed before a deployment to production is triggered - this is configured via the CircleCI config file in this repo `.circleci/config.yml`.


### Logs and metrics

Instance logs and metrics are streamed to Cloudwatch, so that in the event that an instance has been terminated, the logs are still available to help with debugging. You can view them in the AWS console via Cloudwatch > Logs > Log groups. Here you will find the syslog, database replication logs, codedeploy logs, and lambda logs.

These may be of use when investigating any downtime errors such as https://github.com/DemocracyClub/WhoCanIVoteFor/issues/976