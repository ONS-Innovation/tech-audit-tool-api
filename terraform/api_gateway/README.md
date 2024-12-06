## Adding new API Gateway endpoints

### Adding a resource (/api/v1/<resource>)

```
resource "aws_api_gateway_resource" "<resource_name>_resource" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api_v1_resource.id
  path_part   = "user"
}
```

`rest_api_id` is the id of the API Gateway.

`parent_id` is the id of the resource `/api/v1/`.

`path_part` is the name of the resource ie. `user`.


### Adding a method (GET /api/v1/<resource>)

```
resource "aws_api_gateway_method" "<resource_name>_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.<resource_name>_resource.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.header.Authorization" = true
  }
}
```

`rest_api_id` is the id of the API Gateway.

`resource_id` is the id of the resource `/api/v1/<resource>`.

`http_method` is the HTTP method ie. `GET`.


### Adding the integration for the method
Then add in the integration for the method.

```bash
resource "aws_api_gateway_integration" "lambda_integration" {
  for_each = {
    "projects_get"        = aws_api_gateway_method.projects_get
    "projects_post"       = aws_api_gateway_method.projects_post
    "projects_proxy_get"  = aws_api_gateway_method.projects_proxy_get
    "projects_proxy_put"  = aws_api_gateway_method.projects_proxy_put
    "projects_filter_get" = aws_api_gateway_method.projects_filter_get
    "user_get"            = aws_api_gateway_method.user_get
    "verify_get"          = aws_api_gateway_method.verify_get
    "<resource_name>_get" = aws_api_gateway_method.<resource_name>_get
  }

  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = each.value.resource_id
  http_method             = each.value.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${data.terraform_remote_state.api_lambda.outputs.lambda_function_arn}/invocations"
}
```
