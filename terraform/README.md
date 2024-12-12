# Terraform Infrastructure Management

This repository contains Terraform configurations for managing various AWS services including storage, Lambda functions, authentication, API Gateway and CloudWatch.

## Getting Started

### Prerequisites
- Terraform installed (version >= 1.0.0)
- AWS credentials configured
- Appropriate `.tfvars` and `.tfbackend` files in the `env/<environment>/` directory.

### Directory Structure
The infrastructure is organized into separate services in order of application:
- `terraform/secrets/` - Secrets Manager
- `terraform/storage/` - S3 buckets and DynamoDB tables
- `terraform/lambda/` - Lambda functions
- `terraform/authentication/` - Cognito user pools
- `terraform/api_gateway/` - API Gateway configuration

### Common Commands

```bash
cd terraform/<service> 

terraform init -backend-config=env/dev/backend-dev.tfbackend -reconfigure

terraform refresh -var-file=env/dev/dev.tfvars

terraform validate

terraform plan -var-file=env/dev/dev.tfvars

terraform apply -var-file=env/dev/dev.tfvars
```

## Deploying the Infrastructure

For more info on the terraform script, see the [Documentation](https://ons-innovation.github.io/keh-tech-audit-tool-api/infrastructure/#aws-resources) in the root directory.

There are 5 AWS resources that are created by the terraform script:

- Secrets Manager (Secrets)
- S3 Bucket (Storage)
- Cognito User Pool (Authentication)
- Lambda Function (Lambda)
- API Gateway (api_gateway)

Go through the list and deploy each resource one by one.

For each resource, you will need to set the domain and service_subdomain variables in the tfvars file.

### 1. ECR Repository
Make sure you have an ECR repository created in the AWS account. This will be used in the S3 bucket and Lambda function.

### 2. Secrets Manager
Run like normal. Leave the cognito_pool_id, cognito_client_id, cognito_client_secret, and redirect_uri variables blank.

### 3. S3 Bucket
Set the ecr_repository_name variable in the tfvars file. Then run the terraform script.

### 4. Cognito User Pool
Run like normal.

### 5. Lambda Function
The tech audit S3 bucket and the secrets manager secret are created by the terraform script. The aws cognito token url is set by the terraform script. Then run the terraform script for the lambda function and this data is set in the lambda function.

### 6. API Gateway
Run like normal. Note down the URLs in the outputs.

### 7. Secrets Manager Re-application
Go back to the Secrets Manager resource and set the cognito_pool_id, cognito_client_id, cognito_client_secret, and redirect_uri variables.

Finished.
