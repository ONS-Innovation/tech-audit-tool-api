data "terraform_remote_state" "api_auth" {
  backend = "s3"
  config = {
    bucket = "${var.domain}-tf-state"
    key    = "${var.domain}-tech-audit-tool-api-auth/terraform.tfstate"
    region = "eu-west-2"
  }
}

data "terraform_remote_state" "api_lambda" {
  backend = "s3"
  config = {
    bucket = "${var.domain}-tf-state"
    key    = "${var.domain}-tech-audit-tool-api-lambda/terraform.tfstate"
    region = "eu-west-2"
  }
}