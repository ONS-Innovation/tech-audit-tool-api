### Example dev.tfvars file:

Mandatory variables:
```
aws_account_id        = "<ACCOUNT_ID>"
aws_access_key_id     = "<ACCESS_KEY_ID>"
aws_secret_access_key = "<SECRET_ACCESS_KEY>"
domain                = "sdp-dev"
```

Mandatory variables that can be set later:
```
cognito_pool_id       = "<COGNITO_POOL_ID>"
cognito_client_id     = "<COGNITO_CLIENT_ID>"
cognito_secret_id     = "<COGNITO_SECRET_ID>"
redirect_uri          = "<REDIRECT_URI>"
```