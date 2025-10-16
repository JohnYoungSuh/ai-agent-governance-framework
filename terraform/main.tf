# AI Agent Governance Framework - Terraform Automation
# Tier 3 Operations Agent with GitHub Integration
# Version: 1.0

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket         = "ai-agent-governance-terraform-state"
    key            = "ai-ops-agent/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project         = "AI-Agent-Governance"
      ManagedBy       = "Terraform"
      AgentTier       = "Tier3-Operations"
      ComplianceLevel = "Production"
      Framework       = "ai-agent-governance-v2.0"
    }
  }
}

provider "github" {
  owner = var.github_organization
  token = var.github_token
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
