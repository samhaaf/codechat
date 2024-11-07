
data "aws_iam_policy_document" "this" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.lambda_function_arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:${aws_cloudwatch_log_group.this.name}:*"]
  }
}

data "aws_iam_policy_document" "this_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "this" {
  name = "api_gateway_${var.team}_${var.project}_${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.this_assume.json
}

resource "aws_iam_role_policy" "this" {
  name   = "api_gateway_${var.team}_${var.project}_${var.environment}"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.this.json
}
