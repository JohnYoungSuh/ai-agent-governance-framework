# AWS Deployment Guide - AI Agent Governance Framework v2.0

**Last Updated:** 2025-10-17
**Framework Version:** v2.0
**Status:** Ready for Deployment

---

## Overview

This guide walks you through deploying AI agent infrastructure on AWS using the modular Terraform configuration with full governance controls.

**What You'll Deploy:**
- ✅ KMS encryption keys for data at rest
- ✅ AWS Secrets Manager for credential storage
- ✅ DynamoDB audit trail with 90-day hot + 7-year S3 archive
- ✅ Lambda function for agent execution
- ✅ CloudWatch logging and cost alarms
- ✅ IAM roles with least-privilege policies
- ✅ SNS topics for cost alerts

**Estimated Deployment Time:** 15-20 minutes

---

## Prerequisites

### 1. AWS Account Setup

```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version

# Configure AWS credentials
aws configure
# AWS Access Key ID: <your-access-key>
# AWS Secret Access Key: <your-secret-key>
# Default region name: us-east-1
# Default output format: json

# Verify authentication
aws sts get-caller-identity
```

**Required IAM Permissions:**
- KMS: CreateKey, DescribeKey, PutKeyPolicy
- Secrets Manager: CreateSecret, PutSecretValue
- DynamoDB: CreateTable, DescribeTable
- Lambda: CreateFunction, UpdateFunctionCode
- IAM: CreateRole, AttachRolePolicy
- CloudWatch: PutMetricAlarm, CreateLogGroup
- S3: CreateBucket, PutBucketPolicy
- SNS: CreateTopic, Subscribe

### 2. Terraform Installation

```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip
unzip terraform_1.6.6_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version
# Expected: Terraform v1.6.6 or later
```

### 3. Required Credentials

Gather the following before deployment:

| Credential | Where to Get | Required Scopes |
|------------|--------------|-----------------|
| LLM API Key | [Anthropic Console](https://console.anthropic.com/settings/keys) or [OpenAI Platform](https://platform.openai.com/api-keys) | Full access |
| GitHub Token | [GitHub Settings](https://github.com/settings/tokens) | `repo`, `workflow` |
| Alert Email | Your team email | N/A |

---

## Step-by-Step Deployment

### Step 1: Clone Repository and Navigate to Terraform Directory

```bash
cd /home/suhlabs/projects/ai-agent-governance-framework/terraform
```

### Step 2: Create terraform.tfvars

```bash
# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Minimum Required Configuration:**

```hcl
# terraform.tfvars
agent_name = "security-agent"
llm_api_key = "sk-ant-api03-YOUR-ANTHROPIC-KEY"  # Or OpenAI key
github_token = "ghp_YOUR-GITHUB-TOKEN"
alert_email = "your-team@example.com"

# Recommended for development
environment = "dev"
daily_cost_budget = 50.0
monthly_cost_budget = 1000.0
```

### Step 3: Review Configuration

```bash
# Validate syntax
python3 << 'EOF'
import re
with open('main-modular.tf') as f:
    content = f.read()
    open_braces = content.count('{')
    close_braces = content.count('}')
    print(f"✅ Braces balanced: {open_braces == close_braces}")
    modules = re.findall(r'module\s+"([^"]+)"', content)
    print(f"✅ Modules: {', '.join(modules)}")
EOF
```

### Step 4: Initialize Terraform

```bash
# Initialize Terraform (downloads providers)
terraform init

# Expected output:
# Terraform has been successfully initialized!
```

**Note:** If using S3 backend, configure first:

```hcl
# Uncomment in main-modular.tf
backend "s3" {
  bucket         = "ai-agent-governance-terraform-state"
  key            = "agents/security-agent/terraform.tfstate"
  region         = "us-east-1"
  encrypt        = true
  dynamodb_table = "terraform-state-lock"
}
```

### Step 5: Plan Deployment

```bash
# Review what will be created
terraform plan -out=tfplan

# Review output carefully:
# - 3 modules will be created (kms_encryption, secrets_manager, audit_trail)
# - ~20-25 resources total
# - Check that agent_name, environment, and budgets are correct
```

**Expected Resources:**
```
Plan: 25 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + agent_function_arn    = (known after apply)
  + audit_table_name      = "security-agent-audit-trail"
  + kms_key_id            = (known after apply)
  + secret_arns           = (sensitive value)
```

### Step 6: Deploy Infrastructure

```bash
# Apply configuration
terraform apply tfplan

# This will take 5-10 minutes
# Watch for any errors

# Expected final output:
# Apply complete! Resources: 25 added, 0 changed, 0 destroyed.
```

### Step 7: Verify Deployment

```bash
# Run AWS CLI validation commands
./scripts/governance-check.sh \
  --agent security-agent \
  --tier 3 \
  --environment dev \
  --budget-limit 50
```

---

## Post-Deployment Validation

### Validate KMS Encryption

```bash
# List KMS keys
aws kms list-aliases --query "Aliases[?contains(AliasName, 'security-agent')]"

# Expected output:
# {
#     "AliasName": "alias/security-agent-encryption",
#     "AliasArn": "arn:aws:kms:us-east-1:123456789012:alias/security-agent-encryption",
#     "TargetKeyId": "abc-123-def-456"
# }

# Verify key rotation enabled
aws kms get-key-rotation-status --key-id alias/security-agent-encryption

# Expected: {"KeyRotationEnabled": true}
```

### Validate Secrets Manager

```bash
# List secrets
aws secretsmanager list-secrets \
  --query "SecretList[?contains(Name, 'security-agent')]"

# Verify KMS encryption
aws secretsmanager describe-secret \
  --secret-id security-agent/llm-api-key \
  --query 'KmsKeyId'

# Expected: "arn:aws:kms:us-east-1:123456789012:key/abc-123-def-456"
```

### Validate DynamoDB Audit Trail

```bash
# Describe audit table
aws dynamodb describe-table \
  --table-name security-agent-audit-trail \
  --query 'Table.{Name:TableName,Status:TableStatus,Encryption:SSEDescription.Status}'

# Expected output:
# {
#     "Name": "security-agent-audit-trail",
#     "Status": "ACTIVE",
#     "Encryption": "ENABLED"
# }

# Verify point-in-time recovery (for production)
aws dynamodb describe-continuous-backups \
  --table-name security-agent-audit-trail \
  --query 'ContinuousBackupsDescription.PointInTimeRecoveryDescription.PointInTimeRecoveryStatus'

# Expected: "ENABLED" (for production) or "DISABLED" (for dev)
```

### Validate S3 Archive Bucket

```bash
# List archive bucket
aws s3 ls | grep security-agent-audit-archive

# Verify encryption
aws s3api get-bucket-encryption \
  --bucket security-agent-audit-archive-123456789012 \
  --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault'

# Expected:
# {
#     "SSEAlgorithm": "aws:kms",
#     "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/abc-123"
# }

# Verify versioning
aws s3api get-bucket-versioning \
  --bucket security-agent-audit-archive-123456789012

# Expected: {"Status": "Enabled"}
```

### Validate IAM Role

```bash
# Get role policy
aws iam get-role-policy \
  --role-name security-agent-role \
  --policy-name security-agent-secrets-policy

# Verify least-privilege (no wildcard actions)
aws iam get-role-policy \
  --role-name security-agent-role \
  --policy-name security-agent-secrets-policy \
  --query 'PolicyDocument.Statement[].Action' \
  | grep -q '\*' && echo "❌ Wildcard actions found" || echo "✅ Least-privilege policy"
```

### Validate CloudWatch Logs

```bash
# List log groups
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/lambda/security-agent"

# Expected:
# {
#     "logGroups": [
#         {
#             "logGroupName": "/aws/lambda/security-agent",
#             "retentionInDays": 90,
#             "kmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/abc-123"
#         }
#     ]
# }
```

### Validate Cost Alarms

```bash
# List cost alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix "security-agent-daily-cost"

# Expected: 2 alarms (50% and 90% thresholds)
```

---

## Testing the Deployment

### Test 1: Write Test Audit Entry

```bash
# Create test audit entry
aws dynamodb put-item \
  --table-name security-agent-audit-trail \
  --item '{
    "audit_id": {"S": "test-audit-001"},
    "timestamp": {"S": "2025-10-17T22:00:00Z"},
    "actor": {"S": "test-user"},
    "action": {"S": "test_deployment"},
    "workflow_step": {"S": "TEST-001"},
    "policy_controls_checked": {"L": [{"S": "MI-019"}]},
    "compliance_result": {"S": "pass"},
    "evidence_hash": {"S": "sha256:test123"},
    "auditor_agent": {"S": "test-validator"}
  }'

# Verify entry
aws dynamodb get-item \
  --table-name security-agent-audit-trail \
  --key '{"audit_id": {"S": "test-audit-001"}, "timestamp": {"S": "2025-10-17T22:00:00Z"}}'
```

### Test 2: Retrieve Secret (from Lambda perspective)

```bash
# Get secret value
aws secretsmanager get-secret-value \
  --secret-id security-agent/llm-api-key \
  --query 'SecretString' \
  --output text

# Should return your LLM API key (redacted here)
```

### Test 3: Trigger Cost Alarm (Optional)

```bash
# Set alarm state to test notification
aws cloudwatch set-alarm-state \
  --alarm-name security-agent-daily-cost-90pct \
  --state-value ALARM \
  --state-reason "Testing alarm notification"

# Check your email for SNS notification
```

---

## Governance Compliance Verification

Run the enhanced governance check script:

```bash
cd /home/suhlabs/projects/ai-agent-governance-framework

./scripts/governance-check.sh \
  --agent security-agent \
  --tier 3 \
  --environment dev \
  --budget-limit 50
```

**Expected Output:**

```
==========================================
AI Agent Governance Check
==========================================
Agent: security-agent
Tier: 3
Environment: dev
Budget Limit: $50
==========================================

✓ Checking tier assignment...
  ✅ Valid tier: 3
✓ Checking budget configuration...
  ✅ Budget limit configured: $50
✓ Checking framework version...
  ✅ Framework version: 2.1.0
✓ Checking required mitigations...
  ✅ MI-001: Data leakage prevention...
  ✅ MI-003: Secrets management...
  ✅ MI-009: Cost monitoring...
  ✅ MI-020: Tier enforcement...
  ✅ MI-021: Budget limits...
✓ Checking observability setup...
  ✅ OpenTelemetry instrumentation enabled
  ✅ Prometheus metrics endpoint configured
  ✅ Distributed tracing enabled
✓ Checking security configuration...
  ✅ Non-root container (UID 1000)
  ✅ Read-only root filesystem
  ✅ Dropped capabilities (ALL)
  ✅ NetworkPolicy configured
✓ Validating deployed AWS infrastructure state (G-05)...
  Checking DynamoDB table encryption...
    ✅ DynamoDB encryption verified: ENABLED
  Checking Secrets Manager configuration...
    ✅ Secret encrypted with KMS: arn:aws:kms:us-east-1:...
  Checking CloudWatch log groups...
    ✅ CloudWatch log group exists: /aws/lambda/security-agent
  Checking IAM policy for least-privilege...
    ✅ IAM policy follows least-privilege (no wildcard actions)
  Checking KMS encryption key...
    ✅ KMS key alias found: alias/security-agent-encryption
✓ Checking audit trail configuration...
  ✅ Audit trail schema defined
  ✅ 90-day hot storage + 7-year archive retention

==========================================
Governance Check Summary
==========================================
Passed: 25
Failed: 0

✅ All governance checks passed!
Agent security-agent is approved for deployment to dev
```

---

## Cost Estimation

### Monthly Cost Breakdown (Development Environment)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Lambda** | 10,000 invocations @ 1GB memory, 30s avg | $3.50 |
| **DynamoDB** | 1M read/write units, 1GB storage | $2.75 |
| **S3** | 10GB audit archive storage | $0.23 |
| **Secrets Manager** | 2 secrets | $0.80 |
| **KMS** | 1 key, 10,000 API calls | $1.20 |
| **CloudWatch Logs** | 5GB ingestion, 90-day retention | $3.00 |
| **SNS** | 100 notifications | $0.50 |
| **Data Transfer** | 1GB outbound | $0.09 |
| **LLM API** (Anthropic Claude Sonnet) | 1M input tokens, 500K output | $15.00 - $75.00 |
| **TOTAL** | | **$27 - $87/month** |

### Production Environment Estimate

For production with higher usage:
- Lambda: $15-30/month
- DynamoDB: $10-25/month (with reserved capacity)
- LLM API: $100-500/month (depends heavily on usage)
- Other services: $10-20/month
- **TOTAL: $135-575/month**

---

## Troubleshooting

### Issue: Terraform Init Fails

```bash
# Error: Failed to download provider
Solution: Check internet connectivity and retry
terraform init -upgrade
```

### Issue: Insufficient IAM Permissions

```bash
# Error: AccessDeniedException
Solution: Add required IAM permissions to your AWS user/role
# See Prerequisites section for full list
```

### Issue: Secret Already Exists

```bash
# Error: ResourceExistsException
Solution: Import existing secret or delete and recreate
terraform import module.secrets_manager.aws_secretsmanager_secret.agent_secrets[\"llm-api-key\"] \
  security-agent/llm-api-key
```

### Issue: DynamoDB Encryption Not Enabled

```bash
# Encryption shows "NOT_FOUND" in governance check
Solution: Verify KMS key permissions
aws kms describe-key --key-id alias/security-agent-encryption
```

### Issue: Cost Alarms Not Triggering

```bash
# No email notifications received
Solution: Confirm SNS subscription
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:security-agent-cost-alerts

# Confirm email subscription in inbox
```

---

## Cleanup / Teardown

To destroy all infrastructure:

```bash
# WARNING: This will delete all resources including audit data!

# Step 1: Disable deletion protection (if enabled)
# Step 2: Destroy resources
terraform destroy

# Step 3: Verify cleanup
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=AgentID,Values=security-agent

# Step 4: Manual cleanup (if needed)
# - Empty and delete S3 archive bucket
# - Delete CloudWatch log streams
# - Remove SNS subscriptions
```

---

## Next Steps

After successful deployment:

1. **Configure Jira Integration** (for Tier 3/4)
   - Add GitHub Secrets: JIRA_URL, JIRA_USER, JIRA_TOKEN
   - Test validation script

2. **Set Up Monitoring Dashboard**
   - Create CloudWatch dashboard
   - Configure Grafana (if using)
   - Set up Prometheus scraping

3. **Test Agent Functionality**
   - Invoke Lambda function
   - Verify audit trail writes
   - Check cost tracking

4. **Configure CI/CD**
   - Update GitHub Actions workflow
   - Add Jira approval gate
   - Test deployment pipeline

5. **Production Deployment**
   - Review security controls
   - Run STRIDE threat model
   - Get Jira CR approval
   - Deploy to production environment

---

## Support

For deployment issues:
- **Framework Issues**: https://github.com/JohnYoungSuh/ai-agent-governance-framework/issues
- **AWS Support**: https://console.aws.amazon.com/support
- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

---

**Document Version:** 1.0
**Last Updated:** 2025-10-17
**Maintained By:** AI Governance Team
