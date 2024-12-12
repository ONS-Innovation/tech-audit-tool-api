variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
}

variable "service_subdomain" {
  description = "Service subdomain"
  type        = string
  default     = "tech-audit-tool-api"
}

variable "domain" {
  description = "Domain"
  type        = string
  default     = "sdp-dev"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "project_tag" {
  description = "Project"
  type        = string
  default     = "TAT"
}

variable "team_owner_tag" {
  description = "Team Owner"
  type        = string
  default     = "Knowledge Exchange Hub"
}

variable "business_owner_tag" {
  description = "Business Owner"
  type        = string
  default     = "DST"
}

variable "cognito_pool_id" {
  description = "Cognito User Pool ID"
  type        = string
  default     = "TO_BE_SET"
}

variable "cognito_client_id" {
  description = "Cognito Client ID"
  type        = string
  default     = "TO_BE_SET"
}

variable "cognito_client_secret" {
  description = "Cognito Client Secret ID"
  type        = string
  default     = "TO_BE_SET"
  sensitive   = true
}

variable "redirect_uri" {
  description = "Redirect URI for Cognito"
  type        = string
  default     = "TO_BE_SET"
}
