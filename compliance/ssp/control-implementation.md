# Control Implementation Statements

> Detailed implementation statements for NIST 800-53 Rev 5 controls
> AI Agent Governance Framework (AAGF)

**Document Version**: 1.0
**Last Updated**: 2025-10-18
**System**: AI Agent Governance Framework (AAGF-PROD-001)

---

## How to Use This Document

This document provides detailed **control implementation statements** for each NIST 800-53 control applicable to AAGF. Each entry includes:

- **Control Number and Title**: Official NIST designation
- **CCI**: DISA Control Correlation Identifier
- **Implementation Status**: Implemented, Partially Implemented, Planned, Not Applicable
- **Control Description**: What the control requires (from NIST SP 800-53)
- **Implementation Statement**: How AAGF implements this control
- **Responsible Role**: Who maintains this control
- **Evidence**: Where to find proof of implementation

**Format**:
```
## CONTROL-ID: Control Title
CCI: CCI-XXXXXX | Status: ✅ Implemented | Owner: [Role]

### Control Requirement (NIST)
[Official control statement from NIST 800-53]

### AAGF Implementation
[How this system implements the control]

### Evidence
- Location: [File path or system]
- Type: [Configuration, logs, documentation]
```

---

## Critical Controls (Must Implement Before Production)

---

## AC-6: Least Privilege
**CCI**: CCI-002220 | **Status**: ✅ Implemented | **Owner**: Security Team

### Control Requirement (NIST)
*Employ the principle of least privilege, allowing only authorized accesses for users (or processes acting on behalf of users) that are necessary to accomplish assigned organizational tasks.*

### AAGF Implementation

**Part (a)**: Authorize access to security functions and security-relevant information

AAGF implements tier-based privilege separation for AI agents:

| Tier | Privileges | Justification |
|------|-----------|---------------|
| **Tier 1** (Development) | Read-only access to code repositories, suggest changes via PRs | Lowest risk; cannot modify production |
| **Tier 2** (Staging) | Read/write to dev environments, read-only production | Intermediate risk; limited production exposure |
| **Tier 3** (Production) | Write access to production with human approval | High risk; all writes require AC-6-AI-2 approval |
| **Tier 4** (Strategic) | Read-only across all environments | Planning and analysis only |

**Technical Implementation**:
```yaml
# agents/tier1/permissions.yaml
agent_tier: 1
permissions:
  repositories:
    - resource: "github.com/org/*"
      actions: ["read", "create_pr"]
  production:
    - resource: "*"
      actions: ["deny"]
```

**Part (b)**: Require users to use the lowest level of privilege necessary

- All AI agents assigned dedicated service accounts (AC-2)
- Permissions explicitly granted; no default "admin" access
- Privilege escalation requires:
  1. JIRA change ticket (CM-3)
  2. Multi-person approval (developer + security admin)
  3. Audit log entry (AU-3-AI-1)
  4. Time-bound access (automatic expiration after 24 hours)

### Evidence
- **Configuration**: `agents/tier{1,2,3,4}/permissions.yaml`
- **Code**: `src/access-control/rbac.py` implements permission checks
- **Logs**: `audit-logs/access-control/*.json` (AU-3 format)
- **Policy**: `policies/security-policies.md` § AC-6

---

## AC-6(1): Authorize Access to Security Functions
**CCI**: CCI-002233 | **Status**: ✅ Implemented | **Owner**: Security Team

### Control Requirement (NIST)
*Authorize access for individuals and roles to: (a) Security functions; and (b) Security-relevant information.*

### AAGF Implementation

Only Tier 3+ agents can modify security configurations, with restrictions:

**Security Functions** (require elevated privileges):
- Modifying access control policies
- Changing audit log retention settings (AU-11)
- Updating data classification rules (SC-4)
- Rotating credentials (IA-5)
- Changing SIEM alert thresholds (SI-4)

**Authorization Matrix**:
| Function | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Human Admin |
|----------|--------|--------|--------|--------|-------------|
| Read security config | ❌ | ❌ | ✅ | ✅ | ✅ |
| Modify access controls | ❌ | ❌ | ✅ (with approval) | ❌ | ✅ |
| Rotate credentials | ❌ | ❌ | ✅ (with approval) | ❌ | ✅ |
| Modify audit settings | ❌ | ❌ | ❌ | ❌ | ✅ (CISO only) |

**Multi-Person Approval Requirement**:
- Security function changes require separate approvals from:
  1. Development lead (technical review)
  2. Security administrator (security review)
  3. No self-approval permitted

### Evidence
- **Code**: `src/access-control/security-functions.py`
- **Workflow**: `frameworks/approval-workflows.yml` § security_function_changes
- **Audit Trail**: All security function calls logged to `audit-logs/security-events/*.json`

---

## AC-6-AI-1: AI Agent Tier Enforcement (AI Extension)
**CCI**: CCI-AI-005 | **Status**: ✅ Implemented | **Owner**: Platform Engineering

### Control Requirement (Custom AI Extension)
*Enforce tier-based privilege boundaries for AI agents to prevent unauthorized escalation and ensure appropriate human oversight based on risk level.*

### AAGF Implementation

**Tier Enforcement Mechanisms**:

1. **Configuration-Based Enforcement**:
```yaml
# Agent deployment manifest
apiVersion: aagf.io/v1
kind: AIAgent
metadata:
  name: prod-deploy-agent
spec:
  tier: 3  # Cannot be changed without redeployment
  maxPrivilegeLevel: "write:production"
  requiresApproval: true
```

2. **Runtime Validation**:
```python
def validate_action(agent_id: str, action: str, resource: str) -> bool:
    agent_tier = get_agent_tier(agent_id)
    required_tier = get_required_tier_for_action(action, resource)

    if agent_tier < required_tier:
        audit_log(
            event="tier_violation_blocked",
            agent_id=agent_id,
            agent_tier=agent_tier,
            required_tier=required_tier,
            control="AC-6-AI-1",
            cci="CCI-AI-005"
        )
        raise PermissionDenied("Insufficient tier level")

    return True
```

3. **Immutable Tier Assignment**:
- Agent tier defined in Kubernetes ConfigMap (immutable)
- Tier changes require new deployment + CM-3 change control
- Cannot be modified at runtime

**Tier Boundary Violations**:
- Logged as security events (SI-4)
- Trigger SIEM alert for investigation
- Agent automatically suspended pending review

### Evidence
- **Deployment Configs**: `deployments/agents/tier{1,2,3,4}/*.yaml`
- **Runtime Code**: `src/tier-enforcement/validator.py`
- **Audit Logs**: `audit-logs/tier-violations/*.json`
- **SIEM Rules**: `frameworks/observability-config.yml` § tier_boundary_alert

---

## AC-6-AI-2: Human-in-the-Loop Authorization (AI Extension)
**CCI**: CCI-AI-006 | **Status**: ✅ Implemented | **Owner**: DevOps Team

### Control Requirement (Custom AI Extension)
*Require human approval for AI agent actions that pose significant risk to confidentiality, integrity, or availability.*

### AAGF Implementation

**Actions Requiring Human Approval**:

| Action Category | Examples | Approval SLA | Approver Role |
|-----------------|----------|--------------|---------------|
| **Production Write** | Deploy, config change, database migration | 4 hours | DevOps Lead |
| **Security Change** | Modify firewall, update IAM policy | 2 hours | Security Admin |
| **Data Deletion** | Delete records, purge logs | 1 hour | Data Owner + Manager |
| **Cost >$100** | Large batch jobs, extensive LLM calls | 24 hours | Finance Approver |

**Approval Workflow**:

1. **Agent Requests Approval**:
```python
approval_request = {
    "agent_id": "tier3-prod-deploy-001",
    "action": "deploy_application",
    "target": "production/web-app",
    "risk_level": "high",
    "justification": "Security patch deployment",
    "ticket": "JIRA-12345"
}
create_jira_approval_task(approval_request)
```

2. **Human Reviews**:
   - JIRA ticket created automatically
   - Approver sees: agent intent, risk level, test results, rollback plan
   - Approval options: Approve, Deny, Request Changes

3. **Agent Polls for Decision**:
   - Maximum wait: 24 hours
   - If timeout: action cancelled, alert sent to manager
   - If approved: action executes with full AU-3-AI-1 audit logging

4. **Post-Action Validation**:
   - Human spot-checks sample of completed actions (10% random)
   - Feedback loop improves agent quality over time

**Emergency Override**:
- On-call engineer can approve critical actions via CLI
- Requires MFA (IA-2(1))
- All emergency overrides reviewed next business day

### Evidence
- **Workflow Engine**: `src/approvals/human-in-loop.py`
- **JIRA Integration**: `integrations/jira/approval-workflow.py`
- **Audit Logs**: `audit-logs/approvals/*.json` (includes approval_ticket, approver_id)
- **Policy**: `policies/compliance-policies.md` § AC-6-AI-2

---

## AU-2: Event Logging
**CCI**: CCI-000130 | **Status**: ✅ Implemented | **Owner**: Security Operations

### Control Requirement (NIST)
*a. Identify the types of events that the system is capable of logging in support of the audit function*
*b. Coordinate the event logging function with other organizational entities*
*c. Provide a rationale for why the event types selected for logging are deemed to be adequate*

### AAGF Implementation

**Part (a)**: Event types logged

AAGF logs the following event categories per NIST SP 800-92:

1. **Authentication Events** (IA family):
   - Agent service account authentication (success/failure)
   - Secrets Manager credential checkout/checkin
   - API token usage

2. **Authorization Events** (AC family):
   - Permission grants/denials
   - Tier boundary violations (AC-6-AI-1)
   - Privilege escalation attempts

3. **Agent Actions** (AU-3-AI-1):
   - All CRUD operations on production systems
   - Code deployments and rollbacks
   - Configuration changes (CM-3)
   - JIRA ticket creation/updates

4. **Data Access** (SC-4):
   - Classification level of data accessed
   - PII/secrets redaction events
   - Cross-classification boundary access attempts

5. **Security Events** (SI-4):
   - Prompt injection detection (RA-9-AI-2)
   - Hallucination alerts (SI-7-AI-1)
   - DLP violations (SC-4-AI-1)
   - Unusual behavior anomalies

6. **Cost Events** (SA-15-AI-1):
   - LLM API token consumption per agent
   - Budget threshold exceedances (50%, 75%, 90%, 100%)
   - Cost per task/operation

7. **System Events**:
   - Agent start/stop
   - Health check failures
   - Dependency failures (LLM API outages)

**Part (b)**: Coordination with organizational entities

- **Security Operations Center (SOC)**: Receives real-time SIEM alerts
- **Compliance Team**: Monthly access to audit logs for review
- **External Auditors**: Read-only API access to audit trail
- **Privacy Office**: Notified of PII processing events
- **Finance**: Daily cost reports (SA-15-AI-1)

**Part (c)**: Rationale for event selection

Event types selected based on:
- **NIST SP 800-92** recommendations for application security logging
- **Compliance requirements**: FedRAMP, SOC 2, PCI-DSS, HIPAA
- **AI-specific risks**: Hallucination, prompt injection, data leakage (from `policies/risk-catalog.md`)
- **Incident response needs**: Support forensic investigation per IR-4

### Evidence
- **Event Catalog**: `frameworks/observability-config.yml` § log_event_types
- **Log Samples**: `audit-logs/samples/` (sanitized examples)
- **SIEM Configuration**: `configs/siem/splunk-inputs.conf`
- **Policy**: `policies/logging-policy.md` § AU-2

---

## AU-3: Content of Audit Records
**CCI**: CCI-000131 | **Status**: ✅ Implemented | **Owner**: Security Operations

### Control Requirement (NIST)
*Ensure that audit records contain information that establishes the following:*
*a. What type of event occurred*
*b. When the event occurred*
*c. Where the event occurred*
*d. Source of the event*
*e. Outcome of the event*
*f. Identity of individuals, subjects, or objects associated with the event*

### AAGF Implementation

All audit records conform to `policies/schemas/audit-trail.json` and include:

```json
{
  "siem_event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-18T14:32:01.123Z",
  "event_type": "agent_action",
  "log_source": "tier3-prod-deploy-agent-001",
  "source_ip": "10.0.1.50",
  "agent_id": "tier3-prod-deploy-agent-001",
  "agent_tier": 3,
  "action": "deploy_application",
  "target": "production/web-app-v2.1.0",
  "approver_id": "alice@example.com",
  "approval_ticket": "JIRA-12345",
  "classification": "INTERNAL",
  "input_params": {
    "version": "2.1.0",
    "environment": "production",
    "strategy": "rolling_update"
  },
  "output_summary": "Deployment successful, 3 pods updated, 0 errors",
  "outcome": "success",
  "cost_tokens": 15420,
  "cost_usd": 0.23,
  "model_version": "gpt-4-2024-11-20",
  "control_references": ["CM-3", "CM-3-AI-1", "AU-3-AI-1"]
}
```

**Mapping to AU-3 Requirements**:
- **(a) What**: `event_type`, `action` fields
- **(b) When**: `timestamp` in ISO-8601 UTC with milliseconds (AU-8)
- **(c) Where**: `target`, `source_ip`, `log_source` fields
- **(d) Source**: `agent_id`, `log_source` fields
- **(e) Outcome**: `outcome` field (success/failure/partial)
- **(f) Identity**: `agent_id`, `approver_id` fields

### Evidence
- **Schema**: `policies/schemas/audit-trail.json`
- **Implementation**: `src/audit/logger.py` § AuditLogger class
- **Sample Logs**: `audit-logs/samples/` (redacted for sensitivity)
- **Validation**: All logs validated against schema on write

---

## AU-3-AI-1: AI Decision Auditability (AI Extension)
**CCI**: CCI-AI-008 | **Status**: ✅ Implemented | **Owner**: ML Engineering

### Control Requirement (Custom AI Extension)
*Log sufficient information to reproduce AI agent reasoning and validate decisions for audit, compliance, and incident investigation.*

### AAGF Implementation

Extended audit records for AI decisions include:

```json
{
  // ... standard AU-3 fields ...

  // AU-3-AI-1 extensions
  "model_version": "gpt-4-2024-11-20",
  "model_provider": "openai",
  "prompt_template": "deploy_application_v1.2",
  "context_included": [
    "docs/deployment-guide.md",
    "history/last-3-deployments.json"
  ],
  "model_params": {
    "temperature": 0.1,
    "max_tokens": 2000,
    "top_p": 0.95
  },
  "reasoning_chain": [
    "1. Verified version 2.1.0 exists in artifact registry",
    "2. Checked deployment health prerequisites: all passing",
    "3. Selected rolling update strategy based on low-risk change",
    "4. Validated rollback plan is documented in JIRA-12345"
  ],
  "confidence_score": 0.94,
  "citations": [
    "deployment-guide.md#rolling-updates",
    "JIRA-12345 § rollback plan"
  ],
  "validation_result": {
    "hallucination_check": "passed",
    "fact_checker": "validated_against_artifact_registry",
    "llm_as_judge_score": 0.91
  },
  "input_hash": "sha256:abc123...",
  "reproducibility": {
    "model_snapshot": "s3://model-versions/gpt-4-2024-11-20.json",
    "context_hash": "sha256:def456...",
    "seed": 42
  }
}
```

**Reproducibility Guarantee**:
- Exact model version pinned (CM-3-AI-1)
- All context documents hashed and stored
- Model parameters logged
- Random seed captured (for deterministic models)

**Use Cases**:
1. **Compliance Audit**: Auditor can replay exact decision and verify correctness
2. **Incident Investigation**: Understand why agent made specific choice
3. **Model Drift Detection**: Compare reasoning quality over time (CA-7-AI-1)
4. **Bias Analysis**: Review reasoning for discriminatory patterns (RA-5-AI-1)

### Evidence
- **Schema**: `policies/schemas/audit-trail.json` § AU-3-AI-1 section
- **Implementation**: `src/audit/ai-logger.py` § AIDecisionLogger class
- **Sample**: `audit-logs/samples/ai-decision-sample.json`
- **Validation Tool**: `scripts/replay-decision.py` (reconstructs decision from log)

---

## AU-9: Protection of Audit Information
**CCI**: CCI-000162 | **Status**: ✅ Implemented | **Owner**: Security Operations

### Control Requirement (NIST)
*a. Protect audit information and audit logging tools from unauthorized access, modification, and deletion*
*b. Alert system administrators and security personnel in the event of unauthorized access*

### AAGF Implementation

**Part (a)**: Protection mechanisms

1. **Append-Only Storage** (AU-9(2)):
```yaml
# S3 bucket configuration
audit-logs-bucket:
  name: "aagf-audit-logs-prod"
  versioning: enabled
  object_lock:
    mode: GOVERNANCE  # Prevents deletion without special permission
    retention:
      days: 730  # 2 years minimum (AU-11)
  encryption:
    type: "aws:kms"
    key_id: "arn:aws:kms:us-east-1:123456789:key/audit-key"
  access_control:
    write_roles:
      - "ai-auditor-agent-role"  # Append-only permission
    read_roles:
      - "security-team-role"
      - "compliance-team-role"
      - "external-auditor-role"
    deny_delete:
      - "*"  # No one can delete, only legal hold release
```

2. **Immutability**:
   - Object versioning enabled (all modifications create new version)
   - Deletion disabled via bucket policy
   - Object Lock prevents modification for retention period

3. **Cryptographic Protection** (AU-9(3)):
   - Encryption at rest: AES-256-GCM via AWS KMS
   - Encryption in transit: TLS 1.3 minimum
   - Daily Merkle tree hash computation and publication
   - Hash published to immutable ledger for external verification

4. **Access Control**:
   - AI Auditor Agent: Append-only write permission
   - Security Team: Read-only access
   - Compliance Team: Read-only access
   - External Auditors: Read-only API access with MFA
   - Administrators: No delete permission (requires CISO + legal approval)

**Part (b)**: Alerting

SIEM alerts configured for:
- Unauthorized write attempts to audit bucket (SI-4)
- Permission changes to audit bucket policy
- Attempted deletion of audit logs
- Failed MFA attempts for audit log access
- Unusual access patterns (e.g., bulk download)

Alert recipients:
- Security Operations Center (SOC): Real-time SIEM alert
- ISSO: Email within 15 minutes
- CISO: Critical alerts (SMS)

### Evidence
- **S3 Configuration**: `terraform/audit-storage/s3-bucket.tf`
- **Bucket Policy**: `configs/aws/audit-bucket-policy.json`
- **Merkle Hash Publisher**: `scripts/merkle-tree-publisher.py` (runs daily via cron)
- **SIEM Alerts**: `frameworks/observability-config.yml` § audit_protection_alerts
- **Access Logs**: S3 server access logging enabled (logs to separate secure bucket)

---

## IA-5: Authenticator Management
**CCI**: CCI-000195 | **Status**: ✅ Implemented | **Owner**: Security Team

### Control Requirement (NIST)
*Manage system authenticators by:*
*a. Verifying identity before issuing authenticators*
*b. Establishing initial authenticator content*
*c. Ensuring authenticators have sufficient strength*
*d. Establishing and implementing procedures for handling lost/compromised authenticators*
*e. Changing authenticators at defined frequencies*
*f. Protecting authenticator content*
*g. Requiring individuals to take specific measures to safeguard authenticators*

### AAGF Implementation

**Part (a)**: Identity verification

- AI agents assigned dedicated service account identities
- Human administrator provisions initial credentials via secure workflow:
  1. Create service account in IAM
  2. Generate initial secret in Secrets Manager (IA-5(b))
  3. Grant agent role permission to read specific secret path
  4. Log provisioning event (AU-3)

**Part (b)**: Initial authenticator content

- Secrets generated using cryptographically secure random number generator
- Minimum 32 characters (IA-5(c))
- Stored in approved vault: AWS Secrets Manager / HashiCorp Vault / Azure Key Vault
- Agents receive secret path/ARN, never raw value

**Part (c)**: Authenticator strength

| Authenticator Type | Strength Requirements |
|--------------------|-----------------------|
| **API Keys** | 32+ characters, random, base64-encoded |
| **Service Account Tokens** | 256-bit entropy, cryptographically random |
| **SSH Keys** | RSA 4096-bit or Ed25519 |
| **Database Credentials** | 32+ characters, random, alphanumeric + special |

**Part (d)**: Lost/compromised authenticator procedures

```yaml
# Incident response playbook
incident_type: compromised_credential
steps:
  1. Immediate revocation:
     - Revoke compromised credential in vault
     - Block associated service account (AC-2)
     - Terminate active sessions

  2. Forensics:
     - Review audit logs for unauthorized usage (AU-6)
     - Identify scope of potential breach
     - Document timeline in incident ticket

  3. Rotation:
     - Generate new credential
     - Update agent configuration
     - Deploy via CM-3 change control

  4. Notification:
     - Alert ISSO and security team
     - Notify affected system owners
     - Document lessons learned (IR-4)
```

**Part (e)**: Credential rotation

- **Scheduled Rotation**: Every 90 days (automated)
- **On-Demand Rotation**: Via API call
- **Triggered Rotation**: On suspected compromise
- Rotation logged as audit event (AU-2)

```python
# Automated rotation (runs via cron)
def rotate_agent_credentials(agent_id: str):
    old_secret_arn = get_agent_secret_arn(agent_id)

    # Generate new secret
    new_secret = generate_secure_random(32)
    new_secret_arn = secrets_manager.create_secret(
        Name=f"aagf/agents/{agent_id}/credentials",
        SecretString=new_secret,
        Tags=[
            {"Key": "agent_id", "Value": agent_id},
            {"Key": "rotation_date", "Value": datetime.utcnow().isoformat()}
        ]
    )

    # Update agent configuration
    update_agent_config(agent_id, secret_arn=new_secret_arn)

    # Grace period: keep old secret active for 24 hours
    schedule_deletion(old_secret_arn, recovery_window_days=1)

    # Audit log
    audit_log(
        event_type="credential_rotation",
        agent_id=agent_id,
        control="IA-5",
        cci="CCI-000195"
    )
```

**Part (f)**: Protecting authenticator content

- Secrets never logged (IA-5(7))
- Secrets not stored in code, config files, or environment variables
- Secrets encrypted at rest (SC-28) and in transit (SC-8)
- Secrets Manager access logged (AU-3)

**Part (g)**: Safeguarding measures

For human administrators accessing agent credentials:
- Require MFA (IA-2(1))
- Approve access via JIRA ticket (CM-3)
- Time-bound access (auto-revoke after 4 hours)
- Log all access to credentials (AU-3)

### Evidence
- **Vault Configuration**: `terraform/secrets-manager/*.tf`
- **Rotation Script**: `scripts/rotate-credentials.py`
- **Incident Playbook**: `runbooks/compromised-credential.md`
- **Audit Logs**: `audit-logs/credential-events/*.json`
- **Policy**: `policies/security-policies.md` § IA-5

---

## IA-5(7): No Embedded Unencrypted Static Authenticators
**CCI**: CCI-004062 | **Status**: ✅ Implemented | **Owner**: Development Team

### Control Requirement (NIST)
*Ensure that unencrypted static authenticators are not embedded in applications or stored in function scripts or data files.*

### AAGF Implementation

**Pre-Processing Filter**:

Before sending any data to LLM providers (SC-4-AI-1), AAGF scans for embedded secrets:

```python
import re
from detect_secrets import SecretsCollection

# Regex patterns for common secrets
SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9]{32,}",  # OpenAI API keys
    r"-----BEGIN [A-Z ]+ KEY-----",  # Private keys
    r"AIza[0-9A-Za-z\\-_]{35}",  # Google API keys
    r"AKIA[0-9A-Z]{16}",  # AWS access keys
    r"[a-zA-Z0-9+/]{40,}",  # Base64-encoded secrets (potential)
]

def scan_for_secrets(text: str) -> List[SecretMatch]:
    """Detect embedded secrets before LLM transmission"""
    secrets_found = []

    # Pattern-based detection
    for pattern in SECRET_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            secrets_found.append({
                "type": "embedded_secret",
                "pattern": pattern,
                "location": match.span(),
                "redacted_value": match.group()[:4] + "***"
            })

    # ML-based detection (detect-secrets library)
    from detect_secrets import SecretsCollection
    from detect_secrets.settings import default_settings

    secrets = SecretsCollection()
    with default_settings():
        secrets.scan_file(text)
        for secret in secrets:
            secrets_found.append({
                "type": secret.type,
                "line": secret.line_number,
                "confidence": secret.confidence
            })

    return secrets_found

def safe_llm_call(prompt: str, context: str) -> str:
    # Scan for secrets
    secrets_in_prompt = scan_for_secrets(prompt)
    secrets_in_context = scan_for_secrets(context)

    if secrets_in_prompt or secrets_in_context:
        # Log violation
        audit_log(
            event_type="embedded_secret_detected",
            control="IA-5(7)",
            cci="CCI-004062",
            secrets_found=len(secrets_in_prompt) + len(secrets_in_context),
            action="llm_call_blocked"
        )

        # Block LLM call
        raise SecurityViolation(
            "Embedded secrets detected. Cannot send to LLM provider."
        )

    # Proceed with LLM call
    return llm_api.call(prompt=prompt, context=context)
```

**Code Repository Scanning**:

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning
on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run detect-secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --baseline .secrets.baseline
          detect-secrets audit .secrets.baseline

      - name: Run gitleaks
        run: |
          docker run -v $(pwd):/path zricethezav/gitleaks:latest \
            detect --source="/path" --verbose --no-git

      - name: Fail on secrets found
        if: steps.secret-scan.outcome == 'failure'
        run: |
          echo "::error::Secrets detected in code. See security-policies.md § IA-5(7)"
          exit 1
```

**Developer Training**:
- All developers trained on IA-5(7) requirements (AT-3)
- Monthly security reminders about credential handling
- Examples of correct vs. incorrect patterns in documentation

**Correct Pattern**:
```python
# ✅ CORRECT - Reference secret by path
from aws_secretsmanager import get_secret
api_key = get_secret("aagf/prod/api-key")
```

**Incorrect Patterns (Detected and Blocked)**:
```python
# ❌ INCORRECT - Embedded secret
api_key = "sk-abc123..."  # BLOCKED by pre-commit hook

# ❌ INCORRECT - Environment variable (logged in plaintext)
api_key = os.getenv("API_KEY")  # Use Secrets Manager instead

# ❌ INCORRECT - Config file
api_key = config['api_key']  # Secrets should not be in config files
```

### Evidence
- **Scanner Code**: `src/security/secret-scanner.py`
- **CI/CD Integration**: `.github/workflows/secret-scan.yml`
- **Pre-Commit Hook**: `.git/hooks/pre-commit` (runs secret scan)
- **Detection Logs**: `audit-logs/secret-detection/*.json`
- **Baseline**: `.secrets.baseline` (allowlist for test/example data)
- **Policy**: `policies/security-policies.md` § IA-5(7)

---

## SC-4-AI-1: Data Leakage to LLM Providers (AI Extension)
**CCI**: CCI-AI-003 | **Status**: ✅ Implemented | **Owner**: Security Engineering

### Control Requirement (Custom AI Extension)
*Prevent sensitive data (PII, secrets, confidential information, compliance-regulated data) from being transmitted to hosted LLM provider APIs.*

### AAGF Implementation

**Multi-Layer DLP (Data Loss Prevention)**:

1. **Classification-Based Blocking**:
```python
from data_classifier import classify_data

def safe_llm_call(prompt: str, context: str) -> str:
    # Classify all input data
    prompt_classification = classify_data(prompt)
    context_classification = classify_data(context)

    # Block Confidential/Restricted data to external LLMs
    if prompt_classification in ["CONFIDENTIAL", "RESTRICTED"]:
        audit_log(
            event_type="data_leakage_blocked",
            control="SC-4-AI-1",
            cci="CCI-AI-003",
            classification=prompt_classification,
            reason="Confidential data cannot go to hosted LLM"
        )
        raise SecurityViolation("Cannot send Confidential data to external LLM")

    # Redact Internal data
    if prompt_classification == "INTERNAL":
        prompt = redact_pii(prompt)
        audit_log(event_type="pii_redacted", control="SC-4-AI-1")

    # Proceed with external LLM call
    return external_llm_api.call(prompt, context)
```

2. **PII Detection and Redaction**:
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def redact_pii(text: str) -> str:
    """Redact PII before sending to LLM"""
    # Detect PII
    results = analyzer.analyze(
        text=text,
        entities=[
            "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
            "SSN", "IP_ADDRESS", "PERSON", "LOCATION",
            "DATE_OF_BIRTH", "MEDICAL_LICENSE", "US_PASSPORT"
        ],
        language='en'
    )

    # Anonymize with placeholders
    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators={
            "EMAIL_ADDRESS": {"type": "replace", "new_value": "<EMAIL>"},
            "PHONE_NUMBER": {"type": "replace", "new_value": "<PHONE>"},
            "SSN": {"type": "replace", "new_value": "<SSN>"},
            # ... etc
        }
    )

    # Log redaction
    audit_log(
        event_type="pii_redacted",
        pii_types=[r.entity_type for r in results],
        count=len(results),
        control="SC-4-AI-1"
    )

    return anonymized.text
```

3. **Secrets Detection** (per IA-5(7)):
   - See IA-5(7) implementation above
   - Secrets blocked before LLM transmission

4. **On-Premise LLM Fallback**:

```yaml
# Configuration for sensitive data
llm_routing:
  default: "openai"  # External LLM for Public/Internal data

  confidential_override: "local"  # On-premise LLM

  local_llm:
    provider: "ollama"
    model: "llama3-70b"
    endpoint: "http://localhost:11434"
    data_residency: "on-premise"
    certifications: ["SOC 2", "ISO 27001"]
```

**Data Classification Enforcement**:

| Classification | LLM Provider Allowed | Redaction Required | Audit Level |
|----------------|---------------------|-------------------|-------------|
| **Public** | External (OpenAI, Anthropic) | No | Standard (AU-2) |
| **Internal** | External (redacted) or On-Prem | Yes (PII, IP addresses) | Enhanced (AU-3) |
| **Confidential** | On-Premise ONLY | N/A (cannot use external) | Full (AU-3(1)) |
| **Restricted** | No AI processing allowed | N/A | Complete (AU-9) |

### Evidence
- **DLP Implementation**: `src/security/dlp.py`
- **Presidio Integration**: `src/security/pii-redactor.py`
- **Classification Service**: `src/data-classification/classifier.py`
- **On-Prem LLM Config**: `configs/llm/local-llm.yaml`
- **Audit Logs**: `audit-logs/dlp-events/*.json`
- **Test Suite**: `tests/security/test_dlp.py` (validates blocking/redaction)
- **Policy**: `policies/security-policies.md` § SC-4-AI-1

---

## CM-3: Configuration Change Control
**CCI**: CCI-000066 | **Status**: 🟡 Partially Implemented | **Owner**: DevOps Team

### Control Requirement (NIST)
*a. Determine and document the types of changes to the system that are configuration-controlled*
*b. Review proposed configuration-controlled changes and approve or disapprove*
*c. Document configuration change decisions*
*d. Implement approved configuration changes*
*e. Review and approve changes after implementation*
*f. Retain records of configuration-controlled changes*

### AAGF Implementation

**Part (a)**: Configuration-controlled change types

The following changes require CM-3 process:
- All production infrastructure changes (Tier 3)
- AI model version updates (CM-3-AI-1)
- Agent tier escalations (AC-6-AI-1)
- Security configuration changes (IA-5, AC-6)
- Data classification policy changes (SC-4)
- Audit log retention settings (AU-11)
- SIEM alert threshold changes (SI-4)

**Part (b)**: Review and approval

```yaml
# Change approval workflow
change_types:
  infrastructure:
    approvers: ["devops-lead", "security-admin"]
    sla_hours: 24
    required_evidence: ["test_results", "rollback_plan"]

  model_version:
    approvers: ["ml-engineer", "security-admin"]
    sla_hours: 48
    required_evidence: ["regression_test", "cost_impact_analysis"]

  security_policy:
    approvers: ["ciso", "legal"]
    sla_hours: 72
    required_evidence: ["risk_assessment", "compliance_review"]
```

JIRA-based approval process:
1. Agent creates change ticket via API
2. Ticket routed to appropriate approvers
3. Approvers review evidence attachments
4. Approval/denial recorded in JIRA + audit log (AU-3)

**Part (c)**: Documentation

Each change documented with:
- Change ID (JIRA ticket number)
- Requestor (agent ID or human)
- Description and justification
- Risk level (low/medium/high)
- Impact analysis (CM-4)
- Test results
- Rollback plan
- Approver identities and timestamps

**Part (d)**: Implementation

Changes implemented via Infrastructure-as-Code:
```bash
# Example deployment with change control
./deploy.sh \
  --change-ticket JIRA-12345 \
  --approved-by alice@example.com \
  --environment production

# Script validates:
# 1. JIRA ticket exists and is approved
# 2. Approver has authority (AC-6)
# 3. All prerequisites met
# 4. Audit log entry created (AU-3)
```

**Part (e)**: Post-implementation review

- Automated health checks run after deployment
- Human spot-check on sample of changes (10% random)
- Failures trigger rollback and incident investigation (IR-4)

**Part (f)**: Records retention

- All change records retained per AU-11 (2 years minimum)
- Stored in audit-compliant format
- Indexed in SIEM for searchability

**PARTIALLY IMPLEMENTED**: Missing automated testing for all change types (see POA&M Item #3)

### Evidence
- **JIRA Integration**: `integrations/jira/change-management.py`
- **Deployment Scripts**: `scripts/deploy-with-approval.sh`
- **Change Records**: JIRA project "AAGF-CHG" + `audit-logs/change-management/*.json`
- **Policy**: `policies/compliance-policies.md` § CM-3
- **POA&M**: Item #3 (complete automated testing coverage)

---

## SA-15-AI-1: Cost and Budget Controls (AI Extension)
**CCI**: CCI-AI-013 | **Status**: ✅ Implemented | **Owner**: Finance + Engineering

### Control Requirement (Custom AI Extension)
*Implement hard limits and monitoring for AI API consumption costs to prevent runaway expenses and budget overruns.*

### AAGF Implementation

**Budget Configuration**:

```yaml
# configs/cost-controls.yaml
cost_budgets:
  global:
    monthly_limit_usd: 10000
    daily_limit_usd: 500
    per_agent_daily_limit_usd: 50

  tier_limits:
    tier1: 10   # Dev agents: $10/day
    tier2: 50   # Staging agents: $50/day
    tier3: 200  # Production agents: $200/day
    tier4: 100  # Strategic agents: $100/day

  alert_thresholds:
    - percent: 50
      action: "notify_finance"
    - percent: 75
      action: "notify_manager"
    - percent: 90
      action: "notify_ciso"
    - percent: 100
      action: "throttle_agent"
```

**Real-Time Cost Tracking**:

```python
import openai
from decimal import Decimal

class CostTrackedLLM:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.budget = get_agent_budget(agent_id)

    def call(self, prompt: str, **kwargs) -> str:
        # Check budget before call
        current_spend = get_current_spend(self.agent_id, period="daily")
        if current_spend >= self.budget:
            audit_log(
                event_type="budget_exceeded",
                agent_id=self.agent_id,
                current_spend=current_spend,
                budget=self.budget,
                control="SA-15-AI-1",
                cci="CCI-AI-013"
            )
            raise BudgetExceededError(f"Daily budget ${self.budget} exceeded")

        # Make LLM call
        response = openai.ChatCompletion.create(
            model=kwargs.get("model", "gpt-4"),
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )

        # Calculate cost
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = calculate_cost(
            model=kwargs.get("model"),
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        # Record cost
        record_cost(
            agent_id=self.agent_id,
            cost_usd=cost,
            tokens=input_tokens + output_tokens,
            model=kwargs.get("model")
        )

        # Check thresholds
        new_spend = current_spend + cost
        check_budget_thresholds(self.agent_id, new_spend, self.budget)

        return response.choices[0].message.content
```

**Budget Enforcement Actions**:

| Threshold | Action | Notification |
|-----------|--------|--------------|
| 50% | Log warning | Finance team (email) |
| 75% | Escalate alert | Manager + Finance (email) |
| 90% | Critical alert | CISO + Manager (SMS) |
| 100% | **Hard stop** | All LLM calls blocked until budget reset or approval |

**Emergency Override**:

```python
def request_budget_override(agent_id: str, additional_budget_usd: Decimal, justification: str):
    """Request emergency budget increase"""
    ticket = create_jira_ticket(
        project="AAGF-FINANCE",
        summary=f"Emergency budget override: {agent_id}",
        description=f"""
        Agent: {agent_id}
        Current Budget: ${get_agent_budget(agent_id)}
        Requested Increase: ${additional_budget_usd}
        Justification: {justification}

        Requires approval from Finance + Manager
        """,
        priority="high"
    )

    # Block until approved
    wait_for_approval(ticket_id=ticket.id, timeout_hours=4)

    # Apply override
    increase_budget(agent_id, additional_budget_usd)

    audit_log(
        event_type="budget_override",
        agent_id=agent_id,
        amount_usd=additional_budget_usd,
        ticket=ticket.id,
        control="SA-15-AI-1"
    )
```

**Cost Reporting**:

- **Daily**: Automated cost report to Finance team
- **Weekly**: Cost breakdown by agent, tier, model
- **Monthly**: Executive summary with trends and recommendations
- **Real-Time**: Grafana dashboard showing current spend vs. budget

### Evidence
- **Cost Tracker**: `src/cost-control/tracker.py`
- **Budget Config**: `configs/cost-controls.yaml`
- **Grafana Dashboard**: http://grafana.internal/d/cost-monitoring
- **Cost Records**: `audit-logs/cost-events/*.json` (schema: `policies/schemas/agent-cost-record.json`)
- **Reports**: `reports/cost-analysis/` (generated monthly)
- **Policy**: `policies/compliance-policies.md` § SA-15-AI-1

---

## Control Implementation Summary

| Control | Status | CCI | Implementation Evidence | Owner |
|---------|--------|-----|------------------------|-------|
| AC-6 | ✅ Implemented | CCI-002220 | `agents/tier*/permissions.yaml` | Security Team |
| AC-6(1) | ✅ Implemented | CCI-002233 | `src/access-control/security-functions.py` | Security Team |
| AC-6-AI-1 | ✅ Implemented | CCI-AI-005 | `src/tier-enforcement/validator.py` | Platform Engineering |
| AC-6-AI-2 | ✅ Implemented | CCI-AI-006 | `src/approvals/human-in-loop.py` | DevOps Team |
| AU-2 | ✅ Implemented | CCI-000130 | `frameworks/observability-config.yml` | Security Operations |
| AU-3 | ✅ Implemented | CCI-000131 | `policies/schemas/audit-trail.json` | Security Operations |
| AU-3-AI-1 | ✅ Implemented | CCI-AI-008 | `src/audit/ai-logger.py` | ML Engineering |
| AU-9 | ✅ Implemented | CCI-000162 | `terraform/audit-storage/s3-bucket.tf` | Security Operations |
| IA-5 | ✅ Implemented | CCI-000195 | `terraform/secrets-manager/*.tf` | Security Team |
| IA-5(7) | ✅ Implemented | CCI-004062 | `src/security/secret-scanner.py` | Development Team |
| SC-4-AI-1 | ✅ Implemented | CCI-AI-003 | `src/security/dlp.py` | Security Engineering |
| CM-3 | 🟡 Partial | CCI-000066 | `integrations/jira/change-management.py` | DevOps Team |
| SA-15-AI-1 | ✅ Implemented | CCI-AI-013 | `src/cost-control/tracker.py` | Finance + Engineering |

**See**: `control-summary.md` for complete at-a-glance status of all 339 controls

---

## Additional Controls

**For complete implementation statements of all 339 controls**, refer to:
- `control-summary.md` - At-a-glance status table
- `../policies/control-mappings.md` - NIST control to policy mapping
- `../policies/security-policies.md` - AC, IA, SC family implementations
- `../policies/compliance-policies.md` - AU, CM, PL family implementations
- `../policies/logging-policy.md` - Complete AU family implementation guide

---

## Continuous Improvement

**Control effectiveness measured through**:
- Quarterly control testing (CA-2)
- Continuous monitoring (CA-7, CA-7-AI-1)
- Annual security assessment (CA-2)
- Incident lessons learned (IR-4)
- Risk assessment updates (RA-3)

**See**: `poam.md` for current gaps and remediation timelines

---

**Document Owner**: ISSO
**Review Frequency**: Quarterly or on significant system change
**Next Review**: 2026-01-18
