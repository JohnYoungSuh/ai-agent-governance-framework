# Audit Trail Infrastructure
# Implements: MI-019 (Audit Trails)
# Addresses: RI-007 (Insufficient Audit Trail), RI-016 (Compliance)

# DynamoDB table for audit trail storage
resource "aws_dynamodb_table" "audit_trail" {
  count = var.enable_audit_trail ? 1 : 0

  name           = "${var.agent_name}-audit-trail"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "audit_id"
  range_key      = "timestamp"
  stream_enabled = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

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

  # GSI for querying by action
  global_secondary_index {
    name            = "ActionIndex"
    hash_key        = "action"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # GSI for querying compliance failures
  global_secondary_index {
    name            = "ComplianceIndex"
    hash_key        = "compliance_result"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.agent_encryption.arn
  }

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-audit-trail"
      ControlID     = "MI-019"
      RiskAddresses = "RI-007,RI-016"
      Retention     = "90-days-hot,1-year-cold"
      Compliance    = join(",", var.compliance_regulations)
    }
  )
}

# S3 bucket for long-term audit trail archival
resource "aws_s3_bucket" "audit_archive" {
  count = var.enable_audit_trail ? 1 : 0

  bucket = "${var.agent_name}-audit-archive-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-audit-archive"
      ControlID     = "MI-019"
      Purpose       = "Long-term audit trail storage (1+ years)"
    }
  )
}

resource "aws_s3_bucket_versioning" "audit_archive" {
  count = var.enable_audit_trail ? 1 : 0

  bucket = aws_s3_bucket.audit_archive[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit_archive" {
  count = var.enable_audit_trail ? 1 : 0

  bucket = aws_s3_bucket.audit_archive[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.agent_encryption.arn
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "audit_archive" {
  count = var.enable_audit_trail ? 1 : 0

  bucket = aws_s3_bucket.audit_archive[0].id

  rule {
    id     = "archive-old-audits"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = 2555 # 7 years (SOX requirement)
    }
  }
}

resource "aws_s3_bucket_public_access_block" "audit_archive" {
  count = var.enable_audit_trail ? 1 : 0

  bucket = aws_s3_bucket.audit_archive[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lambda function for DynamoDB Stream to S3 archival
resource "aws_lambda_function" "audit_archiver" {
  count = var.enable_audit_trail ? 1 : 0

  filename      = "${path.module}/lambda/audit-archiver.zip"
  function_name = "${var.agent_name}-audit-archiver"
  role          = aws_iam_role.audit_archiver_role[0].arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 60

  environment {
    variables = {
      ARCHIVE_BUCKET = aws_s3_bucket.audit_archive[0].id
      AGENT_NAME     = var.agent_name
    }
  }

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-audit-archiver"
      ControlID = "MI-019"
    }
  )
}

resource "aws_iam_role" "audit_archiver_role" {
  count = var.enable_audit_trail ? 1 : 0

  name = "${var.agent_name}-audit-archiver-role"

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
    var.tags,
    {
      Name = "${var.agent_name}-audit-archiver-role"
    }
  )
}

resource "aws_iam_policy" "audit_archiver_policy" {
  count = var.enable_audit_trail ? 1 : 0

  name = "${var.agent_name}-audit-archiver-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DescribeStream",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:ListStreams"
        ]
        Resource = "${aws_dynamodb_table.audit_trail[0].arn}/stream/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${aws_s3_bucket.audit_archive[0].arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.agent_name}-audit-archiver-policy"
    }
  )
}

resource "aws_iam_role_policy_attachment" "audit_archiver_policy" {
  count = var.enable_audit_trail ? 1 : 0

  role       = aws_iam_role.audit_archiver_role[0].name
  policy_arn = aws_iam_policy.audit_archiver_policy[0].arn
}

resource "aws_lambda_event_source_mapping" "audit_stream" {
  count = var.enable_audit_trail ? 1 : 0

  event_source_arn  = aws_dynamodb_table.audit_trail[0].stream_arn
  function_name     = aws_lambda_function.audit_archiver[0].arn
  starting_position = "LATEST"
  batch_size        = 100
}
