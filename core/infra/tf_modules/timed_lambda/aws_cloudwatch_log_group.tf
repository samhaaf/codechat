resource "aws_cloudwatch_log_group" "this" {
  name = "/aws/lambda/${var.team}_${var.project}_${var.environment}"
  tags              = var.common_tags
  retention_in_days = 30
}
