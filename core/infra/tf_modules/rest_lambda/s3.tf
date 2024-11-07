resource "aws_s3_object" "lambda_zip" {
  bucket = var.artifact_bucket
  key    = "${var.team}/${var.project}/lambda.zip"
  source = data.archive_file.lambda_zip.output_path
  etag   = data.archive_file.lambda_zip.output_md5
}


resource "aws_s3_object" "layer_zip" {
  bucket = var.artifact_bucket
  key    = "${var.team}/${var.project}/lambda_layer.zip"
  source = data.archive_file.lambda_layer_zip.output_path
  etag   = data.archive_file.lambda_zip.output_md5
}
