# Outputs for Modular Terraform Configuration
# AI Agent Governance Framework v2.1

# ============================================================================
# KMS Outputs
# ============================================================================

output "kms_keys" {
  description = "KMS key information"
  value = {
    secrets = {
      key_id    = module.kms_secrets.key_id
      key_arn   = module.kms_secrets.key_arn
      key_alias = module.kms_secrets.key_alias
    }
    cloudtrail = {
      key_id    = module.kms_cloudtrail.key_id
      key_arn   = module.kms_cloudtrail.key_arn
      key_alias = module.kms_cloudtrail.key_alias
    }
    audit_logs = {
      key_id    = module.kms_audit_logs.key_id
      key_arn   = module.kms_audit_logs.key_arn
      key_alias = module.kms_audit_logs.key_alias
    }
  }
}

# ============================================================================
# S3 Audit Logs Outputs
# ============================================================================

output "s3_audit_logs" {
  description = "S3 audit logs bucket information"
  value = {
    bucket_name = module.s3_audit_logs.bucket_name
    bucket_arn  = module.s3_audit_logs.bucket_arn
  }
}

# ============================================================================
# CloudTrail Outputs
# ============================================================================

output "cloudtrail" {
  description = "CloudTrail configuration"
  value = {
    trail_arn       = module.cloudtrail.trail_arn
    trail_name      = module.cloudtrail.trail_name
    log_group_arn   = module.cloudtrail.log_group_arn
    log_group_name  = module.cloudtrail.log_group_name
  }
}

# ============================================================================
# Secrets Manager Outputs
# ============================================================================

output "secrets_security_agent" {
  description = "Security agent secrets"
  value = {
    secret_arns  = module.secrets_tier3_security_agent.secret_arns
    secret_names = module.secrets_tier3_security_agent.secret_names
  }
  sensitive = true
}

output "secrets_ops_agent" {
  description = "Ops agent secrets"
  value = {
    secret_arns  = module.secrets_tier3_ops_agent.secret_arns
    secret_names = module.secrets_tier3_ops_agent.secret_names
  }
  sensitive = true
}

# ============================================================================
# Audit Correlation Outputs
# ============================================================================

output "audit_metadata" {
  description = "Complete audit metadata for all deployed resources"
  value = {
    audit_id              = var.audit_id
    jira_cr_id            = var.jira_cr_id
    deployment_timestamp  = timestamp()
    environment           = var.environment
    aws_account_id        = data.aws_caller_identity.current.account_id
    aws_region            = data.aws_region.current.name
    deployed_by           = var.deployed_by
    terraform_version     = terraform_version

    modules = {
      kms_secrets       = module.kms_secrets.audit_metadata
      kms_cloudtrail    = module.kms_cloudtrail.audit_metadata
      kms_audit_logs    = module.kms_audit_logs.audit_metadata
      s3_audit_logs     = module.s3_audit_logs.audit_metadata
      cloudtrail        = module.cloudtrail.audit_metadata
      secrets_security  = module.secrets_tier3_security_agent.audit_metadata
      secrets_ops       = module.secrets_tier3_ops_agent.audit_metadata
    }
  }
}

output "jira_reference" {
  description = "Jira reference for audit trail correlation"
  value = {
    cr_id          = var.jira_cr_id
    audit_id       = var.audit_id
    environment    = var.environment
    deployed_by    = var.deployed_by
    deployed_at    = timestamp()
    controls       = ["AU-002", "SEC-001", "SEC-002", "G-07", "MI-003", "SC-028"]
    resources_deployed = {
      kms_keys       = 3
      s3_buckets     = 1
      cloudtrail     = 1
      secrets        = 5
    }
  }
}

output "control_implementation_summary" {
  description = "Summary of all control implementations"
  value = {
    "SC-028" = {
      control_family = "System and Communications Protection - Encryption"
      implemented_by = ["KMS Keys (3 instances)"]
      resources      = [
        module.kms_secrets.key_arn,
        module.kms_cloudtrail.key_arn,
        module.kms_audit_logs.key_arn
      ]
      features       = module.kms_secrets.control_implementation.features
    }
    "SEC-001" = {
      control_family = "Secrets Management"
      implemented_by = ["AWS Secrets Manager", "AWS KMS"]
      resources      = flatten([
        values(module.secrets_tier3_security_agent.secret_arns),
        values(module.secrets_tier3_ops_agent.secret_arns)
      ])
      features       = {
        kms_encrypted   = true
        least_privilege = true
        rotation_ready  = true
      }
    }
    "AU-002" = {
      control_family = "Audit and Accountability"
      implemented_by = ["AWS CloudTrail", "S3 Audit Logs"]
      resources      = [
        module.cloudtrail.trail_arn,
        module.s3_audit_logs.bucket_arn
      ]
      features       = module.cloudtrail.control_implementation.features
    }
    "G-07" = {
      control_family = "Audit Trail and Jira Integration"
      implemented_by = ["CloudTrail", "S3 Audit Logs", "Module Metadata"]
      jira_reference = {
        cr_id    = var.jira_cr_id
        audit_id = var.audit_id
      }
    }
  }
}

# ============================================================================
# Resource Tags Summary
# ============================================================================

output "resource_tags_summary" {
  description = "Summary of all resources with control_id tags"
  value = {
    kms_secrets_tags = {
      control_id = join(",", module.kms_secrets.audit_metadata.control_ids)
      jira_cr_id = module.kms_secrets.audit_metadata.jira_reference.cr_id
      audit_id   = module.kms_secrets.audit_metadata.jira_reference.audit_id
    }
    kms_cloudtrail_tags = {
      control_id = join(",", module.kms_cloudtrail.audit_metadata.control_ids)
      jira_cr_id = module.kms_cloudtrail.audit_metadata.jira_reference.cr_id
      audit_id   = module.kms_cloudtrail.audit_metadata.jira_reference.audit_id
    }
    s3_audit_logs_tags = {
      control_id = join(",", module.s3_audit_logs.audit_metadata.control_ids)
      jira_cr_id = module.s3_audit_logs.audit_metadata.jira_reference.cr_id
      audit_id   = module.s3_audit_logs.audit_metadata.jira_reference.audit_id
    }
    cloudtrail_tags = {
      control_id = join(",", module.cloudtrail.audit_metadata.control_ids)
      jira_cr_id = module.cloudtrail.audit_metadata.jira_reference.cr_id
      audit_id   = module.cloudtrail.audit_metadata.jira_reference.audit_id
    }
  }
}

# ============================================================================
# NIST/CCI Compliance Mapping
# ============================================================================

output "compliance_mapping" {
  description = "NIST and CCI control mappings"
  value = {
    nist_controls = {
      "SC-12" = ["KMS key management"]
      "SC-13" = ["KMS encryption algorithms"]
      "SC-28" = ["KMS encryption at rest"]
      "AU-2"  = ["CloudTrail event logging"]
      "AU-3"  = ["CloudTrail audit content"]
      "AU-6"  = ["CloudTrail audit review"]
      "AU-9"  = ["S3 audit log protection"]
      "AU-11" = ["S3 audit log retention"]
      "AU-12" = ["CloudTrail audit generation"]
      "IA-5"  = ["Secrets Manager credential management"]
    }
    cci_controls = merge(
      module.kms_secrets.audit_metadata.compliance.cci_controls,
      module.cloudtrail.audit_metadata.compliance.cci_controls,
      module.s3_audit_logs.audit_metadata.compliance.cci_controls
    )
  }
}

# ============================================================================
# Terraform State Reference
# ============================================================================

output "terraform_state_reference" {
  description = "Reference information for Terraform state"
  value = {
    state_bucket    = "ai-agent-governance-terraform-state"
    state_key       = "governance-framework/terraform.tfstate"
    state_region    = "us-east-1"
    lock_table      = "terraform-state-lock"
    applied_at      = timestamp()
    applied_by      = var.deployed_by
    jira_cr_id      = var.jira_cr_id
    audit_id        = var.audit_id
  }
}
