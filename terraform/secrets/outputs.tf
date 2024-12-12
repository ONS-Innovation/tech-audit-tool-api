output "secret_arn" {
  description = "ARN of the secret"
  value       = aws_secretsmanager_secret.cognito_secrets.arn
}

output "secret_name" {
  description = "Name of the secret"
  value       = aws_secretsmanager_secret.cognito_secrets.name
}
