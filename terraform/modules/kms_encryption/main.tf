# KMS Encryption Module
# Control: SEC-001, MI-003
# Purpose: Encryption at rest for all agent data stores

variable "agent_id" {
  description = "Agent identifier"
  type        = string
}

variable "agent_tier" {
  description = "Agent tier"
  type        = string
}

variable "key_admins" {
  description = "List of IAM ARNs for key administrators"
  type        = list(string)
  default     = []
}

variable "key_users" {
  description = "List of IAM ARNs for key users"
  type        = list(string)
  default     = []
}

variable "control_id" {
  description = "Governance control IDs"
  type        = list(string)
  default     = ["SEC-001", "MI-003"]
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# KMS key for encryption
resource "aws_kms_key" "agent_encryption" {
  description             = "KMS key for ${var.agent_id} data encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-encryption-key"
      AgentID   = var.agent_id
      AgentTier = var.agent_tier
      ControlID = join(",", var.control_id)
      ManagedBy = "Terraform"
      Framework = "AI-Agent-Governance-v2.0"
    }
  )
}

# KMS key alias
resource "aws_kms_alias" "agent_encryption" {
  name          = "alias/${var.agent_id}-encryption"
  target_key_id = aws_kms_key.agent_encryption.key_id
}

# KMS key policy
data "aws_iam_policy_document" "kms_key_policy" {
  # Allow root account full access (required for key management)
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      ]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  # Allow key admins to manage key
  dynamic "statement" {
    for_each = length(var.key_admins) > 0 ? [1] : []
    content {
      sid    = "Allow key administrators"
      effect = "Allow"
      principals {
        type        = "AWS"
        identifiers = var.key_admins
      }
      actions = [
        "kms:Create*",
        "kms:Describe*",
        "kms:Enable*",
        "kms:List*",
        "kms:Put*",
        "kms:Update*",
        "kms:Revoke*",
        "kms:Disable*",
        "kms:Get*",
        "kms:Delete*",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion"
      ]
      resources = ["*"]
    }
  }

  # Allow key users to use key for encryption/decryption
  dynamic "statement" {
    for_each = length(var.key_users) > 0 ? [1] : []
    content {
      sid    = "Allow key users"
      effect = "Allow"
      principals {
        type        = "AWS"
        identifiers = var.key_users
      }
      actions = [
        "kms:Decrypt",
        "kms:DescribeKey",
        "kms:Encrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:CreateGrant"
      ]
      resources = ["*"]

      condition {
        test     = "StringEquals"
        variable = "kms:ViaService"
        values = [
          "secretsmanager.${data.aws_region.current.name}.amazonaws.com",
          "dynamodb.${data.aws_region.current.name}.amazonaws.com",
          "s3.${data.aws_region.current.name}.amazonaws.com"
        ]
      }
    }
  }

  # Allow CloudWatch Logs to use key
  statement {
    sid    = "Allow CloudWatch Logs"
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = [
        "logs.${data.aws_region.current.name}.amazonaws.com"
      ]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey"
    ]
    resources = ["*"]

    condition {
      test     = "ArnLike"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values = [
        "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*"
      ]
    }
  }
}

resource "aws_kms_key_policy" "agent_encryption" {
  key_id = aws_kms_key.agent_encryption.id
  policy = data.aws_iam_policy_document.kms_key_policy.json
}

# Outputs
output "key_id" {
  description = "KMS key ID"
  value       = aws_kms_key.agent_encryption.id
}

output "key_arn" {
  description = "KMS key ARN"
  value       = aws_kms_key.agent_encryption.arn
}

output "key_alias" {
  description = "KMS key alias"
  value       = aws_kms_alias.agent_encryption.name
}
