Example sandbox.tfvars file:

```
aws_account_id                    = "<your_account_id>"
aws_access_key_id                 = "<your_access_key_id>"
aws_secret_access_key             = "<your_secret_access_key>"
domain                            = "sdp-sandbox"
ecr_repository                    = "keh-tech-audit-tool-lambda-api" # ECR repository name where the lambda image is stored
tech_audit_data_bucket_name       = "keh-tech-audit-tool" # S3 bucket name where the tech audit data is stored
aws_cognito_token_url             = "https://tech-audit-tool-api-sdp-dev.auth.eu-west-2.amazoncognito.com/oauth2/token"
```
