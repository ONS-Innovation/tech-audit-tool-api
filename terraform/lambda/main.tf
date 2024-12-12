terraform {
  backend "s3" {
    # Backend is selected using terraform init -backend-config=path/to/backend-<env>.tfbackend
    # bucket         = "sdp-dev-tf-state"
    # key            = "sdp-dev-tech-audit-tool-api-lambda/terraform.tfstate"
    # region         = "eu-west-2"
    # dynamodb_table = "terraform-state-lock"
  }

}

# 1. First create the IAM role
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.domain}-${var.service_subdomain}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# 2. Attach basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  depends_on = [aws_iam_role.lambda_execution_role]
}

# 3. Add ECR policy
resource "aws_iam_role_policy" "lambda_ecr_policy" {
  name = "${var.domain}-${var.service_subdomain}-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetAuthorizationToken",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetRepositoryPolicy"
        ]
        Resource = [
          "arn:aws:ecr:${var.region}:${var.aws_account_id}:repository/${var.ecr_repository}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      }
    ]
  })
  depends_on = [aws_iam_role.lambda_execution_role]
}

# 4. Add S3 access policy
resource "aws_iam_role_policy" "lambda_s3_access" {
  name = "${var.domain}-${var.service_subdomain}-lambda-s3-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${data.terraform_remote_state.storage.outputs.tech_audit_data_bucket_name}",
          "arn:aws:s3:::${data.terraform_remote_state.storage.outputs.tech_audit_data_bucket_name}/*"
        ]
      }
    ]
  })
  depends_on = [aws_iam_role.lambda_execution_role]
}

# 5. Add additional permissions
resource "aws_iam_role_policy" "lambda_additional_permissions" {
  name = "${var.domain}-${var.service_subdomain}-policy-additional"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup"
        ]
        Resource = "arn:aws:logs:${var.region}:${var.aws_account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.region}:${var.aws_account_id}:log-group:/aws/lambda/${var.domain}-${var.service_subdomain}-lambda:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "execute-api:Invoke",
          "execute-api:ManageConnections"
        ]
        Resource = "arn:aws:execute-api:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "s3-object-lambda:*"
        ]
        Resource = "*"
      }
    ]
  })
  depends_on = [aws_iam_role.lambda_execution_role]
}

resource "aws_security_group" "lambda_sg" {
  name = "${var.domain}-${var.service_subdomain}-lambda-sg"
  description = "Security group for ${var.domain}-${var.service_subdomain}-lambda Lambda function"
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] // Allow HTTPS traffic within VPC
  }  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.domain}-${var.service_subdomain}-lambda-sg"
  }
}

# 6. Create the Lambda function
resource "aws_lambda_function" "tech_audit_lambda" {
  function_name = "${var.domain}-${var.service_subdomain}-lambda"
  package_type  = "Image"
  image_uri     = "${var.aws_account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.ecr_repository}:${var.container_ver}"
  
  vpc_config {
    subnet_ids          = data.terraform_remote_state.vpc.outputs.private_subnets
    security_group_ids  = [aws_security_group.lambda_sg.id] // Dedicated security group for Lambda function
  }

  role = aws_iam_role.lambda_execution_role.arn

  memory_size = 128
  timeout     = 30

  environment {
    variables = {
      TECH_AUDIT_DATA_BUCKET = data.terraform_remote_state.storage.outputs.tech_audit_data_bucket_name
      TECH_AUDIT_SECRET_MANAGER = data.terraform_remote_state.secrets.outputs.secret_name
      AWS_COGNITO_TOKEN_URL = "https://${var.service_subdomain}-${var.domain}.auth.eu-west-2.amazoncognito.com/oauth2/token"
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_ecr_policy,
    aws_iam_role_policy.lambda_s3_access,
    aws_iam_role_policy.lambda_additional_permissions,
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy_attachment.lambda_vpc_access,
    aws_ecr_repository_policy.lambda_ecr_access
  ]
}

# 7. Add ECR policy after the lambda function is created
resource "aws_ecr_repository_policy" "lambda_ecr_access" {
  repository = var.ecr_repository

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "LambdaECRImageRetrievalPolicy"
        Effect = "Allow"
        Principal = {
          AWS = [
            "arn:aws:iam::${var.aws_account_id}:root"
          ]
        }
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  })

  depends_on = [aws_iam_role.lambda_execution_role]
}

# Add VPC access policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  depends_on = [aws_iam_role.lambda_execution_role]
} 