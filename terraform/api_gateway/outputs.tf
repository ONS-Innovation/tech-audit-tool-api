output "api_gateway_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.main.id
}

output "api_gateway_stage_name" {
  description = "Name of the API Gateway stage"
  value       = aws_api_gateway_stage.main.stage_name
}

output "api_gateway_invoke_url" {
  description = "Invoke URL for the API Gateway stage"
  value       = aws_api_gateway_stage.main.invoke_url
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.main.execution_arn
}

output "api_domain_name" {
  description = "Custom domain name for the API"
  value       = aws_api_gateway_domain_name.api.domain_name
}

output "api_endpoint" {
  description = "Custom domain endpoint for the API"
  value       = "https://${aws_api_gateway_domain_name.api.domain_name}"
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch Log Group for API Gateway errors"
  value       = aws_cloudwatch_log_group.api_gateway.name
}