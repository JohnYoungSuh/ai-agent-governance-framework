# APP-001: Jira Approval Gate for Tier 3/4 Deployments

Path: `examples/control-validation/APP-001-jira-approval.md`

## Control Description

APP-001 (Human Primacy) mandates that all Tier 3 (Operations) and Tier 4 (Architect) agent deployments to staging and production environments require explicit human approval via Jira Change Request (CR).

This control ensures:
1. **Human oversight** before autonomous agents access production systems
2. **Audit trail** linking deployments to approved CRs
3. **Role-based approvals** requiring appropriate authority (e.g., Change Manager)
4. **Budget enforcement** with token allocations specified in CR

---

## Implementation

### 1. Jira CR Creation

Before deploying a Tier 3/4 agent, create a Jira CR with:

**Required Fields:**
- **Summary**: Deployment of [AGENT_ID] to [ENVIRONMENT]
- **Description**: Include agent tier, purpose, and risk assessment
- **Custom Field - Budget Tokens**: Allocated token budget (e.g., 10000)
- **Custom Field - Controls**: List of applicable controls (e.g., APP-001, SEC-001, MI-003)
- **Approver**: Assign to Change Manager or appropriate role

**Example CR:**
```
CR-2025-1042: Deploy security-agent to Production

Description:
  Agent: security-agent
  Tier: 3 (Operations)
  Purpose: Automated vulnerability scanning and compliance monitoring
  Budget: 10,000 tokens
  Controls: APP-001, SEC-001, MI-003, MI-009, MI-020

  Risk Assessment:
  - STRIDE threat model completed (see attachment)
  - All Tier 3 mitigations implemented
  - Budget limit enforced via circuit breaker

Approver: John Smith (Change Manager)
Status: Approved
```

---

### 2. CI/CD Workflow Integration

The `.github/workflows/deploy-security-agent.yml` enforces Jira approval:

```yaml
jobs:
  # Stage 1: Jira Approval Gate
  jira-approval:
    runs-on: ubuntu-latest
    if: github.event.inputs.environment == 'staging' || github.event.inputs.environment == 'prod'
    steps:
      - uses: actions/checkout@v4

      - name: Validate Jira CR ID provided
        run: |
          if [ -z "${{ github.event.inputs.jira_cr_id }}" ]; then
            echo "❌ ERROR: Jira CR ID required for staging/prod deployments"
            exit 1
          fi

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

**Workflow requires:**
- `jira_cr_id` input parameter for staging/prod deployments
- Environment variables: `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN`
- Validation script exits with code 1 if CR is not approved

---

### 3. Validation Script Execution

When `validate-jira-approval.py` runs, it:

1. **Fetches CR** from Jira API: `GET /rest/api/3/issue/{cr_id}`
2. **Validates status** is "Approved" (not "Pending" or "Rejected")
3. **Verifies approver role** matches required role (e.g., "Change Manager")
4. **Extracts budget** from CR description or custom field
5. **Generates audit trail** conforming to `frameworks/audit-trail.json`
6. **Emits SIEM event** conforming to `policies/schemas/siem-event.json`

---

## Worked Example

### Scenario: Deploy security-agent to Production

#### Step 1: Create Jira CR

```bash
# Manual step in Jira UI or via API
CR ID: CR-2025-1042
Status: Approved
Approver: John Smith (Change Manager)
Budget: 10,000 tokens
```

#### Step 2: Trigger GitHub Actions Workflow

```bash
# Via GitHub UI or gh CLI
gh workflow run deploy-security-agent.yml \
  -f environment=prod \
  -f jira_cr_id=CR-2025-1042
```

#### Step 3: Jira Approval Validation

**Validation Script Output:**
```
==================================================
Jira Approval Validation (APP-001)
==================================================
Agent ID:              security-agent
Change Request:        CR-2025-1042
Required Approver:     Change Manager
==================================================

🔍 Fetching Jira CR details...
✅ CR fetched successfully

📋 CR Status: Approved
✅ CR Status Verified: Approved

👥 Approvers found: 1
✅ Required approver role verified: Change Manager

💰 Budget Tokens Allocated: 10,000

✅ VALIDATION PASSED
==================================================
Jira CR CR-2025-1042 is approved for deployment
Agent: security-agent
Audit ID: audit-1729180800-3a4b5c6d
Audit Trail: /tmp/audit-1729180800-3a4b5c6d.json
==================================================
```

#### Step 4: Generated Audit Trail

**File:** `/tmp/audit-1729180800-3a4b5c6d.json`

```json
{
  "audit_id": "audit-1729180800-3a4b5c6d",
  "timestamp": "2025-10-17T14:20:00Z",
  "actor": "ci-cd-pipeline",
  "action": "jira_approval_validation",
  "workflow_step": "APP-001",
  "jira_reference": {
    "cr_id": "CR-2025-1042",
    "approver_role": "Change Manager",
    "status": "Approved",
    "budget_tokens": 10000,
    "controls": ["APP-001", "G-02", "G-07"],
    "validated_at": "2025-10-17T14:20:00Z"
  },
  "inputs": {
    "agent_id": "security-agent",
    "cr_id": "CR-2025-1042",
    "required_approver_role": "Change Manager",
    "jira_url": "https://your-company.atlassian.net"
  },
  "outputs": {
    "validation_result": "pass",
    "cr_status": "Approved",
    "approval_verified": true,
    "approvers_found": 1
  },
  "policy_controls_checked": ["APP-001", "G-02", "G-07"],
  "compliance_result": "pass",
  "evidence_hash": "sha256:a3f5e8d9c2b1a0f9e8d7c6b5a4f3e2d1...",
  "auditor_agent": "jira-approval-validator-py"
}
```

#### Step 5: Generated SIEM Event

**SIEM Event (correlated via `siem_event_id == audit_id`):**

```json
{
  "siem_event_id": "audit-1729180800-3a4b5c6d",
  "timestamp": "2025-10-17T14:20:00Z",
  "source": "jira",
  "control_id": "APP-001",
  "agent_id": "security-agent",
  "tier": 3,
  "jira_reference": {
    "cr_id": "CR-2025-1042",
    "approver_role": "Change Manager",
    "status": "Approved",
    "approved_at": "2025-10-17T14:15:00Z"
  },
  "payload": {
    "action": "jira_approval_validation",
    "validation_result": "pass",
    "budget_tokens": 10000
  },
  "compliance_result": "pass",
  "ocsf_mapping": {
    "category_uid": 6,
    "class_uid": 6001,
    "severity_id": 1
  },
  "metadata": {
    "environment": "prod",
    "workflow_id": "github-actions-12345",
    "correlation_id": "trace-abc123def456"
  }
}
```

**OCSF Mapping Details:**
- **category_uid: 6** - Application Activity
- **class_uid: 6001** - Application Lifecycle (deployment approval)
- **severity_id: 1** - Informational (successful approval validation)

---

## Correlation Query Example

To correlate audit-trail → SIEM event → Jira CR:

```sql
-- Query SIEM for all deployments linked to Jira CR
SELECT
  s.siem_event_id,
  s.timestamp,
  s.agent_id,
  s.jira_reference.cr_id,
  s.jira_reference.approver_role,
  s.compliance_result,
  s.metadata.environment
FROM siem_events s
WHERE s.control_id = 'APP-001'
  AND s.jira_reference.cr_id = 'CR-2025-1042'
  AND s.compliance_result = 'pass'
ORDER BY s.timestamp DESC;
```

**Result:**
```
siem_event_id              | timestamp            | agent_id        | cr_id         | approver_role  | compliance_result | environment
---------------------------|----------------------|-----------------|---------------|----------------|-------------------|------------
audit-1729180800-3a4b5c6d  | 2025-10-17T14:20:00Z | security-agent  | CR-2025-1042  | Change Manager | pass              | prod
```

---

## Governance Enforcement Points

| Checkpoint | Enforcement Mechanism | Failure Action |
|------------|----------------------|----------------|
| **G-02: Approval Enforcement** | `jira-approval` job in CI/CD blocks deployment if CR not approved | Exit code 1, workflow fails |
| **G-07: Jira Integration** | `validate-jira-approval.py` queries Jira API for status and approver role | Exit code 1 if status ≠ Approved or role missing |
| **APP-001: Human Primacy** | Workflow requires `jira_cr_id` input for staging/prod | Exit code 1 if CR ID not provided |
| **Audit Trail** | Audit entry written to `/tmp/audit-*.json` with Jira CR correlation | Uploaded as GitHub Actions artifact (90-day retention) |
| **SIEM Correlation** | SIEM event includes `jira_reference` object with CR details | Queryable for compliance reporting |

---

## Failure Scenarios

### Scenario 1: CR Not Approved

```bash
gh workflow run deploy-security-agent.yml \
  -f environment=prod \
  -f jira_cr_id=CR-2025-1043  # Status = Pending
```

**Output:**
```
❌ FAILED: CR status is 'Pending', not 'Approved'

GOVERNANCE VIOLATION:
  Control:     APP-001 (Human Primacy)
  Requirement: All Tier 3/4 deployments require approved Jira CR
  Current:     CR CR-2025-1043 has status 'Pending'
  Action:      Update CR to 'Approved' status before deployment
```

**Result:** Workflow exits with code 1, deployment blocked.

---

### Scenario 2: Missing Jira CR ID

```bash
gh workflow run deploy-security-agent.yml \
  -f environment=prod
  # jira_cr_id not provided
```

**Output:**
```
❌ ERROR: Jira CR ID is required for staging/prod deployments (Tier 3)

GOVERNANCE VIOLATION:
  Control:     APP-001 (Human Primacy), G-02 (Approval Enforcement)
  Requirement: All Tier 3/4 deployments to staging/prod require Jira CR approval
  Action:      Provide jira_cr_id input parameter with approved CR
```

**Result:** Workflow exits with code 1 before validation script runs.

---

### Scenario 3: Approver Role Missing

```bash
# CR approved by developer instead of Change Manager
```

**Output:**
```
❌ FAILED: Required approver role 'Change Manager' not found

GOVERNANCE VIOLATION:
  Control:     APP-001 (Human Primacy)
  Requirement: CR must be approved by Change Manager
  Current:     Approver role not found in CR CR-2025-1042
```

**Result:** Workflow exits with code 1, deployment blocked.

---

## Configuration

### Required GitHub Secrets

Add to repository or organization secrets:

```yaml
JIRA_URL: https://your-company.atlassian.net
JIRA_USER: ci-cd-bot@company.com
JIRA_TOKEN: <Jira API token>
```

**To generate Jira API token:**
1. Log in to Jira
2. Go to Account Settings → Security → API Tokens
3. Create new token
4. Store in GitHub Secrets

---

### Required Jira Custom Fields

| Field Name | Field ID | Type | Purpose |
|------------|----------|------|---------|
| Budget Tokens | `customfield_10101` | Number | Token budget allocation |
| Controls | `customfield_10102` | Multi-select | Applicable governance controls |
| Approvers | `customfield_10100` | User Picker | Approver information |

**Note:** Adjust field IDs in `validate-jira-approval.py` based on your Jira instance configuration.

---

## Testing

### Test with Mock Jira Server

```bash
# Start mock Jira server for testing
docker run -d -p 8080:8080 \
  -e JIRA_MOCK_CR_ID=CR-2025-TEST \
  -e JIRA_MOCK_STATUS=Approved \
  mock-jira-server

# Run validation script against mock
export JIRA_URL=http://localhost:8080
export JIRA_USER=test
export JIRA_TOKEN=test

./scripts/validate-jira-approval.py security-agent CR-2025-TEST "Change Manager"
```

### Expected Output:
```
✅ VALIDATION PASSED
Jira CR CR-2025-TEST is approved for deployment
```

---

## Compliance Mapping

| Framework | Control Reference | Requirement |
|-----------|------------------|-------------|
| **NIST AI RMF** | GOVERN-1.1 | Policies for AI system deployment require human oversight |
| **ISO/IEC 42001** | 6.1.2 | Risk assessment and approval before AI system deployment |
| **SOC 2 Type II** | CC6.1 | Logical access to production systems requires authorization |
| **MITRE ATLAS** | AML.T0043 | Prevent unauthorized model deployment |

---

## Metrics & Reporting

### Dashboard Query: Approval Velocity

```sql
SELECT
  DATE_TRUNC('day', timestamp) AS date,
  COUNT(*) AS approvals,
  AVG(EXTRACT(EPOCH FROM (timestamp - cr_created_at)) / 3600) AS avg_approval_time_hours
FROM siem_events
WHERE control_id = 'APP-001'
  AND compliance_result = 'pass'
GROUP BY date
ORDER BY date DESC
LIMIT 30;
```

### Alert: Deployment Without Approval

```yaml
# Prometheus alert rule
- alert: DeploymentWithoutJiraApproval
  expr: |
    increase(deployments_total{tier="3", environment="prod"}[5m]) > 0
    unless
    increase(jira_approvals_total{control_id="APP-001"}[10m]) > 0
  for: 1m
  labels:
    severity: critical
    control_id: APP-001
  annotations:
    summary: "Tier 3 production deployment without Jira approval detected"
    description: "Deployment to {{ $labels.agent_id }} occurred without corresponding APP-001 validation"
```

---

## References

- **Control Schema**: `frameworks/audit-trail.json`
- **SIEM Schema**: `policies/schemas/siem-event.json`
- **Validation Script**: `scripts/validate-jira-approval.py`
- **CI/CD Workflow**: `.github/workflows/deploy-security-agent.yml`
- **Jira Integration Guide**: `workflows/PAR-PROTO/integrations/jira-integration.md`

---

**Document Version:** 1.0
**Last Updated:** 2025-10-17
**Control Owner:** Security & Compliance Team
