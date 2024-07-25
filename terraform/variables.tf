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

variable "account_id" {
  description = "AWS Account ID"
  type        = string
  sensitive   = true
}

variable "public_subnet_cidr_blocks" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "private_subnet_cidr_blocks" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.2.0/24"]
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["ap-southeast-1a"]
}


