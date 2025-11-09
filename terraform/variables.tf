variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "book_bucket" {
  description = "Bucket name for storing data"
  type        = string
  default     = "book-scraping-data"
  validation {
    condition     = can(regex("^[a-z0-9]([a-z0-9-]{1,61}[a-z0-9])?$", var.book_bucket))
    error_message = "Bucket name can't contain uppercase letters, underscores, or end with dash. It must be between 3 to 63 characters."
  }
}

variable "book_repo" {
  description = "Repository name for storing images"
  type        = string
  default     = "book-repo"
}

variable "vpc_id" {
  description = "VPC ID for security group"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for ECS tasks"
  type        = string
}

variable "task_cpu" {
  description = "CPU units for ECS task"
  type        = string
  default     = "4096" # 4 vCPU
}

variable "task_memory" {
  description = "Memory for ECS task in MB"
  type        = string
  default     = "16384" # 16 GB
}
