# Terraform Automation for AI Ops Agent

This Terraform configuration deploys a **Tier 3 Operations AI agent** with comprehensive governance controls, integrated with GitHub for automated workflows.

## Overview

This infrastructure implements the **AI Agent Governance Framework v2.0** with:

- **18 Risk Controls** (RI-001 to RI-018) addressed
- **21 Mitigation Controls** (MI-001 to MI-021) implemented
- **4-Tier Agent Classification** system enforced
- **Compliance mapping** for GDPR, SOX, EU AI Act
- **Complete audit trail** with 7-year retention
- **GitHub Actions integration** for CI/CD

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│  ├─ Workflows (.github/workflows/ai-ops-agent.yml)         │
│  └─ Webhook → API Gateway → Lambda                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS Infrastructure                        │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  IAM Role   │  │   Secrets    │  │  CloudWatch  │      │
│  │  (MI-020)   │  │  Manager     │  │  Logs/Metrics│      │
│  │  Tier-based │  │  (MI-003)    │  │  (MI-004)    │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │         DynamoDB Audit Trail (MI-019)            │      │
│  │  ├─ audit_id, timestamp, actor, action           │      │
│  │  ├─ compliance_result, policy_controls_checked   │      │
│  │  └─ Stream → Lambda → S3 Archive (7 years)      │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │    Cost Monitoring & Alerting (MI-009, MI-021)   │      │
│  │  ├─ Daily budget alerts (50%, 75%, 90%)          │      │
│  │  ├─ Circuit breaker at 90% budget                │      │
│  │  └─ SNS notifications                             │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │      Governance Records (MI-018)                  │      │
│  │  ├─ Control implementations                       │      │
│  │  ├─ Compliance mappings                           │      │
│  │  └─ Evidence storage (S3)                         │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

1. **Terraform** >= 1.5.0
2. **AWS CLI** configured with credentials
3. **GitHub** personal access token with repo and workflow permissions
4. **LLM API key** (Anthropic, OpenAI, or AWS Bedrock)

---

## Quick Start

### 1. Clone and Configure

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your configuration:

```hcl
agent_name            = "my-ai-ops-agent"
agent_tier            = "tier3-operations"
github_organization   = "your-org"
github_repository     = "your-repo"
llm_model_provider    = "anthropic"
llm_model_version     = "claude-sonnet-4-5-20250929"
daily_cost_budget     = 100.0
monthly_cost_budget   = 2000.0
```

### 2. Set Sensitive Variables

```bash
export TF_VAR_github_token="ghp_xxxxx"
export TF_VAR_slack_webhook_url="https://hooks.slack.com/services/xxxxx"
```

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Review Plan

```bash
terraform plan
```

### 5. Deploy Infrastructure

```bash
terraform apply
```

### 6. Store Secrets

After deployment, store your LLM API key:

```bash
aws secretsmanager put-secret-value \
  --secret-id my-ai-ops-agent-llm-api-key \
  --secret-string "sk-ant-xxxxx"

aws secretsmanager put-secret-value \
  --secret-id my-ai-ops-agent-github-token \
  --secret-string "ghp_xxxxx"
```

### 7. Initialize Governance Records

```bash
aws lambda invoke \
  --function-name my-ai-ops-agent-governance-initializer \
  response.json
```

---

## Governance Controls Implemented

### Critical Priority (🔴)

| Control | Description | Status |
|---------|-------------|--------|
| **MI-001** | Data Leakage Prevention (PII redaction) | ✅ Implemented |
| **MI-003** | Secrets Management (AWS Secrets Manager) | ✅ Implemented |
| **MI-009** | Cost Monitoring & Alerting | ✅ Implemented |
| **MI-020** | Tier Enforcement (IAM policies) | ✅ Implemented |
| **MI-021** | Budget Limits & Circuit Breakers | ✅ Implemented |

### High Priority (🟡)

| Control | Description | Status |
|---------|-------------|--------|
| **MI-002** | Input Filtering & Prompt Injection Detection | ⚠️ Configurable |
| **MI-004** | Observability (CloudWatch, X-Ray) | ✅ Implemented |
| **MI-006** | Access Controls (Least Privilege) | ✅ Implemented |
| **MI-007** | Human Review (Tier-based percentages) | ✅ Implemented |
| **MI-019** | Comprehensive Audit Trails | ✅ Implemented |

---

## Compliance Mapping

This infrastructure addresses:

- **NIST AI RMF**: GOVERN, MAP, MEASURE, MANAGE functions
- **ISO/IEC 42001**: AI management system requirements
- **Microsoft Responsible AI**: 7 core principles
- **OWASP Top 10 for LLMs**: All 10 risks covered
- **GDPR**: Data protection and privacy controls
- **SOX**: Audit trail and financial controls
- **EU AI Act**: Transparency and governance requirements

See `outputs/compliance-mapping-{agent_name}.yaml` for detailed mapping.

---

## Files Structure

```
terraform/
├── main.tf                      # Main Terraform configuration
├── variables.tf                 # Input variables
├── outputs.tf                   # Output values
├── secrets.tf                   # Secrets management (MI-003)
├── iam.tf                       # IAM roles and policies (MI-006, MI-020)
├── monitoring.tf                # CloudWatch monitoring (MI-004, MI-009)
├── audit-trail.tf               # Audit trail infrastructure (MI-019)
├── github-integration.tf        # GitHub Actions integration
├── governance-compliance.tf     # Governance records (MI-018)
├── terraform.tfvars.example     # Example configuration
├── README.md                    # This file
├── templates/
│   └── github-workflow.yml.tpl  # GitHub Actions workflow template
└── lambda/                      # Lambda function code
    ├── audit-archiver.zip       # Audit trail archiver
    ├── webhook-handler.zip      # GitHub webhook handler
    └── governance-initializer.zip # Governance initializer
```

---

## Cost Estimation

### Infrastructure Costs (Monthly)

| Resource | Estimated Cost |
|----------|---------------|
| CloudWatch Logs (10 GB/month) | ~$5 |
| DynamoDB (on-demand) | ~$10-50 |
| S3 Storage (audit archive) | ~$1-10 |
| Lambda invocations | ~$1-5 |
| Secrets Manager | ~$1 |
| KMS | ~$1 |
| **Total Infrastructure** | **~$20-75/month** |

### Agent Costs (Variable)

| Usage | LLM Costs (Claude Sonnet 4.5) |
|-------|-------------------------------|
| 100 requests/day | ~$30-50/month |
| 500 requests/day | ~$150-250/month |
| 1000 requests/day | ~$300-500/month |

**Total estimated cost**: $50-$575/month depending on usage.

---

## Monitoring and Alerts

### CloudWatch Dashboard

Access your agent dashboard:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=my-ai-ops-agent-dashboard
```

### Cost Alerts (MI-009, MI-021)

Budget alerts trigger at:
- **50%**: Informational notification
- **75%**: Warning - review usage
- **90%**: Critical - requires approval to continue
- **100%**: Circuit breaker - agent paused

### Audit Trail Queries (MI-019)

Query audit trails using CloudWatch Insights:

```sql
fields @timestamp, audit_id, actor, action, compliance_result
| filter event_type = "audit_trail"
| sort @timestamp desc
| limit 100
```

---

## Security Best Practices

### ✅ Implemented

- **Encryption at rest**: All data stores use KMS encryption
- **Encryption in transit**: TLS/HTTPS enforced
- **Secrets management**: AWS Secrets Manager with rotation
- **Least privilege**: IAM policies enforce tier-based permissions
- **Audit trail**: Complete logging with 7-year retention
- **Network security**: Can be deployed in VPC

### ⚠️ Recommended Enhancements

- Deploy in VPC for network isolation (set `vpc_id` variable)
- Enable AWS GuardDuty for threat detection
- Implement LLM-as-Judge validation (MI-015)
- Set up RAG security controls (MI-014)
- Enable bias testing (MI-012)

---

## GitHub Actions Integration

### Workflow Triggers

The agent workflow triggers on:
- **Push** to main/develop branches
- **Pull requests** to main
- **Manual dispatch** with action selector
- **Schedule** (optional, for cost reports)

### Workflow Jobs

1. **governance-check**: Validates tier permissions, budgets, secrets
2. **security-scan**: Secrets scanning, PII detection, vulnerability scan
3. **agent-deployment**: Deploys agent with human review gate
4. **cost-tracking**: Generates cost reports and budget compliance
5. **audit-trail-review**: Queries audit trail and generates compliance reports

---

## Validation Against Framework

Run validation checklist:

```bash
# Review governance validation report
cat outputs/governance-validation-my-ai-ops-agent.md

# Review compliance mapping
cat outputs/compliance-mapping-my-ai-ops-agent.yaml
```

### NIST AI RMF Alignment

- ✅ **GOVERN**: Clear accountability, policies, risk tolerance
- ✅ **MAP**: Context, capabilities, data quality requirements
- ✅ **MEASURE**: Performance metrics, cost tracking, incident tracking
- ✅ **MANAGE**: Risk mitigations, incident response, continuous monitoring

### OWASP Top 10 for LLMs Coverage

- ✅ **LLM01**: Prompt Injection (MI-002, MI-017)
- ✅ **LLM04**: Model DoS (MI-005, MI-021)
- ✅ **LLM06**: Sensitive Info Disclosure (MI-001)
- ✅ **LLM08**: Excessive Agency (MI-020)
- ✅ **LLM09**: Overreliance (MI-007 human review)

---

## Troubleshooting

### Issue: Terraform apply fails with "AccessDenied"

**Solution**: Ensure your AWS credentials have permissions to create IAM roles, KMS keys, and other resources.

### Issue: GitHub webhook not receiving events

**Solution**: Check API Gateway logs and verify webhook secret in GitHub settings.

### Issue: Cost alerts not triggering

**Solution**: Enable cost allocation tags and wait 24 hours for billing data to populate.

### Issue: Audit trail not logging

**Solution**: Verify DynamoDB table exists and Lambda has correct IAM permissions.

---

## Updating the Infrastructure

### Change Agent Configuration

Edit `terraform.tfvars` and run:

```bash
terraform plan
terraform apply
```

### Update LLM Model Version (MI-010)

1. Update `llm_model_version` in `terraform.tfvars`
2. Test in dev environment first
3. Run full acceptance tests
4. Apply to production:

```bash
terraform apply -var="llm_model_version=claude-sonnet-4-5-20251201"
```

### Add New Risk Control

1. Add control ID to `risk_controls_required` list
2. Implement control in application code
3. Update governance records
4. Run compliance validation

---

## Cleanup

To destroy all resources:

```bash
# WARNING: This will delete all data including audit trails
terraform destroy
```

**Note**: Audit trail archives in S3 Glacier may have minimum storage duration requirements.

---

## Support and Contributing

- **Framework Documentation**: See `/docs` folder
- **Issues**: https://github.com/suhlabs/ai-agent-governance-framework/issues
- **Validation Checklist**: `/VALIDATION-CHECKLIST.md`

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Generated by AI Agent Governance Framework v2.0**
**Terraform infrastructure for production-grade AI agents**
