# DynamoDB Audit Trail Module
# Control: MI-019 (Audit Trails)
# Purpose: Immutable audit trail storage for agent actions

variable "agent_id" {
  description = "Agent identifier"
  type        = string
}

variable "agent_tier" {
  description = "Agent tier"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN for encryption"
  type        = string
}

variable "point_in_time_recovery" {
  description = "Enable point-in-time recovery"
  type        = bool
  default     = true
}

variable "ttl_enabled" {
  description = "Enable TTL for hot storage (archive to S3 after 90 days)"
  type        = bool
  default     = true
}

variable "control_id" {
  description = "Governance control IDs"
  type        = list(string)
  default     = ["MI-019"]
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# DynamoDB table for audit trail
resource "aws_dynamodb_table" "audit_trail" {
  name           = "${var.agent_id}-audit-trail"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "audit_id"
  range_key      = "timestamp"

  attribute {
    name = "audit_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "actor"
    type = "S"
  }

  attribute {
    name = "action"
    type = "S"
  }

  attribute {
    name = "compliance_result"
    type = "S"
  }

  # GSI for querying by actor
  global_secondary_index {
    name            = "ActorIndex"
    hash_key        = "actor"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # GSI for querying by action type
  global_secondary_index {
    name            = "ActionIndex"
    hash_key        = "action"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # GSI for compliance reporting
  global_secondary_index {
    name            = "ComplianceIndex"
    hash_key        = "compliance_result"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  # Enable server-side encryption with KMS
  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  # Enable TTL for hot storage lifecycle
  dynamic "ttl" {
    for_each = var.ttl_enabled ? [1] : []
    content {
      attribute_name = "archive_after"
      enabled        = true
    }
  }

  # Enable streams for real-time SIEM integration
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-audit-trail"
      AgentID   = var.agent_id
      AgentTier = var.agent_tier
      ControlID = join(",", var.control_id)
      Purpose   = "Audit trail storage - 90 days hot, 7 years archive"
      ManagedBy = "Terraform"
      Framework = "AI-Agent-Governance-v2.0"
    }
  )
}

# S3 bucket for long-term archive (7 years)
resource "aws_s3_bucket" "audit_archive" {
  bucket = "${var.agent_id}-audit-archive-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_id}-audit-archive"
      AgentID   = var.agent_id
      AgentTier = var.agent_tier
      ControlID = join(",", var.control_id)
      Purpose   = "7-year audit trail archive"
      ManagedBy = "Terraform"
      Framework = "AI-Agent-Governance-v2.0"
    }
  )
}

# Enable versioning for immutability
resource "aws_s3_bucket_versioning" "audit_archive" {
  bucket = aws_s3_bucket.audit_archive.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "audit_archive" {
  bucket = aws_s3_bucket.audit_archive.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "audit_archive" {
  bucket = aws_s3_bucket.audit_archive.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy: Archive to Glacier Deep Archive after 90 days
resource "aws_s3_bucket_lifecycle_configuration" "audit_archive" {
  bucket = aws_s3_bucket.audit_archive.id

  rule {
    id     = "archive-to-glacier"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER_IR"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = 2555  # 7 years
    }
  }
}

# Data source
data "aws_caller_identity" "current" {}

# Outputs
output "table_name" {
  description = "DynamoDB audit trail table name"
  value       = aws_dynamodb_table.audit_trail.name
}

output "table_arn" {
  description = "DynamoDB audit trail table ARN"
  value       = aws_dynamodb_table.audit_trail.arn
}

output "table_stream_arn" {
  description = "DynamoDB stream ARN for SIEM integration"
  value       = aws_dynamodb_table.audit_trail.stream_arn
}

output "archive_bucket_name" {
  description = "S3 archive bucket name"
  value       = aws_s3_bucket.audit_archive.id
}

output "archive_bucket_arn" {
  description = "S3 archive bucket ARN"
  value       = aws_s3_bucket.audit_archive.arn
}
