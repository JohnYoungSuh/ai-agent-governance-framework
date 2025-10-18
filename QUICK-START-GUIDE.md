# Quick Start Guide - AI Agent Governance Framework v2.1

**Last Updated:** 2025-10-18
**Status:** Production Ready

---

## Overview

This guide provides step-by-step instructions to get started with the AI Agent Governance Framework v2.1, including all new schema validation, Jira integration, and compliance features.

---

## Prerequisites

### 1. Install Dependencies

```bash
# Python dependencies
pip install jsonschema boto3 requests opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

# AWS CLI
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# jq for JSON processing
sudo apt-get install jq  # Debian/Ubuntu
# or
brew install jq  # macOS
```

### 2. Configure Environment Variables

```bash
# Create .env file
cat > .env <<'EOF'
# Jira Configuration
export JIRA_URL=https://your-company.atlassian.net
export JIRA_USER=your-email@company.com
export JIRA_TOKEN=your-jira-api-token

# AWS Configuration
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key

# OpenTelemetry
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Budget Limits
export DAILY_COST_BUDGET=50
export MONTHLY_COST_BUDGET=500
EOF

# Load environment
source .env
```

---

## Step 1: Validate Schemas

```bash
# Validate all schemas in CI/CD
python3 scripts/validate-schema.py --batch

# Expected output:
# 🔍 Running batch schema validation...
# ✅ audit-trail.json      <- test/example-audit-trail.json
# ✅ siem-event.json       <- test/example-siem-event.json
# ✅ agent-cost-record.json <- test/example-cost-record.json
# ✅ All validations passed!
```

---

## Step 2: Setup Jira Integration

### 2.1 Configure Jira Webhook

```bash
# Setup webhook for CR status monitoring (G-07)
./scripts/setup-jira-webhook.sh \
  --jira-url $JIRA_URL \
  --webhook-url https://api.github.com/repos/YOUR_ORG/YOUR_REPO/dispatches

# Follow prompts to:
# 1. Create webhook in Jira
# 2. Configure GitHub secrets
# 3. Test webhook delivery
```

### 2.2 Test Jira Approval Validation

```bash
# Validate a Jira CR is approved
./scripts/validate-jira-approval.py \
  security-agent \
  CR-2025-1042 \
  "Change Manager"

# Expected output if approved:
# ✅ CR Status Verified: Approved
# ✅ Required approver role verified: Change Manager
# ✅ VALIDATION PASSED
```

---

## Step 3: Deploy Agent with Governance

### 3.1 Tier 1-2 Agent (Dev Environment)

```bash
# No Jira CR required
./scripts/setup-agent.sh \
  --tier 2 \
  --name code-reviewer \
  --environment dev \
  --daily-budget 25
```

### 3.2 Tier 3-4 Agent (Production)

```bash
# Jira CR REQUIRED
./scripts/setup-agent.sh \
  --tier 3 \
  --name security-agent \
  --environment prod \
  --jira-cr-id CR-2025-1042 \
  --run-threat-model \
  --daily-budget 50 \
  --monthly-budget 500

# Process:
# 1. ✅ Jira approval validated
# 2. 📁 Agent directory structure created
# 3. 🔐 AWS Secrets Manager configured
# 4. 📊 Monitoring & logging enabled
# 5. ⚙️  Governance checks passed
```

---

## Step 4: Terraform Infrastructure

### 4.1 Initialize Terraform

```bash
cd terraform/

# Initialize
terraform init

# Plan with variables
terraform plan \
  -var="agent_name=security-agent" \
  -var="agent_tier=3" \
  -var="enable_audit_trail=true"
```

### 4.2 Apply Infrastructure

```bash
# Apply changes
terraform apply -auto-approve

# View control implementations (G-03)
terraform output control_implementations

# Expected output:
# {
#   "SEC-001" = {
#     control_id = "SEC-001"
#     nist_controls = ["SC-28", "IA-5"]
#     cci_controls = ["CCI-001199", "CCI-000196"]
#     aws_resources = [...]
#     ...
#   }
# }
```

---

## Step 5: Run Compliance Checks

### 5.1 Governance Check

```bash
# Run comprehensive governance validation
./scripts/governance-check.sh \
  --agent security-agent \
  --tier 3 \
  --environment prod \
  --budget-limit 500

# Validates:
# ✅ Tier assignment
# ✅ Budget configuration
# ✅ Framework version
# ✅ Risk mitigations
# ✅ Observability setup
# ✅ AWS resource compliance (G-05)
#    - KMS key rotation
#    - S3 bucket encryption
#    - CloudWatch log retention
#    - IAM policy wildcards
#    - Secrets Manager rotation
```

---

## Step 6: Track Costs with Schema Validation

### 6.1 Emit Cost Event (OpenTelemetry)

```bash
# Track individual task cost
python3 scripts/cost-tracker-otel.py \
  --agent security-agent \
  --cost 0.75 \
  --tokens 5000 \
  --task-id task-scan-001 \
  --model gpt-4-turbo \
  --budget 500 \
  --total-cost 125.50

# Output:
# ✅ Cost tracked via OpenTelemetry: $0.7500, 5,000 tokens
#    Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
#    Span ID:  00f067aa0ba902b7
```

### 6.2 Generate Monthly Cost Report

```bash
# Generate cost report with schema validation
./scripts/cost-report.sh \
  --agent security-agent \
  --month 2025-10 \
  --validate-schema \
  --format console

# Output includes:
# - Task metrics (total, successful, failed)
# - Token usage breakdown
# - Cost breakdown (LLM, compute, storage, network)
# - ROI metrics (time saved, value delivered)
# - Budget status with alerts
```

---

## Step 7: Secret Management (SEC-001)

### 7.1 Checkout Secret

```python
# Use SEC-001 example implementation
python3 examples/control-validation/sec-001-example.py \
  --agent-id security-agent \
  --tier 3 \
  --secret-name llm-api-key \
  --jira-cr-id CR-2025-1042

# Process:
# 1. Validates Jira CR approved
# 2. Retrieves secret from AWS Secrets Manager
# 3. Creates audit trail entry
# 4. Emits SIEM event
# 5. Returns secret for use
# 6. Checks in secret after use
```

---

## Step 8: Monitor & Observe

### 8.1 View Audit Trail

```bash
# Query DynamoDB audit trail
aws dynamodb scan \
  --table-name security-agent-audit-trail \
  --filter-expression "workflow_step = :step" \
  --expression-attribute-values '{":step":{"S":"SEC-001"}}' \
  --region us-east-1 \
  | jq '.Items[] | {audit_id, timestamp, action, compliance_result}'
```

### 8.2 View SIEM Events

```bash
# SIEM events are exported to /tmp during development
ls -lh /tmp/siem-*.json

# View latest event
jq '.' $(ls -t /tmp/siem-*.json | head -1)

# In production, these go to your SIEM/OTEL collector
```

### 8.3 OpenTelemetry Traces

```bash
# View traces in Jaeger UI (if configured)
open http://localhost:16686

# Search by:
# - service.name: "ai-agent-cost-tracker" or "sec-001-secrets-manager"
# - control.id: "SEC-001", "MI-009", etc.
# - agent.id: "security-agent"
```

---

## Step 9: CI/CD Integration

### 9.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy-agent.yml
name: Deploy Agent with Governance

on:
  workflow_dispatch:
    inputs:
      agent_name:
        required: true
      environment:
        required: true
      jira_cr_id:
        required: false  # Required for prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Step 1: Validate schemas
      - name: Validate Schemas
        run: python3 scripts/validate-schema.py --batch

      # Step 2: Validate Jira CR (if prod)
      - name: Validate Jira Approval
        if: github.event.inputs.environment == 'prod'
        env:
          JIRA_URL: ${{ secrets.JIRA_URL }}
          JIRA_USER: ${{ secrets.JIRA_USER }}
          JIRA_TOKEN: ${{ secrets.JIRA_TOKEN }}
        run: |
          ./scripts/validate-jira-approval.py \
            ${{ github.event.inputs.agent_name }} \
            ${{ github.event.inputs.jira_cr_id }} \
            "Change Manager"

      # Step 3: Run governance checks
      - name: Governance Validation
        run: |
          ./scripts/governance-check.sh \
            --agent ${{ github.event.inputs.agent_name }} \
            --tier 3 \
            --environment ${{ github.event.inputs.environment }}

      # Step 4: Deploy infrastructure
      - name: Terraform Apply
        run: |
          cd terraform
          terraform init
          terraform apply -auto-approve
```

---

## Common Workflows

### Workflow 1: Add New Agent

```bash
# 1. Create Jira CR (for Tier 3/4)
# 2. Get CR approved
# 3. Run setup script
./scripts/setup-agent.sh \
  --tier 3 \
  --name new-agent \
  --jira-cr-id CR-2025-XXXX \
  --environment prod

# 4. Deploy infrastructure
cd terraform && terraform apply

# 5. Verify deployment
./scripts/governance-check.sh --agent new-agent --tier 3
```

### Workflow 2: Update Existing Agent

```bash
# 1. Create Jira CR for change
# 2. Make code changes
# 3. Run validations
python3 scripts/validate-schema.py --batch
./scripts/governance-check.sh --agent existing-agent

# 4. Deploy via CI/CD
# GitHub Actions automatically validates Jira CR and deploys
```

### Workflow 3: Cost Analysis

```bash
# 1. Generate monthly report
./scripts/cost-report.sh \
  --agent security-agent \
  --month 2025-10 \
  --validate-schema \
  --format json \
  --output /tmp/cost-report.json

# 2. Check for budget alerts
# Report automatically shows warnings at 50%, 90%

# 3. Export to finance system
cat /tmp/cost-report.json | \
  jq '{agent_id, month, total_cost: .summary.total_cost_usd, roi: .roi_metrics.roi_ratio}'
```

---

## Troubleshooting

### Issue: Schema Validation Fails

```bash
# Check schema version
head -5 policies/schemas/audit-trail.json

# Validate with detailed errors
python3 scripts/validate-schema.py \
  --schema policies/schemas/audit-trail.json \
  --data test/example-audit-trail.json
```

### Issue: Jira CR Validation Fails

```bash
# Test Jira connection
curl -u $JIRA_USER:$JIRA_TOKEN $JIRA_URL/rest/api/3/myself

# Check CR status manually
curl -u $JIRA_USER:$JIRA_TOKEN \
  $JIRA_URL/rest/api/3/issue/CR-2025-1042 \
  | jq '.fields.status.name'
```

### Issue: AWS Resources Not Found

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check if resources exist
aws secretsmanager list-secrets \
  --region $AWS_REGION \
  | jq '.SecretList[] | select(.Name | contains("security-agent"))'
```

---

## Next Steps

1. **Review Examples:** See `examples/control-validation/` for complete implementations
2. **Customize:** Modify templates in `templates/` for your organization
3. **Deploy:** Use Terraform modules in `terraform/modules/`
4. **Monitor:** Set up OpenTelemetry backend (Jaeger, Grafana, etc.)
5. **Integrate:** Connect SIEM to your security operations center

---

## Support

- **Documentation:** See `docs/` directory
- **Examples:** All `examples/` include working code
- **Issues:** GitHub Issues
- **Schemas:** `policies/schemas/` with detailed field descriptions

---

**Status:** ✅ Production Ready
**Version:** 2.1.0
**Last Updated:** 2025-10-18
