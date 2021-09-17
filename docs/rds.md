## RDS logical replication settings


Before creating an RDS instance, create a custom Parameter Group with the name "Logical".

- In the AWS console, go to RDS.
- Select Parameter Groups from the left habd side menu, then create.
- Select the correct posgres version - probably the latest available.
- Give it the name of "Logical" and description of "Logical replication settings". Click create.

Now click on the 'Logical' parameter group you just created, then click 'Modify" and update the following parameters:

- rds.logical: 1
- shared_preload_libraries: pglogical
- Click 'Continue', then 'Apply changes'

Now when you craete your RDS instance, apply this parameter group to your RDS instance under the Database Options section.