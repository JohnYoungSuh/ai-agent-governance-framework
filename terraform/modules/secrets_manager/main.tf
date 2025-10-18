# Secrets Manager Module
# Control: SEC-001, MI-003
# Purpose: Secure credential storage for AI agents

variable "agent_id" {
  description = "Agent identifier"
  type        = string
}

variable "agent_tier" {
  description = "Agent tier (tier1-observer, tier2-developer, tier3-operations, tier4-architect)"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

variable "secrets" {
  description = "Map of secrets to create"
  type = map(object({
    description = string
    value       = string
  }))
}

variable "control_id" {
  description = "Governance control IDs this module implements"
  type        = list(string)
  default     = ["SEC-001", "MI-003"]
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# Secrets Manager secrets
resource "aws_secretsmanager_secret" "agent_secrets" {
  for_each = var.secrets

  name        = "${var.agent_id}/${each.key}"
  description = each.value.description
  kms_key_id  = var.kms_key_id

  tags = merge(
    var.tags,
    {
      Name       = "${var.agent_id}/${each.key}"
      AgentID    = var.agent_id
      AgentTier  = var.agent_tier
      ControlID  = join(",", var.control_id)
      ManagedBy  = "Terraform"
      Framework  = "AI-Agent-Governance-v2.0"
    }
  )
}

resource "aws_secretsmanager_secret_version" "agent_secrets" {
  for_each = var.secrets

  secret_id     = aws_secretsmanager_secret.agent_secrets[each.key].id
  secret_string = each.value.value
}

# IAM policy for secret access (least-privilege)
data "aws_iam_policy_document" "secret_access" {
  statement {
    sid    = "AllowAgentSecretAccess"
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      for secret in aws_secretsmanager_secret.agent_secrets :
      secret.arn
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:PrincipalTag/AgentID"
      values   = [var.agent_id]
    }
  }

  statement {
    sid    = "AllowKMSDecrypt"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey"
    ]
    resources = [var.kms_key_id]
  }
}

# Outputs
output "secret_arns" {
  description = "ARNs of created secrets"
  value = {
    for key, secret in aws_secretsmanager_secret.agent_secrets :
    key => secret.arn
  }
}

output "secret_names" {
  description = "Names of created secrets"
  value = {
    for key, secret in aws_secretsmanager_secret.agent_secrets :
    key => secret.name
  }
}

output "iam_policy_json" {
  description = "IAM policy document for secret access"
  value       = data.aws_iam_policy_document.secret_access.json
}

# G-03: Control Implementation Outputs
output "control_implementation" {
  description = "Control implementation details for SEC-001 (G-03)"
  value = {
    control_id          = "SEC-001"
    control_family      = "Secrets Management"
    nist_controls       = ["SC-28", "IA-5"]
    cci_controls        = ["CCI-001199", "CCI-000196"]
    aws_resources       = [for s in aws_secretsmanager_secret.agent_secrets : s.arn]
    implementation_type = "AWS Secrets Manager + KMS"
    kms_encrypted       = true
    least_privilege     = true
    agent_id            = var.agent_id
    agent_tier          = var.agent_tier
  }
}

output "audit_metadata" {
  description = "Metadata for audit trail correlation"
  value = {
    module           = "secrets_manager"
    control_ids      = var.control_id
    resources_count  = length(aws_secretsmanager_secret.agent_secrets)
    kms_key_id       = var.kms_key_id
    created_at       = timestamp()
  }
}
