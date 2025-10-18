# AI Agent Governance Framework - Modular Terraform Configuration
# Uses reusable modules for governance compliance
# Version: 2.0

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Optional: Use S3 backend for state management
  # Uncomment and configure for production use
  # backend "s3" {
  #   bucket         = "ai-agent-governance-terraform-state"
  #   key            = "agents/${var.agent_name}/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  #   kms_key_id     = "alias/terraform-state-key"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project         = "AI-Agent-Governance"
      ManagedBy       = "Terraform"
      AgentID         = var.agent_name
      AgentTier       = var.agent_tier
      Environment     = var.environment
      Framework       = "ai-agent-governance-v2.0"
      DeployedBy      = "terraform-modules"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  common_tags = merge(
    var.tags,
    {
      AgentName   = var.agent_name
      AgentTier   = var.agent_tier
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

# ============================================================================
# MODULE 1: KMS Encryption (SEC-001, MI-003)
# ============================================================================
module "kms_encryption" {
  source = "./modules/kms_encryption"

  agent_id   = var.agent_name
  agent_tier = var.agent_tier

  # Key administrators (adjust based on your organization)
  key_admins = [
    "arn:aws:iam::${local.account_id}:role/AdminRole", # Replace with actual role
  ]

  # Key users (will be granted by module for specific services)
  key_users = []

  control_id = ["SEC-001", "MI-003"]
  tags       = local.common_tags
}

# ============================================================================
# MODULE 2: Secrets Manager (SEC-001, MI-003)
# ============================================================================
module "secrets_manager" {
  source = "./modules/secrets_manager"

  agent_id   = var.agent_name
  agent_tier = var.agent_tier
  kms_key_id = module.kms_encryption.key_arn

  # Define secrets to create
  # NOTE: In production, use sensitive variables or retrieve from parameter store
  secrets = {
    "llm-api-key" = {
      description = "LLM API key for ${var.llm_model_provider}"
      value       = var.llm_api_key # Must be provided via tfvars or environment
    }
    "github-token" = {
      description = "GitHub PAT for CI/CD integration"
      value       = var.github_token
    }
  }

  control_id = ["SEC-001", "MI-003"]
  tags       = local.common_tags
}

# ============================================================================
# MODULE 3: DynamoDB Audit Trail (MI-019)
# ============================================================================
module "audit_trail" {
  source = "./modules/dynamodb_audit"

  agent_id   = var.agent_name
  agent_tier = var.agent_tier
  kms_key_arn = module.kms_encryption.key_arn

  # Enable point-in-time recovery for production
  point_in_time_recovery = var.environment == "production" ? true : false

  # Enable TTL for automatic archival after 90 days
  ttl_enabled = true

  control_id = ["MI-019"]
  tags       = local.common_tags
}

# ============================================================================
# IAM Role for Agent Lambda Function
# ============================================================================
resource "aws_iam_role" "agent_role" {
  name = "${var.agent_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.agent_name}-role"
      ControlID = "MI-006,MI-020"
      Purpose   = "Agent execution role with least-privilege"
    }
  )
}

# Attach policy for secret access
resource "aws_iam_role_policy" "agent_secrets_policy" {
  name   = "${var.agent_name}-secrets-policy"
  role   = aws_iam_role.agent_role.id
  policy = module.secrets_manager.iam_policy_json
}

# Attach policy for audit trail writes
resource "aws_iam_role_policy" "agent_audit_policy" {
  name = "${var.agent_name}-audit-policy"
  role = aws_iam_role.agent_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowAuditWrites"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = module.audit_trail.table_arn
      },
      {
        Sid    = "AllowS3Archive"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${module.audit_trail.archive_bucket_arn}/*"
      }
    ]
  })
}

# Attach CloudWatch Logs policy
resource "aws_iam_role_policy_attachment" "agent_logs" {
  role       = aws_iam_role.agent_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ============================================================================
# CloudWatch Log Group (MI-004 Observability)
# ============================================================================
resource "aws_cloudwatch_log_group" "agent_logs" {
  name              = "/aws/lambda/${var.agent_name}"
  retention_in_days = 90
  kms_key_id        = module.kms_encryption.key_arn

  tags = merge(
    local.common_tags,
    {
      Name      = "/aws/lambda/${var.agent_name}"
      ControlID = "MI-004,MI-019"
      Purpose   = "Agent execution logs"
    }
  )
}

# ============================================================================
# Lambda Function (Example - adjust based on your agent implementation)
# ============================================================================
resource "aws_lambda_function" "agent" {
  filename      = "${path.module}/lambda/agent.zip" # You'll need to create this
  function_name = var.agent_name
  role          = aws_iam_role.agent_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 1024

  environment {
    variables = {
      AGENT_NAME          = var.agent_name
      AGENT_TIER          = var.agent_tier
      ENVIRONMENT         = var.environment
      LLM_MODEL_PROVIDER  = var.llm_model_provider
      LLM_MODEL_VERSION   = var.llm_model_version
      AUDIT_TABLE_NAME    = module.audit_trail.table_name
      AUDIT_BUCKET_NAME   = module.audit_trail.archive_bucket_name
      SECRET_LLM_API_KEY  = module.secrets_manager.secret_names["llm-api-key"]
      SECRET_GITHUB_TOKEN = module.secrets_manager.secret_names["github-token"]
      DAILY_COST_BUDGET   = var.daily_cost_budget
      MONTHLY_COST_BUDGET = var.monthly_cost_budget
    }
  }

  # Dead letter queue for failed invocations
  dead_letter_config {
    target_arn = aws_sqs_queue.agent_dlq.arn
  }

  tags = merge(
    local.common_tags,
    {
      Name      = var.agent_name
      ControlID = "MI-001,MI-002,MI-003,MI-004,MI-009,MI-020,MI-021"
      Purpose   = "AI agent Lambda function"
    }
  )

  depends_on = [
    aws_iam_role_policy.agent_secrets_policy,
    aws_iam_role_policy.agent_audit_policy,
    aws_cloudwatch_log_group.agent_logs
  ]
}

# ============================================================================
# Dead Letter Queue for Failed Invocations
# ============================================================================
resource "aws_sqs_queue" "agent_dlq" {
  name                      = "${var.agent_name}-dlq"
  message_retention_seconds = 1209600 # 14 days
  kms_master_key_id         = module.kms_encryption.key_id

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.agent_name}-dlq"
      ControlID = "MI-004"
      Purpose   = "Dead letter queue for failed invocations"
    }
  )
}

# ============================================================================
# CloudWatch Alarms for Cost Monitoring (MI-009, MI-021)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "daily_cost_50pct" {
  alarm_name          = "${var.agent_name}-daily-cost-50pct"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "21600" # 6 hours
  statistic           = "Maximum"
  threshold           = var.daily_cost_budget * 0.5
  alarm_description   = "Alert when daily cost exceeds 50% of budget"
  alarm_actions       = [aws_sns_topic.cost_alerts.arn]

  dimensions = {
    Currency = "USD"
  }

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.agent_name}-daily-cost-50pct"
      ControlID = "MI-009,MI-021"
      Purpose   = "Cost monitoring alarm"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "daily_cost_90pct" {
  alarm_name          = "${var.agent_name}-daily-cost-90pct"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "21600"
  statistic           = "Maximum"
  threshold           = var.daily_cost_budget * 0.9
  alarm_description   = "CRITICAL: Daily cost exceeds 90% of budget - circuit breaker should activate"
  alarm_actions       = [aws_sns_topic.cost_alerts.arn]

  dimensions = {
    Currency = "USD"
  }

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.agent_name}-daily-cost-90pct"
      ControlID = "MI-009,MI-021"
      Purpose   = "Cost circuit breaker alarm"
    }
  )
}

# ============================================================================
# SNS Topic for Alerts
# ============================================================================
resource "aws_sns_topic" "cost_alerts" {
  name              = "${var.agent_name}-cost-alerts"
  kms_master_key_id = module.kms_encryption.key_id

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.agent_name}-cost-alerts"
      ControlID = "MI-009,MI-021"
      Purpose   = "Cost alert notifications"
    }
  )
}

resource "aws_sns_topic_subscription" "cost_alerts_email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.cost_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ============================================================================
# Outputs
# ============================================================================
output "agent_function_arn" {
  description = "ARN of the agent Lambda function"
  value       = aws_lambda_function.agent.arn
}

output "agent_function_name" {
  description = "Name of the agent Lambda function"
  value       = aws_lambda_function.agent.function_name
}

output "agent_role_arn" {
  description = "ARN of the agent IAM role"
  value       = aws_iam_role.agent_role.arn
}

output "kms_key_id" {
  description = "KMS key ID for agent encryption"
  value       = module.kms_encryption.key_id
}

output "kms_key_alias" {
  description = "KMS key alias"
  value       = module.kms_encryption.key_alias
}

output "audit_table_name" {
  description = "DynamoDB audit trail table name"
  value       = module.audit_trail.table_name
}

output "audit_stream_arn" {
  description = "DynamoDB stream ARN for SIEM integration"
  value       = module.audit_trail.table_stream_arn
}

output "audit_archive_bucket" {
  description = "S3 bucket for audit archive"
  value       = module.audit_trail.archive_bucket_name
}

output "secret_arns" {
  description = "ARNs of created secrets"
  value       = module.secrets_manager.secret_arns
  sensitive   = true
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.agent_logs.name
}

output "cost_alert_topic_arn" {
  description = "SNS topic ARN for cost alerts"
  value       = aws_sns_topic.cost_alerts.arn
}
