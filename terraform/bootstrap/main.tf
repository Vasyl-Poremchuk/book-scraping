terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Configure the AWS provider.
provider "aws" {
  region = var.aws_region
}

# Create an S3 bucket for the Terraform state.
resource "aws_s3_bucket" "tf_state_bucket" {
  bucket = var.tf_state_bucket
}

# Enable versioning for the S3 bucket.
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.tf_state_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
