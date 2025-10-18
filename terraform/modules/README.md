# Terraform Modules - AI Agent Governance Framework

This directory contains reusable Terraform modules for deploying AI agents with governance controls.

## Module Overview

| Module | Control IDs | Purpose |
|--------|-------------|---------|
| `kms_encryption` | SEC-001, MI-003 | KMS encryption keys for data at rest |
| `secrets_manager` | SEC-001, MI-003 | Secure credential storage and rotation |
| `dynamodb_audit` | MI-019 | Audit trail storage (90-day hot + 7-year archive) |
| `cloudtrail` | MI-019 | AWS API activity logging |

## Module Structure (G-03 Compliance)

Each module follows this structure:

```
module-name/
├── main.tf           # Main resource definitions
├── variables.tf      # Input variables (optional, can be in main.tf)
├── outputs.tf        # Module outputs (optional, can be in main.tf)
└── README.md         # Module documentation
```

All modules include:
- **control_id** variable for governance traceability
- **agent_id** and **agent_tier** tagging for resource correlation
- **tags** variable for additional custom tags
- Least-privilege IAM policies
- Encryption at rest (KMS)
- Comprehensive outputs for module chaining

---

## Usage Examples

### Example 1: Deploy Tier 3 Agent with All Modules

```hcl
# main.tf
terraform {
  required_version = ">= 1.5.0"
}

provider "aws" {
  region = "us-east-1"
}

variable "agent_name" {
  default = "security-agent"
}

variable "agent_tier" {
  default = "tier3-operations"
}

# Module 1: KMS Encryption
module "kms_encryption" {
  source = "./modules/kms_encryption"

  agent_id   = var.agent_name
  agent_tier = var.agent_tier

  key_admins = [
    "arn:aws:iam::123456789012:role/AdminRole"
  ]

  tags = {
    Environment = "production"
    Project     = "AI-Agent-Governance"
  }
}

# Module 2: Secrets Manager
module "secrets" {
  source = "./modules/secrets_manager"

  agent_id    = var.agent_name
  agent_tier  = var.agent_tier
  kms_key_id  = module.kms_encryption.key_arn

  secrets = {
    "llm-api-key" = {
      description = "OpenAI API key"
      value       = var.llm_api_key  # Pass from variable
    }
    "github-token" = {
      description = "GitHub PAT for CI/CD"
      value       = var.github_token
    }
  }

  tags = {
    Environment = "production"
  }
}

# Module 3: DynamoDB Audit Trail
module "audit_trail" {
  source = "./modules/dynamodb_audit"

  agent_id    = var.agent_name
  agent_tier  = var.agent_tier
  kms_key_arn = module.kms_encryption.key_arn

  point_in_time_recovery = true
  ttl_enabled            = true

  tags = {
    Environment = "production"
  }
}

# Outputs
output "kms_key_id" {
  value = module.kms_encryption.key_id
}

output "secret_arns" {
  value     = module.secrets.secret_arns
  sensitive = true
}

output "audit_table_name" {
  value = module.audit_trail.table_name
}

output "audit_stream_arn" {
  value = module.audit_trail.table_stream_arn
}
```

### Example 2: Multi-Environment Deployment

```hcl
# environments/dev.tfvars
agent_name = "security-agent"
agent_tier = "tier3-operations"
environment = "dev"

# environments/prod.tfvars
agent_name = "security-agent"
agent_tier = "tier3-operations"
environment = "prod"
point_in_time_recovery = true

# Deploy
terraform apply -var-file=environments/prod.tfvars
```

---

## Module Reference

### kms_encryption

**Purpose**: Create KMS encryption keys for data at rest compliance.

**Inputs:**
- `agent_id` (string, required): Agent identifier
- `agent_tier` (string, required): Agent tier
- `key_admins` (list(string), optional): IAM ARNs for key administrators
- `key_users` (list(string), optional): IAM ARNs for key users
- `control_id` (list(string), default: ["SEC-001", "MI-003"]): Governance controls
- `tags` (map(string), optional): Additional tags

**Outputs:**
- `key_id`: KMS key ID
- `key_arn`: KMS key ARN
- `key_alias`: KMS key alias name

**Example:**
```hcl
module "kms" {
  source = "./modules/kms_encryption"

  agent_id   = "ops-agent"
  agent_tier = "tier3-operations"

  key_admins = ["arn:aws:iam::123456789012:role/AdminRole"]
}
```

---

### secrets_manager

**Purpose**: Store sensitive credentials securely with KMS encryption.

**Inputs:**
- `agent_id` (string, required): Agent identifier
- `agent_tier` (string, required): Agent tier
- `kms_key_id` (string, required): KMS key ARN for secret encryption
- `secrets` (map(object), required): Map of secrets to create
  - `description` (string): Secret description
  - `value` (string): Secret value (sensitive)
- `control_id` (list(string), default: ["SEC-001", "MI-003"]): Governance controls
- `tags` (map(string), optional): Additional tags

**Outputs:**
- `secret_arns`: Map of secret keys to ARNs
- `secret_names`: Map of secret keys to full names
- `iam_policy_json`: IAM policy for least-privilege secret access

**Example:**
```hcl
module "secrets" {
  source = "./modules/secrets_manager"

  agent_id   = "ops-agent"
  agent_tier = "tier3-operations"
  kms_key_id = module.kms.key_arn

  secrets = {
    "api-key" = {
      description = "LLM API key"
      value       = var.llm_api_key
    }
  }
}
```

---

### dynamodb_audit

**Purpose**: Create audit trail storage with 90-day hot storage and 7-year S3 archive.

**Inputs:**
- `agent_id` (string, required): Agent identifier
- `agent_tier` (string, required): Agent tier
- `kms_key_arn` (string, required): KMS key ARN for encryption
- `point_in_time_recovery` (bool, default: true): Enable PITR
- `ttl_enabled` (bool, default: true): Enable TTL for hot storage lifecycle
- `control_id` (list(string), default: ["MI-019"]): Governance controls
- `tags` (map(string), optional): Additional tags

**Outputs:**
- `table_name`: DynamoDB table name
- `table_arn`: DynamoDB table ARN
- `table_stream_arn`: DynamoDB stream ARN (for SIEM integration)
- `archive_bucket_name`: S3 archive bucket name
- `archive_bucket_arn`: S3 archive bucket ARN

**Features:**
- Global Secondary Indexes (GSI) for ActorIndex, ActionIndex, ComplianceIndex
- DynamoDB Streams for real-time SIEM correlation
- S3 lifecycle: 90 days → Glacier IR → 365 days → Deep Archive → 7 years expiration
- Versioning enabled for immutability

**Example:**
```hcl
module "audit" {
  source = "./modules/dynamodb_audit"

  agent_id    = "ops-agent"
  agent_tier  = "tier3-operations"
  kms_key_arn = module.kms.key_arn
}
```

---

## Governance Compliance

### G-03: Modular IaC

All modules are designed for reusability:
- ✅ Consistent variable naming (`agent_id`, `agent_tier`, `control_id`, `tags`)
- ✅ Control ID tagging on all resources
- ✅ Least-privilege IAM policies
- ✅ KMS encryption for all data stores
- ✅ Comprehensive outputs for module chaining

### Control Tagging

Every resource created by modules includes:

```hcl
tags = {
  AgentID   = var.agent_id          # e.g., "security-agent"
  AgentTier = var.agent_tier         # e.g., "tier3-operations"
  ControlID = "SEC-001,MI-003"       # Comma-separated control IDs
  ManagedBy = "Terraform"
  Framework = "AI-Agent-Governance-v2.0"
}
```

### Validation Scripts

Use AWS CLI to validate deployed state (G-05):

```bash
# Validate KMS encryption on DynamoDB
aws dynamodb describe-table \
  --table-name security-agent-audit-trail \
  --query 'Table.SSEDescription.Status'

# Validate secret encryption
aws secretsmanager describe-secret \
  --secret-id security-agent/llm-api-key \
  --query 'KmsKeyId'

# List all resources by control ID
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=ControlID,Values=SEC-001 \
  --query 'ResourceTagMappingList[].ResourceARN'
```

---

## Migration from Monolithic Terraform

To migrate existing monolithic Terraform to modules:

### Step 1: Create Module Instances

```hcl
# Replace inline resources with module calls
module "kms" {
  source = "./modules/kms_encryption"
  # ... variables
}
```

### Step 2: Import Existing Resources

```bash
# Import existing KMS key
terraform import module.kms.aws_kms_key.agent_encryption \
  arn:aws:kms:us-east-1:123456789012:key/abc-123

# Import existing secrets
terraform import module.secrets.aws_secretsmanager_secret.agent_secrets[\"llm-api-key\"] \
  security-agent/llm-api-key
```

### Step 3: Validate No Changes

```bash
terraform plan  # Should show no changes
```

---

## Best Practices

1. **Version Pinning**: Pin module versions in production
   ```hcl
   module "kms" {
     source = "git::https://github.com/org/repo.git//terraform/modules/kms_encryption?ref=v1.0.0"
   }
   ```

2. **State Management**: Use remote state with locking
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "terraform-state"
       key            = "agents/security-agent/terraform.tfstate"
       region         = "us-east-1"
       encrypt        = true
       dynamodb_table = "terraform-state-lock"
     }
   }
   ```

3. **Variable Validation**: Add validation rules
   ```hcl
   variable "agent_tier" {
     validation {
       condition     = can(regex("^tier[1-4]-(observer|developer|operations|architect)$", var.agent_tier))
       error_message = "Invalid agent tier format"
     }
   }
   ```

4. **Control ID Tracking**: Always specify `control_id` when using modules
   ```hcl
   module "secrets" {
     control_id = ["SEC-001", "MI-003", "APP-001"]
   }
   ```

---

## Testing

### Unit Tests (Terratest)

```go
// test/modules_test.go
func TestKMSModule(t *testing.T) {
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/kms_encryption",
        Vars: map[string]interface{}{
            "agent_id":   "test-agent",
            "agent_tier": "tier1-observer",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    keyId := terraform.Output(t, terraformOptions, "key_id")
    assert.NotEmpty(t, keyId)
}
```

### Integration Tests

```bash
# Test module deployment
cd test/integration
terraform init
terraform apply -var agent_id=test-agent
./validate-deployment.sh test-agent
terraform destroy
```

---

## Support

For module issues or feature requests:
- **Issues**: https://github.com/JohnYoungSuh/ai-agent-governance-framework/issues
- **Docs**: See README.md in each module directory

---

**Framework Version:** v2.0
**Last Updated:** 2025-10-17
**Maintained By:** AI Governance Team
