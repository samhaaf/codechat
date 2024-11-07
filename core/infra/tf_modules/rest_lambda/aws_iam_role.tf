resource "aws_iam_role" "this" {
    name = "lambda_${var.team}_${var.project}_${var.environment}"

    assume_role_policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Effect = "Allow",
                Action = "sts:AssumeRole",
                Principal = {
                    Service = "lambda.amazonaws.com"
                }
            }
        ]
    })
}

resource "aws_iam_role_policy" "this" {
    name = "lambda_${var.team}_${var.project}_${var.environment}"
    role = aws_iam_role.this.id

    policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Effect = "Allow",
                Action = "iam:ListRoles",
                Resource = "arn:aws:sts::${var.account_id}:assumed-role/${aws_iam_role.this.name}/${var.team}_${var.project}_${var.environment}"
            },
            {
                Effect = "Allow",
                Action = [
                    "logs:CreateLogStream",
                    "logs:DescribeLogStreams",
                    "logs:PutLogEvents",
                    "sns:Publish"
                ],
                Resource = "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/lambda/${var.team}_${var.project}_${var.environment}:*"
            },
            {
                Effect = "Allow",
                Action = [
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface",
                    "ec2:AssignPrivateIpAddresses",
                    "ec2:UnassignPrivateIpAddresses"
                ],
                Resource = "*"
            }
        ]
    })
}
