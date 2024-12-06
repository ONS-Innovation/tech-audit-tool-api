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

variable "ecr_repository" {
  description = "Name of the ECR repository containing the Lambda image"
  type        = string
}

variable "container_ver" {
  description = "Container tag"
  type        = string
  default     = "v0.0.2"

}

variable "image_tag" {
  description = "Tag of the container image to deploy"
  type        = string
  default     = "v0.0.2"
}

variable "tech_audit_data_bucket_name" {
  description = "Name of the S3 bucket for tech audit data"
  type        = string
  default     = "tech-audit-tool-data"
}

variable "tech_audit_secret_manager_name" {
  description = "Name of the Secrets Manager secret for tech audit data"
  type        = string
  default     = "tech-audit-tool-data"
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


variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "tech-audit-tool-api"
}

variable "aws_cognito_token_url" {
  description = "AWS Cognito token URL"
  type        = string
  default     = "TO_BE_SET"
}