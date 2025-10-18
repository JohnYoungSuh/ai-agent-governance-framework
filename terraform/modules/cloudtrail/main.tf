# CloudTrail Module
# AI Agent Governance Framework v2.1
# Control: AU-002 (Audit Logging), G-07 (Audit Trail), SEC-002 (Logging)

variable "trail_name" {
  description = "Name of the CloudTrail trail"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name for CloudTrail logs"
  type        = string
}

variable "enable_log_file_validation" {
  description = "Enable log file integrity validation"
  type        = bool
  default     = true
}

variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch Logs integration"
  type        = bool
  default     = true
}

variable "cloudwatch_log_group_name" {
  description = "CloudWatch log group name"
  type        = string
  default     = ""
}

variable "kms_key_id" {
  description = "KMS key ID for encrypting CloudTrail logs"
  type        = string
}

variable "control_ids" {
  description = "Governance control IDs"
  type        = list(string)
  default     = ["AU-002", "G-07", "SEC-002"]
}

variable "agent_tier" {
  description = "Agent tier (tier1-observer, tier2-developer, tier3-operations, tier4-architect)"
  type        = string
}

variable "jira_cr_id" {
  description = "Jira Change Request ID for audit correlation"
  type        = string
  default     = ""
}

variable "audit_id" {
  description = "Audit trail ID for correlation"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# CloudWatch Log Group for CloudTrail
resource "aws_cloudwatch_log_group" "cloudtrail" {
  count = var.enable_cloudwatch_logs ? 1 : 0

  name              = var.cloudwatch_log_group_name != "" ? var.cloudwatch_log_group_name : "/aws/cloudtrail/${var.trail_name}"
  retention_in_days = 90
  kms_key_id        = var.kms_key_id

  tags = merge(
    var.tags,
    {
      Name       = "${var.trail_name}-logs"
      control_id = join(",", var.control_ids)
      Component  = "CloudWatch"
      jira_cr_id = var.jira_cr_id
      audit_id   = var.audit_id
    }
  )
}

# IAM role for CloudTrail to CloudWatch Logs
resource "aws_iam_role" "cloudtrail_cloudwatch" {
  count = var.enable_cloudwatch_logs ? 1 : 0

  name = "${var.trail_name}-cloudwatch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name       = "${var.trail_name}-cloudwatch-role"
      control_id = join(",", var.control_ids)
      Component  = "IAM"
    }
  )
}

# IAM policy for CloudTrail to write to CloudWatch Logs
resource "aws_iam_role_policy" "cloudtrail_cloudwatch" {
  count = var.enable_cloudwatch_logs ? 1 : 0

  name = "${var.trail_name}-cloudwatch-policy"
  role = aws_iam_role.cloudtrail_cloudwatch[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CreateLogStream"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.cloudtrail[0].arn}:*"
      }
    ]
  })
}

# CloudTrail
resource "aws_cloudtrail" "main" {
  name                          = var.trail_name
  s3_bucket_name                = var.s3_bucket_name
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = var.enable_log_file_validation
  kms_key_id                    = var.kms_key_id

  dynamic "event_selector" {
    for_each = [1]
    content {
      read_write_type           = "All"
      include_management_events = true

      # Log data events for AI agent related resources
      data_resource {
        type = "AWS::S3::Object"
        values = ["arn:aws:s3:::*/ai-agent/*"]
      }

      data_resource {
        type = "AWS::Lambda::Function"
        values = ["arn:aws:lambda:*:*:function:ai-agent-*"]
      }
    }
  }

  # Advanced event selectors for fine-grained logging
  advanced_event_selector {
    name = "AI Agent Secrets Access"

    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }

    field_selector {
      field  = "resources.type"
      equals = ["AWS::SecretsManager::Secret"]
    }

    field_selector {
      field       = "resources.ARN"
      starts_with = ["arn:aws:secretsmanager"]
    }
  }

  advanced_event_selector {
    name = "AI Agent IAM Changes"

    field_selector {
      field  = "eventCategory"
      equals = ["Management"]
    }

    field_selector {
      field  = "eventSource"
      equals = ["iam.amazonaws.com"]
    }

    field_selector {
      field       = "eventName"
      starts_with = ["Create", "Delete", "Update", "Put", "Attach", "Detach"]
    }
  }

  # CloudWatch Logs integration
  cloud_watch_logs_group_arn = var.enable_cloudwatch_logs ? "${aws_cloudwatch_log_group.cloudtrail[0].arn}:*" : null
  cloud_watch_logs_role_arn  = var.enable_cloudwatch_logs ? aws_iam_role.cloudtrail_cloudwatch[0].arn : null

  tags = merge(
    var.tags,
    {
      Name       = var.trail_name
      control_id = join(",", var.control_ids)
      AgentTier  = var.agent_tier
      Component  = "CloudTrail"
      jira_cr_id = var.jira_cr_id
      audit_id   = var.audit_id
      Framework  = "AI-Agent-Governance-v2.1"
    }
  )

  depends_on = [
    aws_iam_role_policy.cloudtrail_cloudwatch
  ]
}

# CloudWatch metric filter for failed API calls
resource "aws_cloudwatch_log_metric_filter" "failed_api_calls" {
  count = var.enable_cloudwatch_logs ? 1 : 0

  name           = "${var.trail_name}-failed-api-calls"
  log_group_name = aws_cloudwatch_log_group.cloudtrail[0].name
  pattern        = "{ ($.errorCode = \"*UnauthorizedOperation\") || ($.errorCode = \"AccessDenied*\") }"

  metric_transformation {
    name      = "FailedAPICalls"
    namespace = "AI-Agent-Governance/CloudTrail"
    value     = "1"
    default_value = 0
  }
}

# Alarm for unauthorized access attempts
resource "aws_cloudwatch_metric_alarm" "unauthorized_api_calls" {
  count = var.enable_cloudwatch_logs ? 1 : 0

  alarm_name          = "${var.trail_name}-unauthorized-access"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FailedAPICalls"
  namespace           = "AI-Agent-Governance/CloudTrail"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Alert on multiple unauthorized access attempts"
  treat_missing_data  = "notBreaching"

  tags = merge(
    var.tags,
    {
      Name       = "${var.trail_name}-unauthorized-alarm"
      control_id = "SEC-002"
      Component  = "Monitoring"
    }
  )
}

# Outputs
output "trail_arn" {
  description = "ARN of the CloudTrail trail"
  value       = aws_cloudtrail.main.arn
}

output "trail_name" {
  description = "Name of the CloudTrail trail"
  value       = aws_cloudtrail.main.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = var.enable_cloudwatch_logs ? aws_cloudwatch_log_group.cloudtrail[0].arn : null
}

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = var.enable_cloudwatch_logs ? aws_cloudwatch_log_group.cloudtrail[0].name : null
}

output "audit_metadata" {
  description = "Metadata for audit trail correlation"
  value = {
    module              = "cloudtrail"
    trail_arn           = aws_cloudtrail.main.arn
    trail_name          = aws_cloudtrail.main.name
    control_ids         = var.control_ids
    log_validation      = var.enable_log_file_validation
    cloudwatch_enabled  = var.enable_cloudwatch_logs
    kms_encrypted       = true
    multi_region        = true
    created_at          = timestamp()
    jira_reference      = {
      cr_id    = var.jira_cr_id
      audit_id = var.audit_id
    }
    compliance          = {
      controls     = var.control_ids
      agent_tier   = var.agent_tier
      nist_controls = ["AU-2", "AU-3", "AU-6", "AU-9", "AU-12"]
      cci_controls  = ["CCI-000130", "CCI-000131", "CCI-000132", "CCI-000133", "CCI-001464"]
    }
  }
}

output "control_implementation" {
  description = "Control implementation details"
  value = {
    control_id          = "AU-002"
    control_family      = "Audit and Accountability"
    implementation_type = "AWS CloudTrail + CloudWatch Logs"
    features            = {
      log_file_validation = var.enable_log_file_validation
      kms_encryption      = true
      multi_region        = true
      cloudwatch_logs     = var.enable_cloudwatch_logs
      data_events         = true
      management_events   = true
    }
  }
}
