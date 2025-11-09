terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "book-data-tf-state"
    key          = "terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

# Configure the AWS provider.
provider "aws" {
  region = var.aws_region
}

# Create an ECR repository to store project images.
resource "aws_ecr_repository" "ecr_repo" {
  name                 = var.book_repo
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Create an ECS cluster.
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "book-cluster"
}

# Create an ECS task execution role with attached policy to it.
resource "aws_iam_role" "ecs_task_exec_role" {
  name = "book-ecs-task-exec-role"

  assume_role_policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "ecs-tasks.amazonaws.com"
          }
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_role_policy_attach" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Create an ECS task role with S3 permissions for storing data with attached policy to it.
resource "aws_iam_role" "ecs_task_role" {
  name = "book-ecs-task-role"

  assume_role_policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "ecs-tasks.amazonaws.com"
          }
        }
      ]
    }
  )
}

resource "aws_iam_policy" "s3_access_policy" {
  name        = "book-s3-access-policy"
  description = "Allow ECS tasks to access S3 bucket for storing book data"

  policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "s3:PutObject",
            "s3:GetObject",
            "s3:ListObject",
            "s3:DeleteObject",
          ]
          Resource = [
            "arn:aws:s3:::${var.book_bucket}",
            "arn:aws:s3:::${var.book_bucket}/*"
          ]
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "s3_access_policy_attach" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# Create an S3 bucket for storing the data.
resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.book_bucket
}

# Create an ECS task definition.
resource "aws_ecs_task_definition" "ecs_task_def" {
  family                   = "book-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode(
    [
      {
        name      = "book-container"
        image     = "${aws_ecr_repository.ecr_repo.repository_url}:latest"
        essential = true
        environemt = [
          { name = "S3_BUCKET", value = var.book_bucket }
        ]
    }]
  )
}

# Create a Lambda function to trigger ECS task.
resource "aws_lambda_function" "lambda_trigger" {
  function_name = "book-trigger"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_func.trigger_ecs_task_handler"
  runtime       = "python3.13"
  timeout       = 60

  filename         = data.archive_file.lambda_code.output_path
  source_code_hash = data.archive_file.lambda_code.output_base64sha256

  environment {
    variables = {
      CLUSTER_NAME      = aws_ecs_cluster.ecs_cluster.name
      TASK_DEFINITION   = aws_ecs_task_definition.ecs_task_def.arn
      SUBNET_ID         = var.subnet_id
      SECURITY_GROUP_ID = aws_security_group.sc.id
    }
  }
}

data "archive_file" "lambda_code" {
  type        = "zip"
  source_file = "${path.module}/lambda/lambda_func.py"
  output_path = "${path.module}/lambda/lambda_func.zip"
}

# Create an IAM role for Lambda function with attached policies to it.
resource "aws_iam_role" "lambda_role" {
  name = "book-lambda-role"

  assume_role_policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
          }
        }
      ]
    }
  )
}

resource "aws_iam_policy" "lambda_ecs_policy" {
  name        = "book-lambda-ecs-policy"
  description = "Allow Lambda function to run ECS tasks"

  policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["ecs:RunTask"]
          Effect   = "Allow"
          Resource = aws_ecs_task_definition.ecs_task_def.arn
        },
        {
          Action = ["iam:PassRole"]
          Effect = "Allow"
          Resource = [
            aws_iam_role.ecs_task_exec_role.arn,
            aws_iam_role.ecs_task_role.arn
          ]
        }
      ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "lambda_logs_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_ecs_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_ecs_policy.arn
}

# Create a security group for ECS tasks.
resource "aws_security_group" "sc" {
  name        = "book-ecs-tasks-sg"
  description = "Allow outbound traffic from ECS tasks"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create an EventBridge rule for scheduled execution (once per week).
resource "aws_cloudwatch_event_rule" "weekly_trigger" {
  name                = "book-weekly-trigger"
  description         = "Trigger book data scraping & parsing weekly"
  schedule_expression = "cron(0 0 ? * SUN *)" # Run every Sunday at midnight.
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.weekly_trigger.name
  target_id = "InvokeLambda"
  arn       = aws_lambda_function.lambda_trigger.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_trigger.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_trigger.arn
}
