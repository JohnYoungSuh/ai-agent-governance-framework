# Jira Integration Guide

**AI Agent Governance Framework v2.1**
**Controls: APP-001 (Human Primacy), G-02 (Approval Enforcement), G-07 (Jira Integration)**

## Overview

This guide covers the complete Jira integration for AI agent governance, including:
- Jira CR approval validation with PKI signing
- Real-time webhook integration for CR status changes
- CI/CD enforcement for non-approved deployments
- Tier 3/4 script requirements

---

## Table of Contents

1. [Architecture](#architecture)
2. [Setup & Configuration](#setup--configuration)
3. [Jira CR Approval Workflow](#jira-cr-approval-workflow)
4. [PKI Signing](#pki-signing)
5. [Webhook Integration](#webhook-integration)
6. [CI/CD Enforcement](#cicd-enforcement)
7. [Script Usage](#script-usage)
8. [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Jira Integration                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌────────────────┐     ┌─────────────────┐    ┌──────────────────┐
│  Jira CR API   │     │ Webhook Receiver│    │  PKI Validation  │
│  Validation    │     │  (Real-time)    │    │   (Signatures)   │
└────────────────┘     └─────────────────┘    └──────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   CI/CD Enforcement     │
                    │  (GitHub Actions)       │
                    └─────────────────────────┘
                                 │
                    ┌────────────┴───────────┐
                    │                        │
                    ▼                        ▼
            ┌──────────────┐        ┌──────────────┐
            │  Tier 3/4    │        │ Audit Trail  │
            │  Deployment  │        │  Generation  │
            └──────────────┘        └──────────────┘
```

---

## Setup & Configuration

### 1. Environment Variables

Create a `.env` file or set environment variables:

```bash
# Jira API Configuration
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_USER="your-email@company.com"
export JIRA_TOKEN="your-jira-api-token"

# Webhook Configuration (optional)
export WEBHOOK_SECRET="your-secure-webhook-secret"
export REDIS_URL="redis://localhost:6379"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# PKI Configuration (optional)
export ENFORCE_PKI_VALIDATION="false"  # Set to "true" for production
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Or install individually
pip install requests cryptography redis
```

### 3. Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it "AI Agent Governance"
4. Copy the token and set as `JIRA_TOKEN`

### 4. GitHub Secrets

Configure GitHub repository secrets:

```
Settings > Secrets and variables > Actions > New repository secret
```

Required secrets:
- `JIRA_URL` - Your Jira instance URL
- `JIRA_USER` - Jira username/email
- `JIRA_TOKEN` - Jira API token

---

## Jira CR Approval Workflow

### CR Creation

1. **Create Change Request in Jira**
   - Project: Your CR project
   - Issue Type: "Change Request"
   - Required Fields:
     - Summary: Brief description
     - Description: Include budget (e.g., "Budget: 10000 tokens")
     - Priority: Based on agent tier
     - Assignee: Responsible team member

2. **CR Naming Convention**
   ```
   Pattern: CR-YYYY-NNNN
   Example: CR-2025-1042
   ```

### CR Approval Process

1. **Submit for Approval**
   - Transition CR to "Pending Approval"
   - Assign to Change Manager or Security Lead

2. **Approval Review**
   - Change Manager reviews:
     - Agent tier and permissions
     - Budget allocation
     - Security implications
     - Compliance requirements

3. **Approve CR**
   - Transition to "Approved" status
   - (Optional) Add PKI signature for cryptographic proof

4. **Use in Deployment**
   ```bash
   # Tier 3 deployment to production
   ./scripts/setup-agent.sh \
     --tier 3 \
     --name security-agent \
     --environment prod \
     --jira-cr-id CR-2025-1042
   ```

---

## PKI Signing

PKI digital signatures provide cryptographic proof of approval authority.

### Generate Key Pair

```bash
# Generate keys for Change Manager
python3 scripts/generate-pki-keys.py \
  --name "Change Manager" \
  --output-dir ./pki-keys \
  --key-size 2048

# Enter password when prompted (min 8 chars)
```

**Output:**
- `change-manager.key` - Private key (encrypted, keep secure!)
- `change-manager.pub` - Public key (share for verification)
- `change-manager.crt` - Self-signed certificate

### Sign a CR Approval

```bash
# Sign CR approval with private key
python3 scripts/generate-pki-keys.py \
  --sign \
  --cr-id CR-2025-1042 \
  --private-key ./pki-keys/change-manager.key \
  --password

# Output: CR-2025-1042-signature.json
```

### Add Signature to Jira

1. Go to Jira CR (e.g., CR-2025-1042)
2. Edit custom field "PKI Signature" (customfield_10103)
3. Paste contents of `CR-2025-1042-signature.json`
4. Save

### Enable PKI Validation

```bash
# For production environments
export ENFORCE_PKI_VALIDATION="true"

# Now deployments will fail if PKI signature is invalid
```

---

## Webhook Integration

Real-time webhook receiver for Jira CR status changes.

### Start Webhook Receiver

```bash
# Development (HTTP)
python3 scripts/jira-webhook-receiver.py --port 8080

# Production (HTTPS with TLS)
python3 scripts/jira-webhook-receiver.py \
  --port 8443 \
  --tls-cert /path/to/cert.pem \
  --tls-key /path/to/key.pem
```

### Configure Jira Webhook

1. **Go to Jira Settings**
   - Settings > System > WebHooks
   - Click "Create a WebHook"

2. **Configure Webhook**
   - Name: `AI Agent Governance - CR Status`
   - Status: Enabled
   - URL: `https://your-domain.com/jira/webhook`
   - Events:
     - ☑ Issue Updated
     - ☑ Issue Transitioned
   - JQL Filter: `project = CR AND issuetype = "Change Request"`

3. **Add Authentication Header**
   ```
   Header: X-Webhook-Signature
   Value: sha256=<your-webhook-secret>
   ```

4. **Test Webhook**
   - Click "Test" button
   - Check receiver logs for event

### Webhook Features

- **Real-time CR Status Updates**: Immediate notification of approvals/rejections
- **Redis Caching**: Fast CR status lookup (24-hour TTL)
- **Slack Notifications**: Alerts for critical status changes
- **Audit Trail**: Automatic logging of all status changes
- **HMAC Validation**: Cryptographic verification of webhook authenticity

### Health Check

```bash
curl http://localhost:8080/health

# Response:
# {
#   "status": "healthy",
#   "service": "jira-webhook-receiver",
#   "version": "2.1",
#   "timestamp": "2025-10-18T12:00:00Z"
# }
```

---

## CI/CD Enforcement

GitHub Actions workflow automatically enforces Jira CR approval for Tier 3/4 deployments.

### Workflow: deploy-security-agent.yml

```yaml
# Tier 3/4 deployment requires Jira CR approval
- name: Validate Jira Approval
  env:
    JIRA_URL: ${{ secrets.JIRA_URL }}
    JIRA_USER: ${{ secrets.JIRA_USER }}
    JIRA_TOKEN: ${{ secrets.JIRA_TOKEN }}
  run: |
    ./scripts/validate-jira-approval.py \
      ${{ env.AGENT_NAME }} \
      "${{ github.event.inputs.jira_cr_id }}" \
      "Change Manager"
```

### Deployment Examples

**Tier 1/2 (Dev) - No CR Required:**
```bash
gh workflow run deploy-security-agent.yml \
  -f environment=dev
```

**Tier 3 (Staging) - CR Required:**
```bash
gh workflow run deploy-security-agent.yml \
  -f environment=staging \
  -f jira_cr_id=CR-2025-1042
```

**Tier 3/4 (Production) - CR Required:**
```bash
gh workflow run deploy-security-agent.yml \
  -f environment=prod \
  -f jira_cr_id=CR-2025-1042
```

### Enforcement Behavior

| Environment | Tier | CR Required? | Validation |
|-------------|------|--------------|------------|
| dev         | Any  | ❌ No        | Skipped    |
| staging     | 3-4  | ✅ Yes       | API + PKI  |
| prod        | 3-4  | ✅ Yes       | API + PKI  |

**Workflow will HALT if:**
- Jira CR ID not provided for staging/prod
- CR status is not "Approved"
- Required approver role not found
- PKI signature validation fails (if enabled)

---

## Script Usage

### validate-jira-approval.py

Validates Jira CR approval status with role enforcement.

```bash
# Basic validation
python3 scripts/validate-jira-approval.py \
  <AGENT_ID> \
  <CR_ID> \
  [REQUIRED_APPROVER_ROLE]

# Example
python3 scripts/validate-jira-approval.py \
  security-agent \
  CR-2025-1042 \
  "Change Manager"
```

**Exit Codes:**
- `0` - CR is approved and valid
- `1` - CR validation failed
- `2` - Missing environment variables or parameters

**Output:**
- Audit trail JSON: `/tmp/audit-<timestamp>-<id>.json`
- Audit ID file: `/tmp/jira-approval-audit-id.txt`

### setup-agent.sh

Agent setup script with Jira CR enforcement.

```bash
# Tier 3 deployment to production
./scripts/setup-agent.sh \
  --tier 3 \
  --name security-agent \
  --environment prod \
  --jira-cr-id CR-2025-1042 \
  --run-threat-model

# Tier 1 deployment (no CR needed)
./scripts/setup-agent.sh \
  --tier 1 \
  --name doc-analyzer \
  --environment dev
```

**Tier 3/4 Requirements:**
- `--jira-cr-id` required for staging/prod
- Jira validation runs automatically
- Threat modeling recommended (`--run-threat-model`)

### deploy-agents.sh

Bulk agent deployment with Jira CR validation.

```bash
# Deploy to production with Jira CR
./scripts/deploy-agents.sh prod CR-2025-1042

# Deploy to dev (no CR needed)
./scripts/deploy-agents.sh dev
```

**Features:**
- Validates Jira CR for staging/prod
- Runs governance checks per agent
- Generates audit trail with jira_reference
- Helm-based deployment

---

## Troubleshooting

### Issue: "Missing required environment variables"

**Solution:**
```bash
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_USER="your-email@company.com"
export JIRA_TOKEN="your-jira-api-token"
```

### Issue: "Jira authentication failed"

**Cause:** Invalid API token or permissions

**Solution:**
1. Regenerate API token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Verify user has permission to view CRs
3. Check Jira URL format (no trailing slash)

### Issue: "CR status is 'Pending', not 'Approved'"

**Cause:** CR not yet approved

**Solution:**
1. Go to Jira CR
2. Transition to "Approved" status
3. Re-run validation

### Issue: "Required approver role not found"

**Cause:** Approver field mapping not configured

**Solution:**
1. Check Jira custom field IDs in `validate-jira-approval.py:89-94`
2. Update field IDs to match your Jira instance
3. Use Jira API to list fields: `GET /rest/api/3/field`

### Issue: "PKI signature validation failed"

**Cause:** Invalid or missing signature

**Solutions:**
1. **Disable PKI enforcement** (development):
   ```bash
   export ENFORCE_PKI_VALIDATION="false"
   ```

2. **Generate and add signature** (production):
   ```bash
   python3 scripts/generate-pki-keys.py --sign \
     --cr-id CR-2025-1042 \
     --private-key ./pki-keys/change-manager.key
   ```

### Issue: "Webhook signature validation failed"

**Cause:** WEBHOOK_SECRET mismatch

**Solution:**
1. Check `WEBHOOK_SECRET` environment variable
2. Verify Jira webhook header: `X-Webhook-Signature`
3. Use same secret in both places

### Issue: "No approver information found in CR"

**Cause:** Custom field not configured

**Solution:**
1. This is a warning, not an error (status check still passes)
2. Configure custom approver field in Jira
3. Update field ID in `validate-jira-approval.py`

---

## Best Practices

### Security

1. **Store Secrets Securely**
   - Use AWS Secrets Manager, HashiCorp Vault, or GitHub Secrets
   - Never commit API tokens to version control
   - Rotate tokens every 90 days

2. **Enable PKI Signing**
   - Required for production deployments
   - Use hardware security modules (HSM) for private keys
   - Rotate signing keys quarterly

3. **Use TLS for Webhooks**
   - Always use HTTPS in production
   - Validate webhook signatures with HMAC
   - Use strong webhook secrets (32+ characters)

### Operational

1. **CR Naming Convention**
   - Use consistent pattern: `CR-YYYY-NNNN`
   - Include year for easier tracking
   - Sequential numbering per year

2. **Budget Allocation**
   - Always include budget in CR description
   - Monitor budget consumption
   - Alert at 80% threshold

3. **Audit Trail Retention**
   - Keep audit trails for 90+ days
   - Archive to S3 or similar
   - Enable audit log shipping to SIEM

4. **Monitoring**
   - Monitor webhook receiver health
   - Alert on failed validations
   - Track approval latency

---

## Related Documentation

- [Governance Policy](./GOVERNANCE-POLICY.md)
- [PAR Workflow Framework](./PAR-WORKFLOW-FRAMEWORK.md)
- [Quick Reference](./QUICK-REFERENCE.md)
- [Schema Documentation](../policies/schemas/)

---

## Support

For issues or questions:
- Review [Troubleshooting](#troubleshooting) section
- Check GitHub Issues
- Contact governance team

**Version:** 2.1
**Last Updated:** 2025-10-18
**Control Coverage:** APP-001, G-02, G-07
