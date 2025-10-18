# Terraform Modules - AI Agent Governance Framework v2.1

## Overview

This directory contains modular Terraform configurations for deploying AI Agent Governance infrastructure with full compliance, audit correlation, and Jira integration.

## Architecture

```
terraform/
├── main-modular-v2.tf           # Main configuration using modules
├── variables-modular-v2.tf      # Input variables
├── outputs-modular-v2.tf        # Output values with audit correlation
└── modules/
    ├── kms/                     # KMS encryption keys
    ├── secrets_manager/         # AWS Secrets Manager
    ├── cloudtrail/              # CloudTrail audit logging
    ├── s3_audit_logs/           # S3 bucket for audit logs
    ├── iam_roles/               # IAM roles (future)
    ├── vpc/                     # VPC networking (future)
    ├── dynamodb_state/          # DynamoDB for state locking (future)
    └── sns_alerts/              # SNS topic for alerts (future)
```

## Modules

### 1. KMS Module (`modules/kms/`)

**Controls:** SC-028, SEC-001

**Purpose:** Create and manage KMS keys for encryption at rest

**Features:**
- Automatic key rotation
- CloudWatch alarms for key deletion
- Least-privilege IAM policies
- Audit metadata with Jira correlation

**Usage:**
```hcl
module "kms_example" {
  source = "./modules/kms"

  key_alias               = "my-app-encryption"
  key_description         = "KMS key for my application"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  control_ids = ["SC-028", "SEC-001"]
  jira_cr_id  = "CR-2025-1042"
  audit_id    = "audit-1729274400-xyz789"

  tags = {
    Environment = "prod"
  }
}
```

**Outputs:**
- `key_id` - KMS key ID
- `key_arn` - KMS key ARN
- `key_alias` - KMS key alias
- `audit_metadata` - Audit correlation data
- `control_implementation` - Control implementation details

---

### 2. Secrets Manager Module (`modules/secrets_manager/`)

**Controls:** SEC-001, MI-003, IA-005

**Purpose:** Securely store and manage agent credentials

**Features:**
- KMS encryption for secrets
- Least-privilege IAM policies
- Tag-based access control
- Audit trail metadata
- Rotation support (optional)

**Usage:**
```hcl
module "secrets_example" {
  source = "./modules/secrets_manager"

  agent_id    = "security-agent"
  agent_tier  = "tier3-operations"
  kms_key_id  = module.kms_secrets.key_arn

  secrets = {
    "api-token" = {
      description = "API token for external service"
      value       = var.api_token
    }
  }

  control_id  = ["SEC-001", "MI-003"]
  jira_cr_id  = "CR-2025-1042"
  audit_id    = "audit-1729274400-xyz789"
}
```

**Outputs:**
- `secret_arns` - Map of secret names to ARNs
- `secret_names` - Map of secret names
- `iam_policy_json` - IAM policy for secret access
- `audit_metadata` - Audit correlation data
- `control_implementation` - Control implementation details

---

### 3. CloudTrail Module (`modules/cloudtrail/`)

**Controls:** AU-002, G-07, SEC-002

**Purpose:** Enable comprehensive audit logging for AWS API calls

**Features:**
- Multi-region trail
- Log file validation
- CloudWatch Logs integration
- KMS encryption
- Advanced event selectors for AI agent resources
- Metric filters and alarms for security events

**Usage:**
```hcl
module "cloudtrail_example" {
  source = "./modules/cloudtrail"

  trail_name                = "my-audit-trail"
  s3_bucket_name            = module.s3_audit_logs.bucket_name
  enable_log_file_validation = true
  enable_cloudwatch_logs    = true
  kms_key_id                = module.kms_cloudtrail.key_arn

  agent_tier  = "tier3-operations"
  control_ids = ["AU-002", "G-07", "SEC-002"]
  jira_cr_id  = "CR-2025-1042"
  audit_id    = "audit-1729274400-xyz789"
}
```

**Outputs:**
- `trail_arn` - CloudTrail ARN
- `trail_name` - Trail name
- `log_group_arn` - CloudWatch log group ARN
- `audit_metadata` - Audit correlation data
- `control_implementation` - Control implementation details

---

### 4. S3 Audit Logs Module (`modules/s3_audit_logs/`)

**Controls:** AU-002, SEC-002, G-07, AU-009

**Purpose:** Create S3 bucket for long-term audit log storage

**Features:**
- Versioning enabled
- KMS encryption
- Public access blocked
- Lifecycle policies (Glacier transition, retention)
- Object lock for compliance
- Bucket policies for CloudTrail

**Usage:**
```hcl
module "s3_audit_logs_example" {
  source = "./modules/s3_audit_logs"

  bucket_name              = "my-audit-logs-bucket"
  kms_key_id               = module.kms_audit_logs.key_id
  lifecycle_glacier_days   = 90
  lifecycle_expiration_days = 2555  # 7 years

  control_ids = ["AU-002", "SEC-002", "G-07"]
  jira_cr_id  = "CR-2025-1042"
  audit_id    = "audit-1729274400-xyz789"
}
```

**Outputs:**
- `bucket_name` - S3 bucket name
- `bucket_arn` - S3 bucket ARN
- `audit_metadata` - Audit correlation data

---

## Deployment Guide

### Prerequisites

1. **Terraform** >= 1.5.0
2. **AWS CLI** configured with appropriate credentials
3. **Jira CR** approved for staging/prod deployments
4. **Audit ID** generated for tracking

### Step 1: Generate Audit ID

```bash
# Generate unique audit ID
export TF_VAR_audit_id="audit-$(date +%s)-$(uuidgen | cut -d'-' -f1)"
echo "Audit ID: $TF_VAR_audit_id"
```

### Step 2: Set Required Variables

```bash
# Environment (dev/staging/prod)
export TF_VAR_environment="prod"

# Jira CR (required for staging/prod)
export TF_VAR_jira_cr_id="CR-2025-1042"

# Deployed by
export TF_VAR_deployed_by="$(whoami)@$(hostname)"

# GitHub configuration
export TF_VAR_github_organization="your-org"
export TF_VAR_github_token="ghp_xxxxxxxxxxxxx"

# AWS region
export TF_VAR_aws_region="us-east-1"
```

### Step 3: Set Sensitive Values (Secrets)

```bash
# Option 1: Use AWS Secrets Manager (recommended)
export TF_VAR_jira_api_token="$(aws secretsmanager get-secret-value --secret-id jira-api-token --query SecretString --output text)"
export TF_VAR_github_token_secret="$(aws secretsmanager get-secret-value --secret-id github-token --query SecretString --output text)"
export TF_VAR_openai_api_key="$(aws secretsmanager get-secret-value --secret-id openai-api-key --query SecretString --output text)"

# Option 2: Use environment variables (development only)
export TF_VAR_jira_api_token="your-jira-token"
export TF_VAR_github_token_secret="your-github-token"
export TF_VAR_openai_api_key="your-openai-key"
```

### Step 4: Validate Configuration

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# Review plan
terraform plan -var-file="environments/${TF_VAR_environment}.tfvars" -out=tfplan
```

### Step 5: Jira Approval Validation

For staging/prod deployments, validate Jira CR approval:

```bash
# Run Jira validation
python3 ../scripts/validate-jira-approval.py \
  "terraform-deployment" \
  "$TF_VAR_jira_cr_id" \
  "Change Manager"
```

### Step 6: Apply Configuration

```bash
# Apply with approval
terraform apply tfplan

# Save outputs
terraform output -json > terraform-outputs-${TF_VAR_audit_id}.json
```

### Step 7: Generate Audit Trail

```bash
# Audit trail is automatically generated in:
# audit-trail-terraform-${TF_VAR_audit_id}.json
cat audit-trail-terraform-${TF_VAR_audit_id}.json
```

---

## Environment-Specific Configurations

Create `.tfvars` files for each environment:

**`environments/dev.tfvars`:**
```hcl
environment              = "dev"
audit_log_glacier_days   = 30
audit_log_retention_days = 365
enable_cloudwatch_logs   = true
```

**`environments/staging.tfvars`:**
```hcl
environment              = "staging"
audit_log_glacier_days   = 60
audit_log_retention_days = 1825  # 5 years
enable_cloudwatch_logs   = true
```

**`environments/prod.tfvars`:**
```hcl
environment              = "prod"
audit_log_glacier_days   = 90
audit_log_retention_days = 2555  # 7 years
enable_cloudwatch_logs   = true
```

---

## Outputs and Audit Correlation

All modules provide `audit_metadata` outputs for correlation:

```hcl
output "audit_metadata" {
  value = {
    module           = "module_name"
    control_ids      = ["CONTROL-001", "CONTROL-002"]
    created_at       = timestamp()
    jira_reference   = {
      cr_id    = var.jira_cr_id
      audit_id = var.audit_id
    }
    compliance       = {
      nist_controls = ["SC-28", "AU-2"]
      cci_controls  = ["CCI-001199"]
    }
  }
}
```

### Viewing Audit Metadata

```bash
# View complete audit metadata
terraform output audit_metadata

# View Jira reference
terraform output jira_reference

# View control implementation summary
terraform output control_implementation_summary

# View resource tags summary
terraform output resource_tags_summary
```

---

## Resource Tagging Strategy

All resources are tagged with:

- `control_id` - Governance control IDs (e.g., "SEC-001,MI-003")
- `jira_cr_id` - Jira Change Request ID (e.g., "CR-2025-1042")
- `audit_id` - Audit trail ID (e.g., "audit-1729274400-xyz789")
- `Framework` - "AI-Agent-Governance-v2.1"
- `Environment` - "dev", "staging", or "prod"
- `ManagedBy` - "Terraform"

**Example tag query:**

```bash
# Find all resources for a specific Jira CR
aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=jira_cr_id,Values=CR-2025-1042"

# Find all resources for a control
aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=control_id,Values=*SEC-001*"
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Deploy Governance Infrastructure

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod
      jira_cr_id:
        description: 'Jira CR ID (required for staging/prod)'
        required: false

jobs:
  validate-jira:
    runs-on: ubuntu-latest
    if: github.event.inputs.environment != 'dev'
    steps:
      - uses: actions/checkout@v4

      - name: Validate Jira CR
        env:
          JIRA_URL: ${{ secrets.JIRA_URL }}
          JIRA_USER: ${{ secrets.JIRA_USER }}
          JIRA_TOKEN: ${{ secrets.JIRA_TOKEN }}
        run: |
          python3 scripts/validate-jira-approval.py \
            terraform-deployment \
            "${{ github.event.inputs.jira_cr_id }}" \
            "Change Manager"

  terraform:
    needs: [validate-jira]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Generate Audit ID
        id: audit
        run: |
          AUDIT_ID="audit-$(date +%s)-$(uuidgen | cut -d'-' -f1)"
          echo "audit_id=$AUDIT_ID" >> $GITHUB_OUTPUT

      - name: Terraform Init
        run: terraform init
        working-directory: ./terraform

      - name: Terraform Plan
        env:
          TF_VAR_environment: ${{ github.event.inputs.environment }}
          TF_VAR_jira_cr_id: ${{ github.event.inputs.jira_cr_id }}
          TF_VAR_audit_id: ${{ steps.audit.outputs.audit_id }}
          TF_VAR_deployed_by: ${{ github.actor }}
        run: |
          terraform plan \
            -var-file="environments/${{ github.event.inputs.environment }}.tfvars" \
            -out=tfplan
        working-directory: ./terraform

      - name: Terraform Apply
        env:
          TF_VAR_environment: ${{ github.event.inputs.environment }}
          TF_VAR_jira_cr_id: ${{ github.event.inputs.jira_cr_id }}
          TF_VAR_audit_id: ${{ steps.audit.outputs.audit_id }}
        run: terraform apply -auto-approve tfplan
        working-directory: ./terraform

      - name: Upload Audit Trail
        uses: actions/upload-artifact@v3
        with:
          name: audit-trail-${{ steps.audit.outputs.audit_id }}
          path: terraform/audit-trail-terraform-*.json
```

---

## Compliance and Security

### NIST Controls Implemented

- **SC-12** - Cryptographic Key Establishment and Management (KMS)
- **SC-13** - Cryptographic Protection (KMS)
- **SC-28** - Protection of Information at Rest (KMS + S3 encryption)
- **AU-2** - Audit Events (CloudTrail)
- **AU-3** - Content of Audit Records (CloudTrail)
- **AU-6** - Audit Review, Analysis, and Reporting (CloudWatch)
- **AU-9** - Protection of Audit Information (S3 + KMS)
- **AU-11** - Audit Record Retention (S3 Lifecycle)
- **AU-12** - Audit Generation (CloudTrail)
- **IA-5** - Authenticator Management (Secrets Manager)

### CCI Controls Implemented

See module outputs for specific CCI mappings.

---

## Troubleshooting

### Issue: "Jira CR ID is required"

**Solution:**
```bash
export TF_VAR_jira_cr_id="CR-2025-1042"
terraform plan
```

### Issue: "Backend initialization failed"

**Solution:**
```bash
# Create backend resources first
aws s3 mb s3://ai-agent-governance-terraform-state
aws dynamodb create-table --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Issue: "Module not found"

**Solution:**
```bash
# Ensure you're in the terraform directory
cd terraform
terraform init
```

---

## Best Practices

1. **Always use Jira CR for staging/prod**: Never bypass approval gates
2. **Generate unique audit IDs**: Track every deployment
3. **Use environment-specific tfvars**: Separate configurations per environment
4. **Store secrets in AWS Secrets Manager**: Never commit secrets to code
5. **Review plans before apply**: Use `terraform plan` extensively
6. **Tag all resources**: Enable audit correlation and cost tracking
7. **Enable state locking**: Prevent concurrent modifications
8. **Use remote state**: Store state in S3 with encryption

---

## Related Documentation

- [Main Governance Policy](../docs/GOVERNANCE-POLICY.md)
- [Jira Integration Guide](../docs/JIRA-INTEGRATION-GUIDE.md)
- [PAR Workflow Framework](../docs/PAR-WORKFLOW-FRAMEWORK.md)

---

**Version:** 2.1
**Last Updated:** 2025-10-18
**Control Coverage:** SC-028, SEC-001, AU-002, G-07, MI-003
