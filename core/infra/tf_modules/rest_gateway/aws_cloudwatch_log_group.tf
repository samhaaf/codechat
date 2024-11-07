resource "aws_cloudwatch_log_group" "this" {
  name = "/API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.this.id}/${var.stage_name}"
  tags              = var.common_tags
  retention_in_days = var.log_retention_in_days
}
