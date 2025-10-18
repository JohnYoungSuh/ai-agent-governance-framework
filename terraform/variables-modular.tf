# Variables for Modular Terraform Configuration
# AI Agent Governance Framework v2.0

# ============================================================================
# Required Variables
# ============================================================================

variable "agent_name" {
  description = "Name of the AI agent (e.g., security-agent, ops-agent)"
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.agent_name))
    error_message = "Agent name must be lowercase alphanumeric with hyphens, 3-30 characters"
  }
}

variable "llm_api_key" {
  description = "LLM API key (Anthropic, OpenAI, etc.)"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token for CI/CD"
  type        = string
  sensitive   = true
}

# ============================================================================
# Agent Configuration
# ============================================================================

variable "agent_tier" {
  description = "Agent tier determines permissions and governance rigor"
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

  validation {
    condition     = contains(["anthropic", "openai", "bedrock"], var.llm_model_provider)
    error_message = "LLM provider must be one of: anthropic, openai, bedrock"
  }
}

variable "llm_model_version" {
  description = "LLM model version (pinned per MI-010)"
  type        = string
  default     = "claude-sonnet-4-5-20250929"
}

# ============================================================================
# AWS Configuration
# ============================================================================

variable "aws_region" {
  description = "AWS region for agent infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production"
  }
}

# ============================================================================
# Cost Controls (MI-009, MI-021)
# ============================================================================

variable "daily_cost_budget" {
  description = "Daily cost budget in USD (MI-009, MI-021)"
  type        = number
  default     = 100.0

  validation {
    condition     = var.daily_cost_budget > 0
    error_message = "Daily cost budget must be greater than 0"
  }
}

variable "monthly_cost_budget" {
  description = "Monthly cost budget in USD (MI-009, MI-021)"
  type        = number
  default     = 2000.0

  validation {
    condition     = var.monthly_cost_budget > 0
    error_message = "Monthly cost budget must be greater than 0"
  }
}

variable "alert_email" {
  description = "Email address for cost and operational alerts"
  type        = string
  default     = ""
}

# ============================================================================
# Security Controls
# ============================================================================

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

# ============================================================================
# Governance Controls
# ============================================================================

variable "human_review_percentage" {
  description = "Percentage of outputs requiring human review (MI-007)"
  type        = number
  default     = 0.25 # 25% for Tier 3

  validation {
    condition     = var.human_review_percentage >= 0 && var.human_review_percentage <= 1
    error_message = "Human review percentage must be between 0 and 1"
  }
}

variable "compliance_regulations" {
  description = "Applicable compliance regulations (MI-018)"
  type        = list(string)
  default     = ["GDPR", "SOX", "HIPAA"]
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

# ============================================================================
# Tagging
# ============================================================================

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
