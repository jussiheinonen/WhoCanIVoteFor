## SSL Certificate

You will need to use the AWS Console to provision an SSL certificate to be used in the deployment. Follow the steps below to create the SSL certificate.

- In the AWS console, go to Certificate Manager
- Choose "Request a Certificate" and select public certificate
- Add the domain and optionally a wildcard for the sub domain e.g. ‘wcivf.club’ and ‘* wcivf.club’
- Choose DNS validation, add any tags, and confirm
- On the review screen, open the domain and click the button “Create record in Route 53”. Repeat for any additional domains you added. This will create DNS records in route 53 to validate the certificate.
- The ARN of the created certificate is then used when deploying to a new environment - this is outlined elsewhere in the documentation.
