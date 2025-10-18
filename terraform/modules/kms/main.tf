# KMS Module
# AI Agent Governance Framework v2.1
# Control: SC-028 (Encryption), SEC-001

variable "key_alias" {
  description = "Alias for the KMS key"
  type        = string
}

variable "key_description" {
  description = "Description of the KMS key"
  type        = string
}

variable "deletion_window_in_days" {
  description = "KMS key deletion window (7-30 days)"
  type        = number
  default     = 30
}

variable "enable_key_rotation" {
  description = "Enable automatic key rotation"
  type        = bool
  default     = true
}

variable "key_administrators" {
  description = "List of IAM principal ARNs for key administration"
  type        = list(string)
  default     = []
}

variable "key_users" {
  description = "List of IAM principal ARNs for key usage"
  type        = list(string)
  default     = []
}

variable "control_ids" {
  description = "Governance control IDs"
  type        = list(string)
  default     = ["SC-028", "SEC-001"]
}

variable "jira_cr_id" {
  description = "Jira Change Request ID"
  type        = string
  default     = ""
}

variable "audit_id" {
  description = "Audit trail ID"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

data "aws_caller_identity" "current" {}

# KMS key
resource "aws_kms_key" "main" {
  description             = var.key_description
  deletion_window_in_days = var.deletion_window_in_days
  enable_key_rotation     = var.enable_key_rotation

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Sid    = "Enable IAM User Permissions"
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
          }
          Action   = "kms:*"
          Resource = "*"
        }
      ],
      length(var.key_administrators) > 0 ? [
        {
          Sid    = "Allow KMS Key Administration"
          Effect = "Allow"
          Principal = {
            AWS = var.key_administrators
          }
          Action = [
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
            "kms:TagResource",
            "kms:UntagResource",
            "kms:ScheduleKeyDeletion",
            "kms:CancelKeyDeletion"
          ]
          Resource = "*"
        }
      ] : [],
      length(var.key_users) > 0 ? [
        {
          Sid    = "Allow KMS Key Usage"
          Effect = "Allow"
          Principal = {
            AWS = var.key_users
          }
          Action = [
            "kms:Decrypt",
            "kms:DescribeKey",
            "kms:Encrypt",
            "kms:ReEncrypt*",
            "kms:GenerateDataKey*",
            "kms:CreateGrant"
          ]
          Resource = "*"
        }
      ] : []
    )
  })

  tags = merge(
    var.tags,
    {
      Name       = var.key_alias
      control_id = join(",", var.control_ids)
      Component  = "KMS"
      jira_cr_id = var.jira_cr_id
      audit_id   = var.audit_id
      Framework  = "AI-Agent-Governance-v2.1"
    }
  )
}

# KMS alias
resource "aws_kms_alias" "main" {
  name          = "alias/${var.key_alias}"
  target_key_id = aws_kms_key.main.key_id
}

# CloudWatch alarm for key deletion
resource "aws_cloudwatch_metric_alarm" "key_deletion_scheduled" {
  alarm_name          = "${var.key_alias}-deletion-scheduled"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ScheduleKeyDeletion"
  namespace           = "AWS/KMS"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Alert when KMS key deletion is scheduled"
  treat_missing_data  = "notBreaching"

  dimensions = {
    KeyId = aws_kms_key.main.key_id
  }

  tags = merge(
    var.tags,
    {
      Name       = "${var.key_alias}-deletion-alarm"
      control_id = "SEC-001"
      Component  = "Monitoring"
    }
  )
}

# Outputs
output "key_id" {
  description = "ID of the KMS key"
  value       = aws_kms_key.main.key_id
}

output "key_arn" {
  description = "ARN of the KMS key"
  value       = aws_kms_key.main.arn
}

output "key_alias" {
  description = "Alias of the KMS key"
  value       = aws_kms_alias.main.name
}

output "audit_metadata" {
  description = "Metadata for audit trail correlation"
  value = {
    module            = "kms"
    key_id            = aws_kms_key.main.key_id
    key_arn           = aws_kms_key.main.arn
    key_alias         = aws_kms_alias.main.name
    control_ids       = var.control_ids
    rotation_enabled  = var.enable_key_rotation
    deletion_window   = var.deletion_window_in_days
    created_at        = timestamp()
    jira_reference    = {
      cr_id    = var.jira_cr_id
      audit_id = var.audit_id
    }
    compliance        = {
      controls      = var.control_ids
      nist_controls = ["SC-12", "SC-13", "SC-28"]
      cci_controls  = ["CCI-002450", "CCI-002451"]
    }
  }
}

output "control_implementation" {
  description = "Control implementation details"
  value = {
    control_id          = "SC-028"
    control_family      = "System and Communications Protection"
    implementation_type = "AWS KMS"
    features            = {
      automatic_rotation = var.enable_key_rotation
      managed_service    = true
      fips_140_2_level_2 = true
    }
  }
}
