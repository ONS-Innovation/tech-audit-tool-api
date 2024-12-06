# Create a service running on fargate with a task definition and service definition
terraform {
  backend "s3" {
    # Backend is selected using terraform init -backend-config=path/to/backend-<env>.tfbackend
    # bucket         = "sdp-dev-tf-state"
    # key            = "sdp-sandbox-tech-audit-tool-api-lambda/terraform.tfstate"
    # region         = "eu-west-2"
    # dynamodb_table = "terraform-state-lock"
  }

}

# Remove the ECR repository creation since it already exists
# Instead, use data source to reference existing ECR
data "aws_ecr_repository" "tech_audit_tool" {
  name = var.ecr_repository_name
}

# Initial ECR repository policy (without Lambda role)
resource "aws_ecr_repository_policy" "tech_audit_tool_policy" {
  repository = data.aws_ecr_repository.tech_audit_tool.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPushPull"
        Effect = "Allow"
        Principal = {
          AWS = [
            "arn:aws:iam::${var.aws_account_id}:root",
            "arn:aws:iam::${var.aws_account_id}:user/ecr-user"
          ]
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
      }
    ]
  })
}

# Output the repository name for use in other modules
output "repository_name" {
  value = data.aws_ecr_repository.tech_audit_tool.name
}