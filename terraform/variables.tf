variable "access_key" {
  description = "Access key to AWS console"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Secret key to AWS console"
  type        = string
  sensitive   = true
}

variable "region" {
  default     = "ap-southeast-1"
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for SG"
  type        = string
}

variable "db_username" {
  description = "RDS DB username"
  type        = string
}

variable "db_password" {
  description = "RDS DB password"
  type        = string
  sensitive   = true
}

variable "opensearch_username" {
  description = "Vector DB password"
  type        = string
}

variable "opensearch_password" {
  description = "Vector DB password"
  type        = string
  sensitive   = true
}
