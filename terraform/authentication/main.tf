terraform {
  backend "s3" {
    # Backend is selected using terraform init -backend-config=path/to/backend-<env>.tfbackend
    # bucket         = "sdp-dev-tf-state"
    # key            = "sdp-sandbox-ecs-tech-audit-tool-api-auth/terraform.tfstate"
    # region         = "eu-west-2"
    # dynamodb_table = "terraform-state-lock"
  }

}

module "cognito" {
  source = "git::https://github.com/ONS-Innovation/keh-cognito-auth-tf-module.git"

  domain                     = var.domain
  service_subdomain          = var.service_subdomain
  domain_extension           = var.domain_extension
  region                     = var.region
  project_tag                = var.project_tag
  team_owner_tag             = var.team_owner_tag
  business_owner_tag         = var.business_owner_tag
  service_title              = var.service_title
  token_validity_values     = var.token_validity_values
  token_validity_units      = var.token_validity_units
  callback_urls             = var.callback_urls
}
