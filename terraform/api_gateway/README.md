Example sandbox.tfvars file:

```
aws_account_id        = "<your_account_id>"
aws_access_key_id     = "<your_access_key_id>"
aws_secret_access_key = "<your_secret_access_key>"
domain                = "sdp-sandbox"
cognito_user_pool_arn = "arn:aws:cognito-idp:REGION:ACCOUNT_ID:userpool/USER_POOL_ID"
lambda_function_name  = "LAMBDA_FUNCTION_NAME"
lambda_function_invoke_arn = "arn:aws:lambda:REGION:ACCOUNT_ID:function:LAMBDA_FUNCTION_NAME"
```