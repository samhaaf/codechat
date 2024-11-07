data "archive_file" "lambda_zip" {
  type             = "zip"
  output_path      = "${var.lambda_source_dir}.zip"
  output_file_mode = "0755"
  source_dir       = var.lambda_source_dir

  depends_on = [
    null_resource.install_dependencies
  ]
}

data "archive_file" "lambda_layer_zip" {
  type             = "zip"
  output_path      = "${var.lambda_layer_dir}.zip"
  output_file_mode = "0755"
  source_dir       = var.lambda_layer_dir

  depends_on = [
    null_resource.install_dependencies
  ]
}

resource "null_resource" "install_dependencies" {
  provisioner "local-exec" {
    command = var.build_layer_command
  }
  triggers = {
    always_run = "${timestamp()}" #ensures the resource is always triggered since the terraform cloud agent cleans up after every run.
  }

}
