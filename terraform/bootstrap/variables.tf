variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "tf_state_bucket" {
  description = "Bucket name for Terraform state"
  type        = string
  default     = "book-data-tf-state"
  validation {
    condition     = can(regex("^[a-z0-9]([a-z0-9-]{1,61}[a-z0-9])?$", var.tf_state_bucket))
    error_message = "Bucket name can't contain uppercase letters, underscores, or end with dash. It must be between 3 to 63 characters."
  }
}
