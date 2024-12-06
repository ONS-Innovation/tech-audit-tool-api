# Terraform Infrastructure Management

This repository contains Terraform configurations for managing various AWS services including storage, Lambda functions, authentication, API Gateway and CloudWatch.

## Getting Started

### Prerequisites
- Terraform installed (version >= 1.0.0)
- AWS credentials configured
- Appropriate `.tfvars` and `.tfbackend` files in the `env/sandbox/` directory

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

### Authentication

You must create the Cognito user pool (authentication) then create the API Gateway (api_gateway).

Once API Gateway is created, you can configure the callback URLs in the Cognito user pool to point to the API Gateway endpoint.

#### Secrets and Environments

The app in aws_lambda_script uses environment variables set in the lambda environment variables. These variables point to the secrets in Secrets Manager and the S3 bucket.
