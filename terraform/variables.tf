variable "access_key" {
    description = "Access key to AWS console"
}

variable "secret_key" {
    description = "Secret key to AWS console"
}

variable "region" {
  default     = "ap-southeast-1"
  description = "AWS region"
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
