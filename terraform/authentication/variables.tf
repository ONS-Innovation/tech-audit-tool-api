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

variable "service_title" {
  description = "Service title"
  type        = string
  default     = "Tech Audit Tool API"
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

variable "domain_extension" {
  description = "Domain extension"
  type        = string
  default     = "aws.onsdigital.uk"
}

variable "token_validity_values" {
  description = "Token validity duration values for Cognito tokens"
  type = object({
    refresh_token = number
    access_token  = number
    id_token      = number
  })
  default = {
    refresh_token = 30
    access_token  = 1
    id_token      = 1
  }
}

variable "token_validity_units" {
  description = "Time units for token validity durations"
  type = object({
    refresh_token = string
    access_token  = string
    id_token      = string
  })
  default = {
    refresh_token = "days"
    access_token  = "days"
    id_token      = "days"
  }
}

variable "callback_urls" {
  description = "List of allowed callback URLs for the Cognito user pool client"
  type        = list(string)
  default     = []
}

