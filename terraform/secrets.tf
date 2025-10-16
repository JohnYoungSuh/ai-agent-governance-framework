# Secrets Management (MI-003: Secrets Management & Environment Isolation)
# Addresses: RI-015 (Data to Hosted LLM)

# AWS Secrets Manager for storing sensitive credentials
resource "aws_secretsmanager_secret" "llm_api_key" {
  name        = "${var.agent_name}-llm-api-key"
  description = "LLM API key for ${var.agent_name} (${var.llm_model_provider})"

  recovery_window_in_days = 7

  tags = merge(
    var.tags,
    {
      Name           = "${var.agent_name}-llm-api-key"
      ControlID      = "MI-003"
      RiskAddresses  = "RI-015"
      SecurityLevel  = "Critical"
      RotationPolicy = "90-days"
    }
  )
}

# GitHub token for repository access
resource "aws_secretsmanager_secret" "github_token" {
  name        = "${var.agent_name}-github-token"
  description = "GitHub token for ${var.agent_name}"

  recovery_window_in_days = 7

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-github-token"
      ControlID     = "MI-003"
      RiskAddresses = "RI-015"
      SecurityLevel = "Critical"
    }
  )
}

# Slack webhook URL
resource "aws_secretsmanager_secret" "slack_webhook" {
  count = var.slack_webhook_url != "" ? 1 : 0

  name        = "${var.agent_name}-slack-webhook"
  description = "Slack webhook URL for ${var.agent_name} notifications"

  recovery_window_in_days = 7

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-slack-webhook"
      ControlID     = "MI-003"
      SecurityLevel = "Confidential"
    }
  )
}

# JIRA API token
resource "aws_secretsmanager_secret" "jira_token" {
  count = var.jira_api_url != "" ? 1 : 0

  name        = "${var.agent_name}-jira-token"
  description = "JIRA API token for ${var.agent_name}"

  recovery_window_in_days = 7

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-jira-token"
      ControlID     = "MI-003"
      SecurityLevel = "Confidential"
    }
  )
}

# IAM policy for accessing secrets
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.agent_name}-secrets-access"
  description = "Allow ${var.agent_name} to access required secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.llm_api_key.arn,
          aws_secretsmanager_secret.github_token.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.agent_encryption.arn
        ]
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-secrets-access"
      ControlID = "MI-003"
    }
  )
}

# KMS key for encryption at rest
resource "aws_kms_key" "agent_encryption" {
  description             = "KMS key for ${var.agent_name} encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-encryption-key"
      ControlID     = "MI-003"
      SecurityLevel = "Critical"
    }
  )
}

resource "aws_kms_alias" "agent_encryption" {
  name          = "alias/${var.agent_name}-encryption"
  target_key_id = aws_kms_key.agent_encryption.key_id
}
