resource "aws_cloudwatch_event_rule" "this" {
  name                = "lambda_${var.team}_${var.project}_${var.environment}_schedule"
  description         = "Fires every thirty minutes"
  schedule_expression = "rate(${var.invoke_lambda_every})"
}

resource "aws_cloudwatch_event_target" "this" {
  rule      = aws_cloudwatch_event_rule.this.name
  target_id = aws_lambda_function.this.id
  arn       = aws_lambda_function.this.arn
}

resource "aws_lambda_permission" "this" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.this.arn
}
