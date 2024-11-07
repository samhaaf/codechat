resource "aws_api_gateway_rest_api" "this" {
    name        = "det_logscale_management_api_${var.environment}"
    description = "API Gateway for ${var.environment}"
    endpoint_configuration {
        types = ["PRIVATE"]
    }
}

resource "aws_api_gateway_resource" "this" {
    rest_api_id = aws_api_gateway_rest_api.this.id
    parent_id   = aws_api_gateway_rest_api.this.root_resource_id
    path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "this" {
    rest_api_id   = aws_api_gateway_rest_api.this.id
    resource_id   = aws_api_gateway_resource.this.id
    http_method   = "ANY"
    authorization = "NONE"
}

resource "aws_api_gateway_integration" "this" {
    rest_api_id = aws_api_gateway_rest_api.this.id
    resource_id = aws_api_gateway_resource.this.id
    http_method = aws_api_gateway_method.this.http_method

    type                    = "AWS_PROXY"
    integration_http_method = "POST"
    uri                     = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${var.lambda_function_arn}/invocations"
}

resource "aws_api_gateway_deployment" "this" {
    rest_api_id = aws_api_gateway_rest_api.this.id

    depends_on = [
        aws_api_gateway_integration.this
    ]
}

resource "aws_api_gateway_stage" "this" {
    stage_name    = var.stage_name
    rest_api_id   = aws_api_gateway_rest_api.this.id
    deployment_id = aws_api_gateway_deployment.this.id

    access_log_settings {
        destination_arn = aws_cloudwatch_log_group.this.arn
        format          = "$context.identity.sourceIp $context.identity.caller $context.identity.user [$context.requestTime] \"$context.httpMethod $context.routeKey $context.protocol\" $context.status $context.responseLength $context.requestId"
    }
}

resource "aws_lambda_permission" "this_apigw" {
    statement_id  = "AllowExecutionFromAPIGateway"
    action        = "lambda:InvokeFunction"
    function_name = var.lambda_function_name
    principal     = "apigateway.amazonaws.com"
    source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${aws_api_gateway_rest_api.this.id}/*/${aws_api_gateway_method.this.http_method}${aws_api_gateway_resource.this.path}"
}

# VPC Endpoint for API Gateway

resource "aws_vpc_endpoint" "api_gw_endpoint" {
    vpc_id            = var.vpc_id
    service_name      = "com.amazonaws.${var.region}.execute-api"
    vpc_endpoint_type = "Interface"
    subnet_ids        = var.vpc_subnet_ids

    security_group_ids = [var.vpc_security_group_id]

    private_dns_enabled = true
}
