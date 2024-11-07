variable "account_id" {
  type        = string
  description = "This variable defines the account ID of the AWS environment."
}

variable "region" {
  type        = string
  description = "This variable defines the region of the lambda."
}

variable "team" {
  type        = string
  description = "The team responsible for this resource"
}

variable "project" {
  type        = string
  description = "The name of the project to use in prefixes"
}

variable "environment" {
  type        = string
  description = "This variable defines the environment the module is running in."
}

variable "lambda_runtime" {
  type        = string
  description = "Which runtime to use in the lambda function."
}

variable "lambda_handler" {
  type        = string
  description = "The path to the handler."
}

variable "lambda_source_dir" {
  type        = string
  description = "This variable defines the source directory for the lambda function."
}

variable "lambda_layer_dir" {
  type        = string
  description = "This variable defines the source directory for the lambda layer."
}

variable "timeout" {
  type        = string
  description = "This variable defines the timeout for the lambda function."
}

variable "memory_size" {
  type        = number
  description = "The amount of memory that the Lambda needs to run."
}

variable "invoke_lambda_every" {
  type        = string
  description = "The rate at which cloudwatch should invoke the lambda. (e.g. '30 minutes')"
}

variable "log_retention_in_days" {
  type        = number
  description = "This variable defines the retention period in days for the CloudWatch log group."
}

variable "vpc_subnet_ids" {
  type        = set(string)
  description = "The subnet id's to associate to the lambda."
}

variable "vpc_security_group_ids" {
  type        = string
  description = "The security group id's to associate to the lambda"
}

variable "artifact_bucket" {
  type        = string
  description = "The bucket to retrieve relevant lambda artifacts."
}

variable "layer_zip_key" {
  type        = string
  description = "The key for the lambda layer zip file in the S3 bucket."
}

variable "build_layer_command" {
  type        = string
  description = "The command to build the lambda function."
}

variable "common_tags" {
  type        = map(string)
  description = "This variable defines the common tags for the resources."
}

variable "environment_variables" {
  type        = map(string)
  description = "This is the map of environment variables to inject into the lambda."
}
