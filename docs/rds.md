## RDS logical replication settings

When creating an RDS instance, create a custom Parameter Group with the name "Logical". Updat the following parameters:

- rds.logical: 1
- shared_preload_libraries: pglogical

Apply this parameter group to your RDS instance under the Database Options, then wait for the instance to update before moving on.