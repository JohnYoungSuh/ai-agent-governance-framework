# S3 Audit Logs Module
# AI Agent Governance Framework v2.1
# Control: AU-002, SEC-002, G-07

variable "bucket_name" {
  description = "Name of the S3 bucket for audit logs"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for bucket encryption"
  type        = string
}

variable "lifecycle_glacier_days" {
  description = "Days before transitioning to Glacier"
  type        = number
  default     = 90
}

variable "lifecycle_expiration_days" {
  description = "Days before log expiration"
  type        = number
  default     = 2555  # 7 years for compliance
}

variable "control_ids" {
  description = "Governance control IDs"
  type        = list(string)
  default     = ["AU-002", "SEC-002", "G-07"]
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

# S3 bucket for audit logs
resource "aws_s3_bucket" "audit_logs" {
  bucket = var.bucket_name

  tags = merge(
    var.tags,
    {
      Name       = var.bucket_name
      control_id = join(",", var.control_ids)
      Component  = "S3"
      Purpose    = "AuditLogs"
      jira_cr_id = var.jira_cr_id
      audit_id   = var.audit_id
      Framework  = "AI-Agent-Governance-v2.1"
    }
  )
}

# Enable versioning for audit integrity
resource "aws_s3_bucket_versioning" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = true
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy
resource "aws_s3_bucket_lifecycle_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    transition {
      days          = var.lifecycle_glacier_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.lifecycle_expiration_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# Bucket policy for CloudTrail
resource "aws_s3_bucket_policy" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.audit_logs.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.audit_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      },
      {
        Sid    = "DenyUnencryptedObjectUploads"
        Effect = "Deny"
        Principal = "*"
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.audit_logs.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption" = "aws:kms"
          }
        }
      },
      {
        Sid    = "DenyInsecureTransport"
        Effect = "Deny"
        Principal = "*"
        Action   = "s3:*"
        Resource = [
          aws_s3_bucket.audit_logs.arn,
          "${aws_s3_bucket.audit_logs.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

# Enable access logging
resource "aws_s3_bucket_logging" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  target_bucket = aws_s3_bucket.audit_logs.id
  target_prefix = "access-logs/"
}

# Object lock for compliance
resource "aws_s3_bucket_object_lock_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    default_retention {
      mode = "GOVERNANCE"
      days = 365
    }
  }
}

# Outputs
output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.audit_logs.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.audit_logs.arn
}

output "audit_metadata" {
  description = "Metadata for audit trail correlation"
  value = {
    module               = "s3_audit_logs"
    bucket_name          = aws_s3_bucket.audit_logs.id
    bucket_arn           = aws_s3_bucket.audit_logs.arn
    control_ids          = var.control_ids
    versioning_enabled   = true
    kms_encrypted        = true
    public_access_blocked = true
    lifecycle_glacier_days = var.lifecycle_glacier_days
    retention_days       = var.lifecycle_expiration_days
    created_at           = timestamp()
    jira_reference       = {
      cr_id    = var.jira_cr_id
      audit_id = var.audit_id
    }
    compliance           = {
      controls      = var.control_ids
      nist_controls = ["AU-9", "AU-11"]
      cci_controls  = ["CCI-001348", "CCI-001350"]
    }
  }
}
