## Troubleshooting

### Deploys

You can monitor a deploy via the [CircleCI dashboard](https://app.circleci.com/pipelines/github/DemocracyClub/WhoCanIVoteFor). 

If a `sam_deploy` job of a build fails, the deploy will not proceed to the `code_deploy` job. An error at this stage is likely to be the result of an error in a change to the sam-template.yaml. In this circumstance, the cloudformation stack will rollback to its previous state and the original EC2 instance will remain with the code from the last successfully completed build, and so no downtime should occur.

If a `code_deploy` job fails, this is likely to be as a result of one of the Code Deploy hooks failing. You can find out more information about the error via the AWS console in the 'Deployments' section of CodeDeploy. In this circumstance, the Cloudformation stack will have been updated, but the original instance will remain from the last successful deploy. No downtime should occur.

In the event of a failed build, you can restart the deployment via the CircleCI job or push changes to trigger a new attempt. Concurrent deployments to the development and staging environment have to succeed before a deployment to production is triggered - this is configured via the CircleCI config file in this repo `.circleci/config.yml`.

#### Scaling

To increase the number of EC2 instances for an environment (e.g. during busy times around elections) increase the `min-size`, `max-size` and `desired-capacity` variables found in the `code_deploy` jobs in the [Circle CI config file](/.circleci/config.yml) file. These can be set for each environment (development, staging and production). You should then commit these changes, push and open a pull request as normal. After merging deployment will be triggered as normal, and the number of instances will be increased as part of the `code_deploy` job. In emergencies where waiting for a full deploy will take too long, you can also edit the auto scaling group settings directly via the AWS console. These can be found in EC2 > Auto Scaling > Auto Scaling Groups. However this is not recommended, as any subsequent merge and deploy will revert the number of instances back to what is defined in the [Circle CI config file](/.circleci/config.yml).

The settings described in the [RDS docs](/docs/s3.md) are the current active settings at time of writing. These should allow us to scale up on election day without issue, as long as the number of instances that need to connect to the RDS instance does not exceed `max_replication_slots`. To calculate the number of connections, multiply the number of active instances by 2, as each instance needs at least 1 additional slot available for temporary table synchronisation slots. Also note that as we are using blue/green deployments with code deploy, old instances are not terminated until the new ones have been deployed, so you will need to account for these instances when making your calculation.

For example, if you start with 2 active instances, these will already be taking up 4 replication slots. You should therefore not try to increase instances above 48, as these will use 96 replication slots, with the original instances taking up the remaining 4 slots during the deployment process, making a total of 100 replication slots in use during the deployment. In reality there should not be any need to scale to this many instances (2022 election day ran comfortably on 10 instances) but these notes are intended to give an explanation of the limits of scaling.

See the [RDS debugging section](/docs/rds.md#debugging) for details on how to view the current replication slots, as well as further reading about logical replication.

### Logs and metrics

Instance logs and metrics are streamed to Cloudwatch, so that in the event that an instance has been terminated, the logs are still available to help with debugging. You can view them in the AWS console via Cloudwatch > Logs > Log groups. Here you will find the syslog, database replication logs, codedeploy logs, and lambda logs.

These may be of use when investigating any downtime errors such as https://github.com/DemocracyClub/WhoCanIVoteFor/issues/976