terraform {
  backend "s3" {
    # Backend is selected using terraform init -backend-config=path/to/backend-<env>.tfbackend
    # bucket         = "sdp-dev-tf-state"
    # key            = "sdp-dev-ecs-tech-audit-tool-api-lambda/terraform.tfstate"
    # region         = "eu-west-2"
    # dynamodb_table = "terraform-state-lock"
  }
}

resource "aws_secretsmanager_secret" "cognito_secrets" {
  name = "${var.domain}-${var.service_subdomain}/secrets"
  
  tags = {
    Environment = var.domain
    Service     = var.service_subdomain
  }
}

resource "aws_secretsmanager_secret_version" "cognito_secrets_version" {
  secret_id = aws_secretsmanager_secret.cognito_secrets.id
  
  secret_string = jsonencode({
    COGNITO_POOL_ID     = var.cognito_pool_id
    COGNITO_CLIENT_ID   = var.cognito_client_id
    COGNITO_CLIENT_SECRET   = var.cognito_client_secret
    REDIRECT_URI        = var.redirect_uri
  })
}
