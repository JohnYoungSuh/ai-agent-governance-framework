# Logging and Audit Policy

> Implements NIST 800-53 Rev 5 AU (Audit and Accountability) family controls

**Primary Controls**: AU-2, AU-3, AU-8, AU-9, AU-11 | **CCI**: CCI-000130 through CCI-001849
**AI Extensions**: AU-3-AI-1 (AI Decision Auditability) | **CCI**: CCI-AI-008

---

## Purpose

This policy implements NIST 800-53 Audit and Accountability (AU) controls for AI agent operations, defining requirements for generating, protecting, storing, and integrating logs and audit records.

Compliance frameworks (FedRAMP, SOC 2, PCI-DSS, HIPAA), security monitoring, and both internal and external audits rely on these logs to demonstrate control effectiveness and system integrity.

---

## Scope

**Applies To**: All components of the AI/Dev/Sec/Ops framework

**In Scope**:
- AI OPS Agents (Tier 1-4) generating audit-trail entries
- AI Auditor Agent ingesting and verifying logs
- JIRA change-management events (CM-3)
- AWS Secrets Manager credential operations (IA-5)
- SIEM ingestion pipelines (AU-6, SI-4)
- External audit interfaces (compliance reporting)

**Control References**:
- See `policies/compliance-policies.md` for full AU control implementations
- See `policies/control-mappings.md` for NIST-to-CCI mappings

---

## AU-2: Auditable Events

**NIST Control**: AU-2 | **CCI**: CCI-000130
**Control Statement**: Identify and log organizationally-defined auditable events

### Log Sources (by Control Family)

| Log Source | Control Family | Events Logged | Schema |
|------------|----------------|---------------|--------|
| **AI Agent Actions** | AU-3-AI-1, AC-6 | All CRUD operations, approvals, tier enforcement | `audit-trail.json` |
| **JIRA Tickets** | CM-3, CM-4 | Change requests, approvals, status changes | `siem-event.json` |
| **Secrets Manager** | IA-5, IA-5(7) | Credential checkout/checkin, rotation | `siem-event.json` |
| **Access Control** | AC-2, AC-6 | Permission grants/revocations, escalations | `audit-trail.json` |
| **Cost Tracking** | SA-15-AI-1 | Token usage, budget exceedances | `agent-cost-record.json` |
| **Security Events** | SI-4, RA-9-AI-2 | Prompt injection, hallucination alerts | `siem-event.json` |

---

## AU-3: Content of Audit Records

**NIST Control**: AU-3, AU-3(1) | **CCI**: CCI-000131, CCI-000133
**AI Extension**: AU-3-AI-1 | **CCI**: CCI-AI-008

### Required Schema Compliance

All log entries MUST conform to approved JSON schemas:
- `policies/schemas/audit-trail.json` - AI agent decision logs
- `policies/schemas/siem-event.json` - Generic security events
- `policies/schemas/agent-cost-record.json` - Cost tracking

### Mandatory Fields (per AU-3)

Each record MUST include (per CCI-000131):
```json
{
  "siem_event_id": "UUID v4 - unique identifier",
  "timestamp": "ISO-8601 UTC with milliseconds (AU-8)",
  "event_type": "Categorization: agent_action | auth_event | config_change",
  "source": "Originating system/component",
  "agent_id": "If agent-generated (AC-6-AI-1)",
  "outcome": "success | failure | partial",
  "classification": "Data classification level (SC-4)"
}
```

### AI-Specific Additional Information (AU-3-AI-1)

For AI agent decisions, MUST also include (per CCI-AI-008):
```json
{
  "model_version": "Exact LLM model version (CM-3-AI-1)",
  "prompt_template": "Template used (for reproducibility)",
  "reasoning_chain": "Chain-of-thought or decision steps",
  "confidence_score": "Model confidence [0.0-1.0]",
  "citations": "Sources referenced in decision",
  "validation_result": "Hallucination check status (SI-7-AI-1)"
}
```

**Rationale**: Enables reproducing AI decisions for audits, compliance, and incident investigation

---

## AU-8: Time Stamps

**NIST Control**: AU-8 | **CCI**: CCI-000159

**Requirements**:
- **Format**: ISO-8601 extended format with milliseconds
- **Time Zone**: UTC (Coordinated Universal Time)
- **Clock Sync**: NTP synchronization required (within 1 second)
- **Example**: `2025-10-18T14:32:01.123Z`

**Implementation**:
```python
from datetime import datetime, timezone

# ✅ CORRECT
timestamp = datetime.now(timezone.utc).isoformat()

# ❌ INCORRECT - no timezone
timestamp = datetime.now().isoformat()
```

---

## AU-9: Protection of Audit Information

**NIST Controls**: AU-9, AU-9(2), AU-9(3) | **CCI**: CCI-000162, CCI-001350, CCI-001351

**Control Statement**: Protect audit logs from unauthorized access, modification, and deletion

### AU-9(2): Store on Separate Physical Systems

**Implementation** (CCI-001350):
- **Primary Storage**: Dedicated append-only audit bucket (S3 with Object Lock)
- **Separate from**: Application databases, operational storage
- **Network Isolation**: Dedicated audit VPC/subnet
- **Access Path**: API-only (no direct bucket access)

### AU-9(3): Cryptographic Protection

**Implementation** (CCI-001351):
- **Encryption at Rest**: AES-256-GCM (SC-28(1))
- **Encryption in Transit**: TLS 1.3 minimum
- **Integrity Protection**: Daily Merkle tree hash publication
- **Key Management**: AWS KMS or equivalent (IA-5(2))

```yaml
# S3 Bucket Configuration
audit-logs-bucket:
  versioning: enabled
  object_lock:
    mode: GOVERNANCE  # Prevents deletion without special permission
    retention: 2 years
  encryption:
    type: "aws:kms"
    key_id: "arn:aws:kms:region:account:key/audit-key"
  access_control:
    append_only_role: "ai-auditor-agent-role"
    read_only_roles: ["security-team", "compliance-team", "external-auditor"]
```

### Access Control Matrix

| Role | Read | Append | Modify | Delete | Requires |
|------|------|--------|--------|--------|----------|
| AI Auditor Agent | No | Yes | No | No | Service account (IA-5) |
| Security Team | Yes | No | No | No | MFA (IA-2(1)) |
| Compliance Team | Yes | No | No | No | MFA (IA-2(1)) |
| External Auditor | Yes (API) | No | No | No | API key + audit ticket |
| Administrator | No | No | No | Restricted* | Multi-person + CISO approval |

*Deletion only for legal holds, requires documented approval

---

## AU-11: Audit Record Retention

**NIST Control**: AU-11 | **CCI**: CCI-001849

**Control Statement**: Retain audit records for organizationally-defined time period

### Retention Schedule

| Retention Tier | Duration | Storage Type | Compliance Driver |
|----------------|----------|--------------|-------------------|
| **Hot Storage** | 2 years | S3 Standard | Baseline requirement |
| **Warm Archive** | Years 2-5 | S3 Glacier | Industry best practice |
| **Cold Archive** | Years 5-7 | S3 Deep Archive | SOX, regulatory |
| **Legal Hold** | Indefinite | Immutable | Litigation/investigation |

### Compliance-Specific Extensions

**Override minimum retention for**:
- **SOX (Sarbanes-Oxley)**: 7 years for financial system audits
- **HIPAA**: 6 years for healthcare PHI access logs (SC-4-AI-1)
- **PCI-DSS**: 1 year hot + 3 years archive for payment data (SC-4-AI-1)
- **EU GDPR**: Per data retention policy + 3 years for compliance evidence

**Implementation**:
```yaml
# Lifecycle policy example
retention_policy:
  default:
    hot: 730 days  # 2 years
    warm: 1825 days  # 5 years total
    cold: 2555 days  # 7 years total

  overrides:
    - tag: "sox_financial"
      retention_days: 2555  # 7 years

    - tag: "hipaa_phi"
      retention_days: 2190  # 6 years

    - tag: "legal_hold"
      retention: "indefinite"
      immutable: true
```

---

## SIEM Integration (AU-6, SI-4)

**Supporting Controls**: AU-6 (Audit Review), SI-4 (System Monitoring)

### SIEM Connector Configuration

**Ingest Sources**:
1. Append-only audit trail store (direct S3 integration)
2. JIRA webhook endpoint (change management events)
3. AWS Secrets Manager CloudTrail logs (credential operations)
4. Agent cost tracking API (budget monitoring)

**Field Mapping**: All sources normalized to `siem-event.json` schema

### Alert Rules (SI-4)

Define SIEM correlation rules for (documented in `frameworks/observability-config.yml`):

| Alert | Trigger Condition | Severity | Response |
|-------|------------------|----------|----------|
| **Missing Audit Event** | Sequence gap detected | High | Investigate agent/system |
| **Budget Overrun** | Cost >90% of limit (SA-15-AI-1) | Critical | Throttle agent API calls |
| **Unapproved Change** | Tier 3 action without JIRA ticket (CM-3) | Critical | Rollback + incident |
| **Log Tampering Attempt** | Write to audit log from non-authorized role (AU-9) | Critical | Security incident |
| **Privilege Escalation** | Tier boundary violation (AC-6-AI-1) | High | Suspend agent + review |
| **Data Classification Violation** | Confidential data to external LLM (SC-4-AI-1) | Critical | Block + incident |

---

## Audit Monitoring (AI Auditor Agent)

**Control**: AU-6 (Audit Review, Analysis, and Reporting) | **CCI**: CCI-000154

### AI Auditor Agent Responsibilities

1. **Real-Time Validation**:
   - Verify all Tier 3+ actions have corresponding JIRA tickets (CM-3)
   - Check budget compliance (SA-15-AI-1)
   - Validate timestamp sequences (AU-8)

2. **Compliance Reporting**:
   - Generate weekly control effectiveness reports
   - Flag policy violations for human review (AC-6-AI-2)
   - Support external audit requests (read-only API)

3. **Integrity Verification**:
   - Compute daily Merkle tree hash of audit logs
   - Publish hash to immutable ledger (blockchain or timestamping service)
   - Detect and alert on any log inconsistencies

### Example Auditor Logic

```python
def validate_tier3_action(audit_record):
    """AU-6 + CM-3 compliance check"""
    if audit_record.agent_tier >= 3:
        if not audit_record.approval_ticket:
            raise ComplianceViolation(
                control="CM-3",
                cci="CCI-000066",
                message="Tier 3 action missing JIRA approval"
            )

        # Verify ticket exists and is approved
        jira_ticket = fetch_jira(audit_record.approval_ticket)
        if jira_ticket.status != "approved":
            raise ComplianceViolation(
                control="CM-3",
                message=f"Ticket {jira_ticket.id} not approved"
            )
```

---

## Implementation Checklist

### Initial Setup
- [ ] Deploy append-only S3 bucket with Object Lock (AU-9)
- [ ] Configure KMS encryption keys (AU-9(3))
- [ ] Create AI Auditor Agent service account with append-only permissions
- [ ] Set up SIEM connectors for all log sources (AU-6)
- [ ] Define alert rules in SIEM (SI-4)
- [ ] Configure retention lifecycle policies (AU-11)
- [ ] Establish Merkle tree hash publishing (AU-9(3))

### Ongoing Operations
- [ ] Review SIEM alerts daily (AU-6)
- [ ] Run AI Auditor Agent validation hourly
- [ ] Generate weekly compliance reports
- [ ] Quarterly access review for audit log readers (AC-2(3))
- [ ] Annual cryptographic key rotation (IA-5)
- [ ] Test log integrity verification monthly
- [ ] External audit support on-demand

---

## References

### Internal Documentation
- `policies/compliance-policies.md` - Full AU control implementations
- `policies/control-mappings.md` - NIST 800-53 to CCI mappings
- `policies/schemas/audit-trail.json` - AI decision log schema
- `policies/schemas/siem-event.json` - Generic event schema
- `frameworks/observability-config.yml` - SIEM alert definitions

### Standards
- **NIST SP 800-53 Rev 5**: AU family controls
- **NIST SP 800-92**: Guide to Computer Security Log Management
- **DISA CCI**: Control Correlation Identifiers
- **FedRAMP**: Audit and Accountability requirements
- **PCI-DSS 4.0**: Requirement 10 (Logging and Monitoring)

---

**Version**: 2.0 (NIST-aligned)
**Last Updated**: 2025-10-18
**Control Owner**: Security & Compliance Team
**Review Frequency**: Quarterly  
