
# Create CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.domain}-${var.service_subdomain}"
  retention_in_days = 30

  tags = {
    Project       = var.project_tag
    TeamOwner     = var.team_owner_tag
    BusinessOwner = var.business_owner_tag
  }
}

# Create IAM role for CloudWatch logging
resource "aws_iam_role" "cloudwatch" {
  name = "${var.domain}-${var.service_subdomain}-cloudwatch"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project       = var.project_tag
    TeamOwner     = var.team_owner_tag
    BusinessOwner = var.business_owner_tag
  }
}

# Updated CloudWatch logs policy
resource "aws_iam_role_policy" "cloudwatch_logs" {
  name = "cloudwatch-logs-policy"
  role = aws_iam_role.cloudwatch.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Enable CloudWatch logging for API Gateway
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch.arn

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
  }

  depends_on = [
    aws_iam_role.cloudwatch,
    aws_cloudwatch_log_group.api_gateway
  ]
}
