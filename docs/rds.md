## RDS logical replication settings

NB The following steps are only required on the initial setup of a new AWS account, where no RDS instance has yet been created.

Before creating an RDS instance, create a custom Parameter Group with the name "Logical".

- In the AWS console, go to RDS.
- Select Parameter Groups from the left habd side menu, then create.
- Select the correct posgres version - probably the latest available.
- Give it the name of "Logical" and description of "Logical replication settings". Click create.

Now click on the 'Logical' parameter group you just created, then click 'Modify" and update the following parameters:

- rds.logical: 1
- shared_preload_libraries: pglogical
- max_wal_size: 1028
- max_slot_wal_keep_size: 5000
- max_replication_slots: 100
- max_wal_senders: 105
- Click 'Continue', then 'Apply changes'

Now when you craete your RDS instance, apply this parameter group to your RDS instance under the Database Options section.

If you have already created your RDS instance, you will need to modify it and apply the parameter group, then ensure the instance reboots. Confirm it has been applied by going to your instance, then clicking on the Configuration tab, and checking the "Parameter group" name is displayed as "in-sync". If not, modify the instance and reboot it, and check again.

### Enabling replication of the database

The "publisher" is the PostgreSQL in your RDS instance that is intended to replicate all tables of the WCIVF project database.

The "subscriber" is the read-only PostgreSQL database that exists in the EC2 instances.

In order to setup replication from a "publisher" to a "subscriber" the schemas must match.

#### Steps to take on the "publisher" database
- Login details for the RDS user are stored in the DC Bitwarden account. Ensure you are using the right user details for your environment/account.
- Connect to your RDS instance, create the database and ensure the schema and initial data have been imported e.g. using `pg_restore` with a database backup. If you are using a production backup from the old AWS account, you may need to manually drop the following tables:
    - `mentions_mention`
    - `mentions_mention_people`
    - `mentions_mention_posts`
- This is because the tables mentioned above are defunct tables that are not created or removed as part of the django `migrate` command that will take place on the "subscriber" instances, hence why they may need to be removed manually. If you inspect the "publisher" schema and these tables do not exist, then ignore this step.
- Run the following psql command:
    - `CREATE PUBLICATION alltables FOR ALL TABLES;`
- You can then disconnect from the "publisher" database

#### Steps to take on the "subscriber" database
You do not need to take any steps to setup the database subscription, as this process is managed by the `wcivf_db_replication.service` that is included in the provisioned instance AMI. If you want to see the steps taken, in the `who_deploy` repo look at the following files:
- `files/systemd/db_replication.service`
- `files/scripts/setup_db_replication.sh`
- `files/scripts/remove_db_replication.sh`

Further reading about setting up logical replication:

- https://aws.amazon.com/blogs/database/using-logical-replication-to-replicate-managed-amazon-rds-for-postgresql-and-amazon-aurora-to-self-managed-postgresql/
- https://blog.searce.com/rds-postgresql-logical-replication-copy-from-aws-rds-snapshot-6983446472a9

### Debugging

The following queries are useful for checking replication slots on a master instance. You will first need to [connect to the RDS instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToPostgreSQLInstance.html#USER_ConnectToPostgreSQLInstance.psql) and relevant WCIVF database. Required secrets can be found in the DC bitwarden account.

View all replication slots:
- `select * from pg_replication_slots;`

To drop a replication slot:
- `select pg_drop_replication_slot('slotnametodrop');`

The slotname includes the EC2 instance ID so you can identify with slot relates to which instance. If a replication slot is marked as inactive then you may want to drop it.

The AMI used is preconfigured to enable cloudwatch to capture logs related to database replication. Check the `cloudwatch.json` config file in the `who_deploy` repo to check the location of the logs on the server, and the log group and stream used by Cloudwatch. At the time of writing, you can view them in the AWS console at:

- Cloudwatch > Log groups > /db_replication/ > logs

[Pgmetrics is a useful tool for debugging an RDS instance](https://pgmetrics.io/docs/aws.html)

[Blog post related to ensuring that replication slots dont use up an instances full storage space](https://www.2ndquadrant.com/en/blog/pg13-slot-size-limit/)