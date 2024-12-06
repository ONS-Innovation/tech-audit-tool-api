# Deployment Guide

This project has no CI/CD pipeline. The API is deployed manually.

Make sure to create an ECR repository before terraforming the API.

You can find more information on creating an ECR repository [here](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html).

Note down the ECR repository URI as you will need it for the Terraform code and pushing the Docker image.

Your URI should be in the format: `<aws_account_id>.dkr.ecr.<aws_region>.amazonaws.com/<repository_name>`.

For example: `999999999999.dkr.ecr.eu-west-2.amazonaws.com/tech-audit-tool-api`.

### Containerising the API

Change directory into the `aws_lambda_script` directory:

```bash
cd aws_lambda_script
```

Make sure to version your container images, using this format: `v<major>.<minor>.<patch>`.

Build the Docker image with ECR repository URI as the name. 

```bash
docker build -t <ecr_uri>:<version_tag> .
```

Push the Docker image to the ECR repository:

```bash
docker push <ecr_uri>:<version_tag>
```

You can now find that image with that version tag in the ECR repository.

Edit this URL with your ECR repository URI and region details to visit the repository (make sure you're logged in):

```
https://<region>.console.aws.amazon.com/ecr/repositories/private/<aws_account_id>/<repository_name>
```
