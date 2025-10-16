# SEC-001: AWS Secrets Manager Credential Checkout/Check-in

Path: `examples/control-validation/SEC-001-aws-secrets-manager.md`

## Control Description

SEC-001 mandates that every AWS Secrets Manager credential checkout and check-in be logged both as:

1. An **audit-trail entry** conforming to `policies/schemas/audit-trail.json`  
2. A **SIEM event** conforming to `policies/schemas/siem-event.json`

Both records share the same `siem_event_id` so you can correlate audit store entries with SIEM data.

---

## Worked Example

### 1. Credential Checkout

#### Audit-Trail Entry (`audit-trail.json`)
```json
{
  "audit_id": "3c9f2a1e-7d45-4f8b-9c2a-8a1b2c3d4e5f",
  "timestamp": "2025-10-15T11:55:00Z",
  "actor": "ai-ops-agent-01",
  "action": "credential_checkout",
  "workflow_step": "SEC-001",
  "jira_reference": {
    "cr_id": "CR-2025-1042",
    "approver_role": "Change Manager",
    "budget_tokens": 500,
    "controls": ["SEC-001"]
  },
  "inputs": {
    "secret_name": "prod/db/password",
    "purpose": "database_connection"
  },
  "outputs": {
    "lease_id": "lease-xyz-123",
    "expiry": "2025-10-15T12:05:00Z"
  },
  "policy_controls_checked": ["SEC-001"],
  "compliance_result": "pass",
  "evidence_hash": "sha256:abcd1234...",
  "auditor_agent": "AUD-001"
}
