---
trigger: always_on
---

# Governance Policy & Architecture Rules

## Core Architecture Invariants (Do Not Reverse)

### 1. GPIS is the Single PDP
The Governance Policy Inquiry Service (`app/main.py`) is the **only** Policy Decision Point. No agent may self-authorize. Every Tier 2+ operation must obtain a signed JWT from GPIS before execution.

### 2. JWT Token Contract
- Tier 1: 15-min TTL, category + namespace claims
- Tier 2: 10-min TTL, category + namespace + `requires_confirmation` claims
- Tier 3: 5-min TTL, all claims + `jira_cr_id` required
- Tier 4: 2-min TTL, all claims + `jira_cr_id` + `human_approver` required
- **NEVER** embed secrets or PII in JWT payloads

### 3. Audit Trail is Append-Only
The audit trail (`policies/schemas/audit-trail.json`) is an immutable append-only log. Never modify, delete, or retroactively update entries. Every governance decision emits one entry.

### 4. Token-Efficient Routing Hierarchy
Requests MUST flow through this stack in order — never skip levels:
```
Cache Classifier (Gemini Flash, ~100 tokens)
    ↓ MISS
Intent Router (Gemini Flash, ~200 tokens)
    ↓ complex/high-risk
Simple Rules (0 tokens — YAML lookup)
    ↓ no match
Large Model Escalation (Claude Sonnet, ~600 tokens)
    ↓ high confidence
Distillation Queue (promote to simple rules)
```

### 5. Agent Tier Authority Matrix
| Tier | Dev Env | Staging | Production | Requires |
|------|---------|---------|------------|---------|
| 1 | READ-ONLY | READ-ONLY | READ-ONLY | GPIS JWT |
| 2 | CREATE/MODIFY | READ-ONLY | DENY | GPIS JWT + confirmation |
| 3 | FULL | CREATE/MODIFY | Approved ops only | GPIS JWT + Jira CR |
| 4 | FULL | FULL | Design + approved | GPIS JWT + Jira CR + human |

### 6. Namespace Isolation (Guardrail #1)
An agent operating outside its declared namespace is an immediate DENY with audit event. No exceptions. The namespace is validated on every GPIS call via the agent manifest in CMDB.

## Policy Evolution Rules

### When Adding a New Policy Rule:
1. Write the business rule in plain English first (`policies/agent-safety-policies.md`)
2. Map it to ≥1 NIST 800-53 control in `policies/control-mappings.md`
3. Add the rule to `policies/simple_rules.yml` with the standardized format
4. Write integration tests for both ALLOW and DENY paths
5. Emit a SIEM event type for each outcome
6. Update `CHANGELOG.md` with the policy version

### When Modifying an Existing Policy Rule:
1. NEVER modify in place — create a new version (v1.py → v2.py pattern from CHANGELOG)
2. A/B test new vs old with 20+ sample requests
3. Monitor accuracy for 24h before promoting to 100% traffic
4. Update `config/token_router.yml` prompt version expectations

## Compliance Integration Rules

### NIST 800-53 Control Traceability
Every new code feature must reference ≥1 control:
- `AC-*` — Access controls → agent tier enforcement
- `AU-*` — Audit and accountability → audit trail emission
- `IA-*` — Identity and authentication → JWT, mTLS
- `SC-*` — System and communications protection → encryption, network policy
- `SI-*` — System and information integrity → input validation, CVE scanning

### Jira CR Enforcement (Tier 3/4)
```python
# Required check in GPIS before Tier 3/4 JWT issuance:
if agent_tier in ["tier3", "tier4"]:
    jira_cr_id = payload.get("jira_cr_id")
    if not jira_cr_id:
        return DENY("Jira CR required for Tier 3/4 operations")
    if not validate_jira_approval(jira_cr_id):
        return DENY("Jira CR not approved or expired")
```

## Patent Integrity Rules
- The **Atomic Governance Transaction (AGT)** schema in `policies/schemas/audit-trail.json` is the core patent claim
- Do NOT change field names, required fields, or nesting structure without a patent counsel review
- Every new governance capability must either: (a) fit within existing patent claims, or (b) be documented as a new provisional filing candidate in `docs/PATENT-DISCLOSURE.md`
- The `audit_id` (UUID), `timestamp` (ISO 8601), `actor`, `action`, `compliance_result` fields are immutable patent anchors
