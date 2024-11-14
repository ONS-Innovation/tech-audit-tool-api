terraform {
  backend "s3" {
    # Backend is selected using terraform init -backend-config=path/to/backend-<env>.tfbackend
    # bucket         = "sdp-dev-tf-state"
    # key            = "sdp-sandbox-ecs-tech-audit-tool-api-gateway/terraform.tfstate"
    # region         = "eu-west-2"
    # dynamodb_table = "terraform-state-lock"
  }

}

# Add these data sources at the top of the file, after the terraform block
data "aws_route53_zone" "domain" {
  name = "${var.domain}.${var.domain_extension}"
}

# Create the API Gateway REST API
resource "aws_api_gateway_rest_api" "main" {
  name = "${var.domain}-${var.service_subdomain}"

  tags = {
    Project       = var.project_tag
    TeamOwner     = var.team_owner_tag
    BusinessOwner = var.business_owner_tag
  }
}

# Create an authorizer using the Cognito User Pool
resource "aws_api_gateway_authorizer" "cognito" {
  name            = "${var.service_subdomain}-authorizer"
  rest_api_id     = aws_api_gateway_rest_api.main.id
  type            = "COGNITO_USER_POOLS"
  provider_arns   = [var.cognito_user_pool_arn]
  identity_source = "method.request.header.Authorization"
}
# Root API resource
resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "api"
}

# /api/v1 resource
resource "aws_api_gateway_resource" "api_v1_resource" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api_resource.id
  path_part   = "v1"
}

# /api/v1/projects resource
resource "aws_api_gateway_resource" "projects_resource" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api_v1_resource.id
  path_part   = "projects"
}

# /api/v1/projects GET and POST methods
resource "aws_api_gateway_method" "projects_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.projects_resource.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

resource "aws_api_gateway_method" "projects_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.projects_resource.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# /api/v1/projects/{proxy+} resource and methods
resource "aws_api_gateway_resource" "projects_proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.projects_resource.id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "projects_proxy_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.projects_proxy.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
    "method.request.path.proxy"           = true
  }
}

resource "aws_api_gateway_method" "projects_proxy_put" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.projects_proxy.id
  http_method   = "PUT"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
    "method.request.path.proxy"           = true
  }
}

# /api/v1/projects/filter resource and GET method
resource "aws_api_gateway_resource" "projects_filter" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.projects_resource.id
  path_part   = "filter"
}

resource "aws_api_gateway_method" "projects_filter_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.projects_filter.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# /api/v1/user resource and GET method
resource "aws_api_gateway_resource" "user_resource" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api_v1_resource.id
  path_part   = "user"
}

resource "aws_api_gateway_method" "user_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.user_resource.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# /api/v1/verify resource and GET method
resource "aws_api_gateway_resource" "verify_resource" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api_v1_resource.id
  path_part   = "verify"
}

resource "aws_api_gateway_method" "verify_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.verify_resource.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}

# /swagger.json resource and GET method
resource "aws_api_gateway_resource" "swagger_json" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "swagger.json"
}

resource "aws_api_gateway_method" "swagger_json_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.swagger_json.id
  http_method   = "GET"
  authorization = "NONE"
}

# /swaggerui resource and GET method
resource "aws_api_gateway_resource" "swaggerui" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "swaggerui"
}

resource "aws_api_gateway_method" "swaggerui_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.swaggerui.id
  http_method   = "GET"
  authorization = "NONE"
}

# /swaggerui/{proxy+} resource and GET method
resource "aws_api_gateway_resource" "swaggerui_proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.swaggerui.id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "swaggerui_proxy_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.swaggerui_proxy.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.path.proxy" = true
  }
}

# Lambda integrations for all protected endpoints
resource "aws_api_gateway_integration" "lambda_integration" {
  for_each = {
    "projects_get"        = aws_api_gateway_method.projects_get
    "projects_post"       = aws_api_gateway_method.projects_post
    "projects_proxy_get"  = aws_api_gateway_method.projects_proxy_get
    "projects_proxy_put"  = aws_api_gateway_method.projects_proxy_put
    "projects_filter_get" = aws_api_gateway_method.projects_filter_get
    "user_get"            = aws_api_gateway_method.user_get
    "verify_get"          = aws_api_gateway_method.verify_get
  }

  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = each.value.resource_id
  http_method             = each.value.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${var.lambda_function_invoke_arn}/invocations"
}

# Mock integrations for Swagger endpoints
resource "aws_api_gateway_integration" "mock_integration" {
  for_each = {
    "swagger_json"    = aws_api_gateway_method.swagger_json_get
    "swaggerui"       = aws_api_gateway_method.swaggerui_get
    "swaggerui_proxy" = aws_api_gateway_method.swaggerui_proxy_get
  }

  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = each.value.resource_id
  http_method = each.value.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  depends_on = [
    aws_api_gateway_integration.lambda_integration,
    aws_api_gateway_integration.mock_integration
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.stage_name

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      errorMessage   = "$context.error.message"
      errorType      = "$context.error.responseType"
    })
  }
}

# Stage settings
resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.main.stage_name
  method_path = "*/*"

  settings {
    logging_level      = "ERROR"
    data_trace_enabled = false
    metrics_enabled    = true
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*/*"
}

# Create API Gateway domain name
resource "aws_api_gateway_domain_name" "api" {
  domain_name              = "${var.service_subdomain}.${var.domain}.${var.domain_extension}"
  regional_certificate_arn = aws_acm_certificate_validation.cert_validation.certificate_arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Create Route53 record
resource "aws_route53_record" "api" {
  name    = aws_api_gateway_domain_name.api.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.domain.zone_id

  alias {
    name                   = aws_api_gateway_domain_name.api.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api.regional_zone_id
    evaluate_target_health = true
  }
}

# Create ACM certificate
resource "aws_acm_certificate" "cert" {
  domain_name       = "${var.service_subdomain}.${var.domain}.${var.domain_extension}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Create Route53 record for certificate validation
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.domain.zone_id
}

# Certificate validation
resource "aws_acm_certificate_validation" "cert_validation" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# Map custom domain to API Gateway stage
resource "aws_api_gateway_base_path_mapping" "api" {
  api_id      = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.main.stage_name
  domain_name = aws_api_gateway_domain_name.api.domain_name
}
