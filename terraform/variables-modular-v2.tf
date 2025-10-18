# Variables for Modular Terraform Configuration
# AI Agent Governance Framework v2.1

# ============================================================================
# General Configuration
# ============================================================================

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "github_organization" {
  description = "GitHub organization name"
  type        = string
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

# ============================================================================
# Audit and Compliance
# ============================================================================

variable "jira_cr_id" {
  description = "Jira Change Request ID for audit correlation (required for staging/prod)"
  type        = string
  default     = ""
  validation {
    condition     = var.environment == "dev" || (var.environment != "dev" && can(regex("^CR-[0-9]{4}-[0-9]+$", var.jira_cr_id)))
    error_message = "Jira CR ID is required for staging/prod and must match pattern CR-YYYY-NNNN."
  }
}

variable "audit_id" {
  description = "Audit trail ID for this deployment"
  type        = string
  default     = ""
}

variable "deployed_by" {
  description = "User or system deploying this configuration"
  type        = string
  default     = "terraform-automation"
}

# ============================================================================
# Audit Log Retention
# ============================================================================

variable "audit_log_glacier_days" {
  description = "Days before transitioning audit logs to Glacier"
  type        = number
  default     = 90
}

variable "audit_log_retention_days" {
  description = "Days to retain audit logs before deletion"
  type        = number
  default     = 2555  # 7 years for compliance
  validation {
    condition     = var.audit_log_retention_days >= 365
    error_message = "Audit log retention must be at least 365 days for compliance."
  }
}

# ============================================================================
# Secrets (Sensitive Values)
# ============================================================================

variable "jira_api_token" {
  description = "Jira API token for CR validation"
  type        = string
  sensitive   = true
  default     = "placeholder-will-be-set-via-secrets"
}

variable "github_token_secret" {
  description = "GitHub token for repository access"
  type        = string
  sensitive   = true
  default     = "placeholder-will-be-set-via-secrets"
}

variable "openai_api_key" {
  description = "OpenAI API key for LLM operations"
  type        = string
  sensitive   = true
  default     = "placeholder-will-be-set-via-secrets"
}

variable "aws_ops_credentials" {
  description = "AWS credentials for ops agent"
  type        = string
  sensitive   = true
  default     = "placeholder-will-be-set-via-secrets"
}

variable "kubectl_config" {
  description = "Kubernetes cluster configuration"
  type        = string
  sensitive   = true
  default     = "placeholder-will-be-set-via-secrets"
}

# ============================================================================
# Feature Flags
# ============================================================================

variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch Logs integration for CloudTrail"
  type        = bool
  default     = true
}

variable "enable_secrets_rotation" {
  description = "Enable automatic secrets rotation"
  type        = bool
  default     = false  # Requires Lambda function setup
}

# ============================================================================
# Control IDs for Tagging
# ============================================================================

variable "control_tags" {
  description = "Map of resources to their control IDs"
  type        = map(list(string))
  default = {
    "kms"             = ["SC-028", "SEC-001"]
    "secrets_manager" = ["SEC-001", "MI-003", "IA-005"]
    "cloudtrail"      = ["AU-002", "AU-003", "AU-006", "G-07", "SEC-002"]
    "s3_audit_logs"   = ["AU-002", "AU-009", "G-07"]
  }
}
