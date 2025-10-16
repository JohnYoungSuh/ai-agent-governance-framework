# Variables for AI Ops Agent Infrastructure

variable "aws_region" {
  description = "AWS region for agent infrastructure"
  type        = string
  default     = "us-east-1"
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

variable "agent_name" {
  description = "Name of the AI ops agent"
  type        = string
  default     = "ai-ops-agent"
}

variable "agent_tier" {
  description = "Agent tier (tier1-observer, tier2-developer, tier3-operations, tier4-architect)"
  type        = string
  default     = "tier3-operations"

  validation {
    condition     = contains(["tier1-observer", "tier2-developer", "tier3-operations", "tier4-architect"], var.agent_tier)
    error_message = "Agent tier must be one of: tier1-observer, tier2-developer, tier3-operations, tier4-architect"
  }
}

variable "llm_model_provider" {
  description = "LLM provider (anthropic, openai, bedrock)"
  type        = string
  default     = "anthropic"
}

variable "llm_model_version" {
  description = "LLM model version (pinned per MI-010)"
  type        = string
  default     = "claude-sonnet-4-5-20250929"
}

variable "daily_cost_budget" {
  description = "Daily cost budget in USD (MI-009, MI-021)"
  type        = number
  default     = 100.0
}

variable "monthly_cost_budget" {
  description = "Monthly cost budget in USD (MI-009, MI-021)"
  type        = number
  default     = 2000.0
}

variable "human_review_percentage" {
  description = "Percentage of outputs requiring human review (MI-007)"
  type        = number
  default     = 0.25 # 25% for Tier 3

  validation {
    condition     = var.human_review_percentage >= 0 && var.human_review_percentage <= 1
    error_message = "Human review percentage must be between 0 and 1"
  }
}

variable "enable_audit_trail" {
  description = "Enable comprehensive audit trails (MI-019)"
  type        = bool
  default     = true
}

variable "enable_observability" {
  description = "Enable OpenTelemetry observability (MI-004)"
  type        = bool
  default     = true
}

variable "github_repository" {
  description = "GitHub repository for agent operations"
  type        = string
}

variable "github_workflow_file" {
  description = "GitHub Actions workflow file name"
  type        = string
  default     = "ai-ops-agent.yml"
}

variable "vpc_id" {
  description = "VPC ID for agent infrastructure (optional for MI-008 sandboxing)"
  type        = string
  default     = ""
}

variable "allowed_actions" {
  description = "List of allowed actions for this agent tier"
  type        = list(string)
  default = [
    "read_data",
    "modify_dev",
    "deploy_staging",
    "deploy_prod"
  ]
}

variable "compliance_regulations" {
  description = "Applicable compliance regulations (MI-018)"
  type        = list(string)
  default     = ["GDPR", "SOX", "EU_AI_ACT"]
}

variable "risk_controls_required" {
  description = "Required risk control mitigations"
  type        = list(string)
  default = [
    "MI-001", # Data Leakage Prevention
    "MI-002", # Input Filtering
    "MI-003", # Secrets Management
    "MI-004", # Observability
    "MI-007", # Human Review
    "MI-009", # Cost Monitoring
    "MI-019", # Audit Trails
    "MI-020", # Tier Enforcement
    "MI-021"  # Budget Limits
  ]
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "enable_pii_redaction" {
  description = "Enable PII redaction using Presidio (MI-001)"
  type        = bool
  default     = true
}

variable "enable_secrets_scanning" {
  description = "Enable secrets scanning (MI-003)"
  type        = bool
  default     = true
}

variable "enable_prompt_injection_detection" {
  description = "Enable prompt injection detection (MI-002)"
  type        = bool
  default     = true
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  sensitive   = true
  default     = ""
}

variable "jira_api_url" {
  description = "JIRA API URL for issue tracking"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
