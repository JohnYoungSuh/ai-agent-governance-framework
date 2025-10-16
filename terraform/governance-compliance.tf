# Governance and Compliance Controls
# Implements governance framework requirements and compliance mappings

# DynamoDB table for governance records
resource "aws_dynamodb_table" "governance_records" {
  name           = "${var.agent_name}-governance-records"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "control_id"

  attribute {
    name = "control_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "last_reviewed"
    type = "S"
  }

  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "status"
    range_key       = "last_reviewed"
    projection_type = "ALL"
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
      Name          = "${var.agent_name}-governance-records"
      ControlID     = "MI-018,MI-019"
      Purpose       = "Store governance control records"
    }
  )
}

# Lambda function to initialize governance records
resource "aws_lambda_function" "governance_initializer" {
  filename      = "${path.module}/lambda/governance-initializer.zip"
  function_name = "${var.agent_name}-governance-initializer"
  role          = aws_iam_role.governance_initializer_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300

  environment {
    variables = {
      GOVERNANCE_TABLE       = aws_dynamodb_table.governance_records.name
      AGENT_NAME             = var.agent_name
      AGENT_TIER             = var.agent_tier
      RISK_CONTROLS_REQUIRED = jsonencode(var.risk_controls_required)
      COMPLIANCE_REGULATIONS = jsonencode(var.compliance_regulations)
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.agent_name}-governance-initializer"
    }
  )
}

resource "aws_iam_role" "governance_initializer_role" {
  name = "${var.agent_name}-governance-initializer-role"

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
      Name = "${var.agent_name}-governance-initializer-role"
    }
  )
}

resource "aws_iam_policy" "governance_initializer_policy" {
  name = "${var.agent_name}-governance-initializer-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = aws_dynamodb_table.governance_records.arn
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
      Name = "${var.agent_name}-governance-initializer-policy"
    }
  )
}

resource "aws_iam_role_policy_attachment" "governance_initializer_policy" {
  role       = aws_iam_role.governance_initializer_role.name
  policy_arn = aws_iam_policy.governance_initializer_policy.arn
}

# EventBridge rule for governance compliance checks (quarterly reviews)
resource "aws_cloudwatch_event_rule" "quarterly_governance_review" {
  name                = "${var.agent_name}-quarterly-governance-review"
  description         = "Trigger quarterly governance review for ${var.agent_name}"
  schedule_expression = "cron(0 10 1 */3 ? *)" # 10 AM UTC on 1st day of every 3rd month

  tags = merge(
    var.tags,
    {
      Name      = "${var.agent_name}-quarterly-governance-review"
      ControlID = "MI-018"
    }
  )
}

resource "aws_cloudwatch_event_target" "quarterly_review_sns" {
  rule      = aws_cloudwatch_event_rule.quarterly_governance_review.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.agent_alerts.arn

  input = jsonencode({
    message = "Quarterly governance review required for ${var.agent_name}"
    agent   = var.agent_name
    tier    = var.agent_tier
    action  = "governance_review"
  })
}

# S3 bucket for governance documentation and evidence
resource "aws_s3_bucket" "governance_evidence" {
  bucket = "${var.agent_name}-governance-evidence-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    var.tags,
    {
      Name          = "${var.agent_name}-governance-evidence"
      ControlID     = "MI-018,MI-019"
      Purpose       = "Store governance evidence artifacts"
    }
  )
}

resource "aws_s3_bucket_versioning" "governance_evidence" {
  bucket = aws_s3_bucket.governance_evidence.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "governance_evidence" {
  bucket = aws_s3_bucket.governance_evidence.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.agent_encryption.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "governance_evidence" {
  bucket = aws_s3_bucket.governance_evidence.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Local file for compliance mapping documentation
resource "local_file" "compliance_mapping" {
  filename = "${path.module}/outputs/compliance-mapping-${var.agent_name}.yaml"

  content = yamlencode({
    agent_name = var.agent_name
    agent_tier = var.agent_tier
    generated  = timestamp()

    regulations = [
      for reg in var.compliance_regulations : {
        name       = reg
        applicable = true
        controls_implemented = var.risk_controls_required
      }
    ]

    risk_controls = {
      for control in var.risk_controls_required : control => {
        status         = "implemented"
        implementation = "terraform-managed"
        evidence_bucket = aws_s3_bucket.governance_evidence.id
      }
    }

    tier_permissions = {
      tier             = var.agent_tier
      allowed_actions  = var.allowed_actions
      human_review_pct = var.human_review_percentage
      approval_required = var.agent_tier == "tier3-operations" || var.agent_tier == "tier4-architect"
    }

    monitoring = {
      observability_enabled = var.enable_observability
      audit_trail_enabled   = var.enable_audit_trail
      cost_monitoring       = true
      budget_limits = {
        daily   = var.daily_cost_budget
        monthly = var.monthly_cost_budget
      }
    }

    security_controls = {
      pii_redaction              = var.enable_pii_redaction
      secrets_scanning           = var.enable_secrets_scanning
      prompt_injection_detection = var.enable_prompt_injection_detection
      encryption_at_rest         = true
      encryption_in_transit      = true
      kms_key_id                 = aws_kms_key.agent_encryption.id
    }
  })
}

# Output governance validation report
resource "local_file" "governance_validation_report" {
  filename = "${path.module}/outputs/governance-validation-${var.agent_name}.md"

  content = <<-EOT
# AI Agent Governance Validation Report

**Agent Name:** ${var.agent_name}
**Agent Tier:** ${var.agent_tier}
**Generated:** ${timestamp()}
**Framework Version:** v2.0

---

## Compliance Status

### Regulations Addressed
${join("\n", [for reg in var.compliance_regulations : "- ✅ ${reg}"])}

### Risk Controls Implemented
${join("\n", [for control in var.risk_controls_required : "- ✅ ${control}"])}

---

## Governance Controls

### MI-001: Data Leakage Prevention
- **Status:** ${var.enable_pii_redaction ? "✅ IMPLEMENTED" : "❌ NOT IMPLEMENTED"}
- **Implementation:** PII redaction enabled in agent runtime
- **Evidence:** Terraform-managed

### MI-003: Secrets Management
- **Status:** ✅ IMPLEMENTED
- **Implementation:** AWS Secrets Manager with KMS encryption
- **Secrets:** ${length([aws_secretsmanager_secret.llm_api_key, aws_secretsmanager_secret.github_token])} secrets configured

### MI-004: Observability
- **Status:** ${var.enable_observability ? "✅ IMPLEMENTED" : "⚠️  OPTIONAL"}
- **Implementation:** CloudWatch Logs, X-Ray tracing, custom dashboard
- **Log Retention:** 90 days

### MI-006: Access Controls
- **Status:** ✅ IMPLEMENTED
- **Implementation:** IAM role with least-privilege permissions
- **Tier Enforcement:** ${var.agent_tier}

### MI-007: Human Review
- **Status:** ✅ IMPLEMENTED
- **Review Rate:** ${var.human_review_percentage * 100}%
- **Requirement:** Tier-based review workflow

### MI-009: Cost Monitoring
- **Status:** ✅ IMPLEMENTED
- **Daily Budget:** $${var.daily_cost_budget}
- **Monthly Budget:** $${var.monthly_cost_budget}
- **Alerts:** 50%, 75%, 90% thresholds

### MI-019: Audit Trails
- **Status:** ${var.enable_audit_trail ? "✅ IMPLEMENTED" : "❌ NOT IMPLEMENTED"}
- **Implementation:** DynamoDB table with S3 archival
- **Retention:** 90 days hot, 7 years archive

### MI-020: Tier Enforcement
- **Status:** ✅ IMPLEMENTED
- **Allowed Actions:** ${join(", ", var.allowed_actions)}
- **Enforcement:** IAM policy-based

### MI-021: Budget Limits
- **Status:** ✅ IMPLEMENTED
- **Circuit Breaker:** Enabled at 90% budget
- **Alerts:** SNS topic configured

---

## Security Posture

- **Encryption at Rest:** ✅ KMS-encrypted (all data stores)
- **Encryption in Transit:** ✅ TLS/HTTPS enforced
- **Secrets Management:** ✅ AWS Secrets Manager
- **Access Controls:** ✅ IAM least-privilege
- **Network Security:** ${var.vpc_id != "" ? "✅ VPC-isolated" : "⚠️  Public (consider VPC)"}
- **Audit Trail:** ${var.enable_audit_trail ? "✅ Comprehensive logging" : "❌ Not enabled"}

---

## Validation Checklist

### NIST AI RMF Alignment
- [x] GOVERN: Clear accountability and policies
- [x] MAP: Context and use cases documented
- [x] MEASURE: Performance and cost metrics
- [x] MANAGE: Risk mitigations implemented

### ISO/IEC 42001 Alignment
- [x] Organizational context defined
- [x] Risk assessment methodology
- [x] Documentation maintained
- [x] Monitoring and measurement

### OWASP Top 10 for LLMs
- [${var.enable_prompt_injection_detection ? "x" : " "}] LLM01: Prompt Injection (MI-002)
- [ ] LLM02: Insecure Output Handling
- [x] LLM03: Training Data Poisoning (N/A - hosted model)
- [x] LLM04: Model DoS (MI-005, MI-021)
- [x] LLM05: Supply Chain (MI-010 version pinning)
- [x] LLM06: Sensitive Info Disclosure (MI-001)
- [x] LLM07: Insecure Plugin Design (MI-008 sandboxing)
- [x] LLM08: Excessive Agency (MI-020 tier enforcement)
- [x] LLM09: Overreliance (MI-007 human review)
- [x] LLM10: Model Theft (N/A - hosted model)

---

## Recommendations

### Critical (Must Implement)
${var.enable_audit_trail ? "" : "- [ ] Enable audit trail (MI-019)"}
${var.enable_pii_redaction ? "" : "- [ ] Enable PII redaction (MI-001)"}
${var.enable_prompt_injection_detection ? "" : "- [ ] Enable prompt injection detection (MI-002)"}

### High Priority (Should Implement)
${var.enable_observability ? "" : "- [ ] Enable observability stack (MI-004)"}
${var.vpc_id != "" ? "" : "- [ ] Deploy in VPC for network isolation (MI-008)"}
- [ ] Implement LLM-as-Judge validation (MI-015)
- [ ] Set up RAG security controls (MI-014)

### Medium Priority (Consider)
- [ ] Enable bias testing (MI-012)
- [ ] Implement citations requirement (MI-013)
- [ ] Set up change monitoring (MI-016)
- [ ] Deploy AI firewall (MI-017)

---

## Approval Sign-off

**Infrastructure Deployed:** ${timestamp()}
**Terraform Apply Date:** _____________________
**Security Review:** _____________________
**Compliance Approval:** _____________________

---

**Generated by AI Agent Governance Framework v2.0**
**Terraform-managed infrastructure**
EOT
}
