## Create a DNS record for your environment

After deploying to a new environment for the first time, you may need to add a DNS record from your domain to point at the load balancer created by cloudfront. This guide will use the example of setting up the record for a development environment using :

- In the AWS Console, go to Route 53
- Click "Hosted zones" and find the domain you will be using e.g. `wcivf.club`.
- Click "Create a record"
- If required, enter a subdomain value for the record e.g. `development.wcivf.club`
- Choose "Simple routing" then "Define simple record"
- Under "Record type", select "A record"
- Under "Value/Route traffic to" choose "Alias to Application and Classic Load Balancer"
- Under "Choose region" select your region - this should be "eu-west-2"
- Click the "Choose load balancer" box and you should see the load balancer for the environment listed e.g. `dualstack.wcivf-elb-xxxxx.eu-west-2.elb.amazonaws.com`
- Click the "Define simple record" button. You will need to wait a short time for the record to propogate before you can access the website on your specified domain
