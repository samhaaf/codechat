resource "aws_lambda_function" "this" {
  function_name     = "${var.team}_${var.project}_${var.environment}"
  role              = aws_iam_role.this.arn
  runtime           = var.lambda_runtime
  handler           = var.lambda_handler
  timeout           = var.timeout
  s3_bucket         = var.artifact_bucket
  s3_key            = aws_s3_object.lambda_zip.key
  s3_object_version = aws_s3_object.lambda_zip.version_id
  source_code_hash  = aws_s3_object.lambda_zip.etag
  layers            = [aws_lambda_layer_version.this.arn]
  memory_size       = var.memory_size
  publish           = true
  environment {
    variables = var.environment_variables
  }
  vpc_config {
    subnet_ids         = var.vpc_subnet_ids
    security_group_ids = [var.vpc_security_group_ids]
  }
  depends_on = [aws_iam_role.this]
}

resource "aws_lambda_layer_version" "this" {
  layer_name               = "${var.team}_${var.project}_${var.environment}_layer"
  s3_bucket                = var.artifact_bucket
  s3_key                   = aws_s3_object.layer_zip.id
  s3_object_version        = aws_s3_object.layer_zip.version_id
  compatible_runtimes      = [var.lambda_runtime]
  compatible_architectures = ["x86_64"]
}
