variable "account_id" {
  type        = string
  description = "This variable defines the account ID of the AWS environment."
}

variable "region" {
  type        = string
  description = "This variable defines the region of the lambda."
  default     = "us-east-2"
}

variable "team" {
  type        = string
  description = "The team responsible for this resource"
  default     = "det"
}

variable "project" {
  type        = string
  description = "The name of the project to use in prefixes"
  default     = "logscale_management_api"
}

variable "environment" {
  type        = string
  description = "This variable defines the environment the module is running in."
}

variable "stage_name" {
  type        = string
  description = "The name of the API Gateway Stage"
  default     = "default"
}

variable "log_retention_in_days" {
  type        = number
  description = "This variable defines the retention period in days for the CloudWatch log group."
  default     = 30
}

variable "lambda_function_arn" {
  type        = string
  description = "ARN of the lambda function that handles proxy requests."
}

variable "lambda_function_name" {
  type        = string
  description = "Name of the lambda function that handles proxy requests."
}

variable "vpc_id" {
  type        = string
  description = "The vpc id's to associate to the gateway."
}

variable "vpc_subnet_ids" {
  type        = set(string)
  description = "The subnet id's to associate to the gateway."
}

variable "vpc_security_group_id" {
  type        = string
  description = "The security group id to associate to the gateway"
}

variable "common_tags" {
  type        = map(string)
  description = "This variable defines the common tags for the resources."
}
