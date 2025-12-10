# [DEPRECATED] GPIS Requirements Specification
> [!WARNING]
> **This document has been superseded by [PATENT-DISCLOSURE.md](../docs/PATENT-DISCLOSURE.md).**
> Please refer to the Patent Disclosure for the authoritative technical specification of the Governance Kernel.

# Governance Policy Inquiry Service (GPIS) - Technical Requirements Specification

**Document Version:** 1.0.0  
**Framework Version:** 3.0.0  
**Status:** DRAFT - For Review  
**Last Updated:** 2025-11-22  
**Author:** AI Policy Architect  
**Alignment:** Unified AI Agent Governance Framework v3.0

---

## Executive Summary

The **Governance Policy Inquiry Service (GPIS)** is the authoritative, real-time Policy Engine that serves as the central decision point for all autonomous AI agent actions. It implements Zero Trust Architecture for AI Agents (ZT-A), ensuring that every action request is authenticated, authorized, and audited before execution.

**Core Mission:** Enable **≥80% autonomous operation** while maintaining **100% accountability** through real-time policy enforcement and immutable audit trails.

**Analogy:** The GPIS is the air traffic control tower for your AI agent ecosystem. Before any agent "takes off" (executes an action), it must query the GPIS for clearance. The tower verifies identity, checks the flight plan against policies, ensures sufficient fuel (budget), and records every communication—guaranteeing that autonomy never compromises accountability.

---

## Table of Contents

1. [Non-Negotiable Architectural Mandates](#1-non-negotiable-architectural-mandates)
2. [Input and Identity Requirements](#2-input-and-identity-requirements)
3. [Core Decision Logic and Policy Enforcement](#3-core-decision-logic-and-policy-enforcement)
4. [Output and Auditability Requirements](#4-output-and-auditability-requirements)
5. [Required Metrics and Monitoring](#5-required-metrics-and-monitoring)
6. [Gap Analysis: Current vs. Required State](#6-gap-analysis-current-vs-required-state)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Integration with Existing Framework](#8-integration-with-existing-framework)

---

## 1. Non-Negotiable Architectural Mandates

### 1.1 Zero Trust (ZT) Enforcement Core

**Requirement:** The GPIS MUST function as the Policy Engine implementing ZT-A (Zero Trust for AI Agents).

**Mandatory Capabilities:**
- **Continuous Verification:** Every query evaluated independently, no session-based trust
- **Identity Attestation:** Cryptographic verification of agent identity on every request
- **Granular Authorization:** Per-action, per-resource authorization checks
- **Network Location Irrelevant:** Trust based on identity and policy, not network position
- **Credential Expiration:** Short-lived credentials (max 1 hour) with automatic rotation

**Performance Requirement:**
- **Latency Target:** <100ms for Tier 0/1 decisions, <2s for Tier 2 decisions
- **Throughput:** Support ≥1,000 requests/second per GPIS instance
- **Availability:** 99.9% uptime (max 43 minutes downtime/month)

**Rationale:** Performance is critical to achieving the ≥80% auto-approval target. High latency undermines autonomy by creating operational friction.

### 1.2 Total Accountability via Immutability

**Requirement:** Every decision MUST be recorded instantaneously as an immutable event in the Decision Ledger.

**Mandatory Fields:**
```json
{
  "decision_id": "unique_uuid",
  "timestamp": "ISO8601_with_nanoseconds",
  "agent_identity": "namespace-agent-instance-id",
  "namespace": "project_namespace",
  "action": "specific_operation",
  "action_tier": "0|1|2|3",
  "decision": "AUTO-APPROVE|HUMAN-REQUIRED|DENY",
  "policy_id": "policy_identifier",
  "policy_version": "semantic_version",
  "policy_hash": "sha256_hash",
  "justification": "policy_rule_citation",
  "cost_center": "business_cost_center",
  "project_code": "project_tracking_code",
  "estimated_cost": "float_usd",
  "trace_id": "distributed_trace_id",
  "signature": "cryptographic_signature"
}
```

**Storage Requirements:**
- **Immutability:** Write-once-read-many (WORM) storage
- **Integrity:** Cryptographic hash chain or digital signatures
- **Retention:** ≥7 years for financial events, ≥3 years for security events
- **Replication:** Geographic redundancy for disaster recovery
- **Access Control:** Restricted to governance operators only

**Implementation Options:**
- AWS S3 with Object Lock + CloudTrail
- Azure Blob Storage with immutability policy
- Blockchain-based audit log (Hyperledger Fabric)
- Splunk with write-once indexes

### 1.3 Policy-as-Code (PaC)

**Requirement:** All governance rules MUST be defined as executable code.

**Mandatory Capabilities:**
- **Version Control:** All policies in Git with semantic versioning
- **Testability:** Unit tests for policy rules
- **Dynamic Enforcement:** Real-time policy updates without service restart
- **Declarative Syntax:** YAML, Rego (OPA), or JSON-based policy definitions
- **Hash Verification:** Agents verify policy hash before execution

**Policy Structure:**
```yaml
policy_id: "unified-governance-v3"
version: "3.0.0"
hash: "sha256:abc123..."
effective_date: "2025-11-21T00:00:00Z"

action_tiers:
  tier_0:
    approval_mode: "auto-approve"
    examples:
      - "read_own_data"
      - "list_resources_in_namespace"
      - "status_check"
  
  tier_1:
    approval_mode: "auto-approve-with-audit"
    examples:
      - "write_to_own_workspace"
      - "scale_within_quota"
      - "normal_deployment"
  
  tier_2:
    approval_mode: "human-required"
    sla_hours: 4
    escalation_on_timeout: "auto-deny"
    examples:
      - "budget_overage"
      - "privilege_escalation"
      - "cross_namespace_access"
  
  tier_3:
    approval_mode: "always-deny"
    examples:
      - "credential_sharing"
      - "audit_log_deletion"
      - "policy_bypass"

resource_quotas:
  compute:
    cpu_cores_max: 16
    memory_gb_max: 64
  budget:
    monthly_limit_usd: 5000
    alert_threshold_percent: 80
```

### 1.4 High Performance / Low Latency

**Requirement:** Policy checks MUST NOT create operational bottlenecks.

**Performance Targets:**

| Decision Tier | Latency Target | Throughput Target | Availability |
|---------------|----------------|-------------------|--------------|
| Tier 0 (Auto) | <50ms (p95) | ≥2,000 req/s | 99.95% |
| Tier 1 (Auto+Audit) | <100ms (p95) | ≥1,000 req/s | 99.9% |
| Tier 2 (Human) | <2s (p95) | ≥100 req/s | 99.5% |
| Tier 3 (Deny) | <50ms (p95) | ≥2,000 req/s | 99.95% |

**Optimization Strategies:**
- **Caching:** Policy rules cached in-memory with TTL
- **Pre-computation:** Common decision paths pre-computed
- **Async Logging:** Decision Ledger writes asynchronous
- **Load Balancing:** Multiple GPIS instances with sticky sessions
- **Circuit Breakers:** Fail-safe mode if Decision Ledger unavailable

---

## 2. Input and Identity Requirements (The Query Structure)

### 2.1 Mandatory Communication Protocol

**Requirement:** All incoming queries MUST adhere to Cross-Agent Communication standards.

**Protocol Requirements:**
- **Transport:** HTTPS with mutual TLS (mTLS) or gRPC over TLS
- **Authentication:** JWT with signed claims or platform attestation (SPIFFE/SPIRE)
- **Message Signing:** Cryptographic signature on every message
- **Timestamp Validation:** Reject messages >5 minutes old (replay protection)
- **Schema Validation:** JSON Schema or Protobuf validation before processing

**Rejection Criteria:**
- Unsigned or invalid signature
- Expired timestamp (>5 minutes)
- Replayed message_id (duplicate detection)
- Malformed schema
- Invalid or revoked agent identity

### 2.2 Required Query Payload

**Requirement:** The query MUST include all fields necessary for policy evaluation.

**Mandatory Fields:**
```json
{
  "message_id": "unique_uuid",
  "timestamp": "ISO8601",
  "source_namespace": "team-alpha",
  "source_agent_identity": "team-alpha-deploy-001",
  "destination_namespace": "team-alpha",
  "destination_resource": "deployment/web-app",
  "action": "scale_deployment",
  "action_parameters": {
    "current_replicas": 3,
    "target_replicas": 5,
    "resource_type": "deployment"
  },
  "justification": "Traffic increased 300% in last hour, need additional capacity",
  "cost_center": "CC-12345",
  "project_code": "PROJ-ALPHA-2025",
  "estimated_cost": 15.50,
  "dry_run": false,
  "signature": "base64_encoded_signature",
  "trace_id": "distributed_trace_id"
}
```

**Optional but Recommended:**
- `rollback_plan`: Recovery procedure if action fails
- `dependencies`: Resources this action depends on
- `blast_radius`: Estimated impact scope
- `idempotent`: Boolean indicating if action can be safely retried

### 2.3 Identity Validation

**Requirement:** The GPIS MUST immediately validate agent identity and namespace.

**Validation Steps:**
1. **Signature Verification:** Validate cryptographic signature using agent's public key
2. **Namespace Validation:** Verify `source_namespace` matches agent's assigned namespace
3. **Identity Attestation:** Confirm identity via JWT claims, mTLS certificate, or SPIFFE attestation
4. **Revocation Check:** Ensure identity not revoked (check CRL or OCSP)
5. **Quota Verification:** Confirm agent within resource and budget quotas

**Identity Structure:**
```yaml
agent_identity: "team-alpha-deploy-001"
namespace: "team-alpha"
tier: 3
permissions:
  - "deployment.create"
  - "deployment.update"
  - "deployment.scale"
quotas:
  cpu_cores: 16
  memory_gb: 64
  budget_monthly_usd: 5000
credentials:
  type: "jwt"
  issuer: "https://identity.example.com"
  expiration: "2025-11-22T20:00:00Z"
```

**Rejection Scenarios:**
- Identity signature invalid
- Namespace mismatch (agent claims namespace it doesn't own)
- Identity revoked or expired
- Agent over quota (CPU, memory, budget)

---

## 3. Core Decision Logic and Policy Enforcement

### 3.1 Scope and Boundary Control

**Requirement:** Verify that the requested action is within the agent's explicitly defined namespace.

**Validation Logic:**
```python
def validate_scope(query):
    """Validate action is within agent's namespace scope"""
    
    # Extract namespaces
    source_ns = query["source_namespace"]
    dest_ns = query["destination_namespace"]
    agent_ns = get_agent_namespace(query["source_agent_identity"])
    
    # Strict namespace isolation
    if source_ns != agent_ns:
        return {
            "decision": "DENY",
            "tier": 3,
            "justification": f"Agent namespace mismatch: claimed={source_ns}, actual={agent_ns}"
        }
    
    # Cross-namespace operations require Tier 2 approval
    if dest_ns != source_ns:
        return {
            "decision": "HUMAN-REQUIRED",
            "tier": 2,
            "justification": f"Cross-namespace operation requires approval: {source_ns} -> {dest_ns}",
            "escalation_route": "namespace_owner"
        }
    
    # Resource ownership verification
    resource = query["destination_resource"]
    if not verify_resource_ownership(resource, source_ns):
        return {
            "decision": "HUMAN-REQUIRED",
            "tier": 2,
            "justification": f"Resource ownership unclear for {resource}, requires clarification"
        }
    
    return {"decision": "PROCEED", "scope_valid": True}
```

**Clarification Protocol:**
- If resource ownership uncertain, MUST escalate for human clarification
- Never assume ownership of untagged resources
- Require explicit confirmation before cross-namespace operations

### 3.2 Action Tiering and Human Escalation

**Requirement:** Determine the Action Tier (0, 1, 2, or 3) for every request.

**Tier Classification Logic:**

```python
def classify_action_tier(query):
    """Classify action into Tier 0-3 based on risk and impact"""
    
    action = query["action"]
    params = query["action_parameters"]
    agent = get_agent_manifest(query["source_agent_identity"])
    
    # Tier 3: Always Deny (prohibited actions)
    prohibited_actions = [
        "credential_sharing",
        "audit_log_deletion",
        "policy_bypass",
        "rm_rf_root",
        "cross_namespace_modify"
    ]
    
    if action in prohibited_actions:
        return {
            "tier": 3,
            "decision": "DENY",
            "justification": f"Action '{action}' is prohibited by policy"
        }
    
    # Tier 2: Human Required (high-risk operations)
    if is_budget_overage(query, agent):
        return {
            "tier": 2,
            "decision": "HUMAN-REQUIRED",
            "justification": "Budget overage requires FinOps approval",
            "escalation_route": "finops_team"
        }
    
    if is_privilege_escalation(action, agent):
        return {
            "tier": 2,
            "decision": "HUMAN-REQUIRED",
            "justification": "Privilege escalation requires security approval",
            "escalation_route": "security_team"
        }
    
    if is_destructive_action(action) and not query.get("dry_run"):
        return {
            "tier": 2,
            "decision": "HUMAN-REQUIRED",
            "justification": "Destructive action requires confirmation",
            "escalation_route": "namespace_owner"
        }
    
    # Tier 1: Auto-approve with audit (routine operations)
    if action in agent["allowed_actions"] and within_quota(query, agent):
        return {
            "tier": 1,
            "decision": "AUTO-APPROVE",
            "justification": "Action within agent privileges and quotas"
        }
    
    # Tier 0: Auto-approve (read-only, low-risk)
    if is_read_only(action):
        return {
            "tier": 0,
            "decision": "AUTO-APPROVE",
            "justification": "Read-only operation"
        }
    
    # Default: Escalate if uncertain
    return {
        "tier": 2,
        "decision": "HUMAN-REQUIRED",
        "justification": "Action classification uncertain, requires review"
    }
```

**Escalation Routing:**

| Trigger | Destination | SLA | Timeout Action |
|---------|-------------|-----|----------------|
| Budget overage | FinOps team + budget owner | 4 hours | Auto-deny |
| Security escalation | SOC + security team | 2 hours | Auto-deny |
| Compliance issue | Compliance + legal (if regulatory) | 8 hours | Auto-deny |
| Cross-namespace | Namespace owner + governance | 4 hours | Auto-deny |
| Operational issue | On-call engineer + namespace owner | 1 hour | Auto-deny |

### 3.3 Operational Safety and Idempotency

**Requirement:** Enforce safety checks for destructive or high-impact actions.

**Safety Checklist:**
```python
def enforce_safety_checks(query):
    """Enforce safety requirements for high-risk actions"""
    
    action = query["action"]
    
    # Destructive actions MUST run in dry-run first
    if is_destructive(action):
        if not has_dry_run_evidence(query):
            return {
                "decision": "DENY",
                "tier": 3,
                "justification": "Destructive action requires dry-run simulation first"
            }
        
        if not query.get("rollback_plan"):
            return {
                "decision": "HUMAN-REQUIRED",
                "tier": 2,
                "justification": "Destructive action requires rollback plan"
            }
    
    # High-impact actions MUST be idempotent
    if is_high_impact(action):
        if not query.get("idempotent"):
            return {
                "decision": "HUMAN-REQUIRED",
                "tier": 2,
                "justification": "High-impact action must be idempotent"
            }
    
    # Production data operations require additional checks
    if is_production_data(query["destination_resource"]):
        if not has_backup_verification(query):
            return {
                "decision": "DENY",
                "tier": 3,
                "justification": "Production data operation requires backup verification"
            }
    
    return {"decision": "PROCEED", "safety_checks_passed": True}
```

### 3.4 Resource and Budget Governance

**Requirement:** Enforce real-time budget and resource quota validation.

**Pre-Execution Validation:**
```python
def validate_resource_budget(query, agent_manifest):
    """Validate resource request against quotas and budget"""
    
    # Extract resource requirements
    estimated_cost = query.get("estimated_cost", 0)
    cpu_required = query["action_parameters"].get("cpu_cores", 0)
    memory_required = query["action_parameters"].get("memory_gb", 0)
    
    # Get current consumption
    current_usage = get_current_usage(query["source_agent_identity"])
    current_spending = get_current_spending(query["source_agent_identity"])
    
    # Check budget
    monthly_budget = agent_manifest["budget"]["monthly_limit_usd"]
    remaining_budget = monthly_budget - current_spending
    
    if estimated_cost > remaining_budget:
        return {
            "decision": "HUMAN-REQUIRED",
            "tier": 2,
            "justification": f"Cost ${estimated_cost} exceeds remaining budget ${remaining_budget}",
            "escalation_route": "finops_team",
            "budget_details": {
                "monthly_limit": monthly_budget,
                "current_spending": current_spending,
                "remaining": remaining_budget,
                "requested": estimated_cost
            }
        }
    
    # Check resource quotas
    cpu_quota = agent_manifest["resource_quotas"]["compute"]["cpu_cores"]
    memory_quota = agent_manifest["resource_quotas"]["compute"]["memory_gb"]
    
    if current_usage["cpu"] + cpu_required > cpu_quota:
        return {
            "decision": "HUMAN-REQUIRED",
            "tier": 2,
            "justification": f"CPU quota exceeded: {current_usage['cpu']+cpu_required} > {cpu_quota}",
            "escalation_route": "namespace_owner"
        }
    
    if current_usage["memory"] + memory_required > memory_quota:
        return {
            "decision": "HUMAN-REQUIRED",
            "tier": 2,
            "justification": f"Memory quota exceeded: {current_usage['memory']+memory_required} > {memory_quota}",
            "escalation_route": "namespace_owner"
        }
    
    # Soft limit warning (80% threshold)
    if current_spending / monthly_budget >= 0.8:
        emit_warning(f"Agent {query['source_agent_identity']} at 80% budget utilization")
    
    return {
        "decision": "PROCEED",
        "within_quota": True,
        "budget_utilization": current_spending / monthly_budget
    }
```

---

## 4. Output and Auditability Requirements

### 4.1 Structured Decision Output

**Requirement:** The GPIS MUST return a structured response for every query.

**Response Schema:**
```json
{
  "decision_id": "dec-2025-11-22-abc123",
  "timestamp": "2025-11-22T19:03:22.123456Z",
  "request_id": "req-xyz789",
  "decision": "AUTO-APPROVE",
  "tier": 1,
  "justification": "Action 'scale_deployment' is within agent privileges (deployment.scale) and quotas (CPU: 12/16 cores, Budget: $3,200/$5,000)",
  "policy_citation": {
    "policy_id": "unified-governance-v3",
    "policy_version": "3.0.0",
    "policy_hash": "sha256:abc123...",
    "rule_applied": "action_tiers.tier_1.scale_within_quota"
  },
  "compliance_metadata": {
    "cost_center": "CC-12345",
    "project_code": "PROJ-ALPHA-2025",
    "environment": "production",
    "estimated_cost": 15.50,
    "trace_id": "trace-xyz789"
  },
  "next_steps": "Proceed with deployment scaling. Action will be logged to Decision Ledger for audit.",
  "audit_log_id": "audit-2025-11-22-def456",
  "escalation_id": null,
  "expires_at": "2025-11-22T19:08:22Z"
}
```

**For Tier 2 (Human Required):**
```json
{
  "decision_id": "dec-2025-11-22-xyz456",
  "timestamp": "2025-11-22T19:03:22.123456Z",
  "request_id": "req-abc123",
  "decision": "HUMAN-REQUIRED",
  "tier": 2,
  "justification": "Estimated cost $75 would exceed remaining budget $50 (current utilization: 90%). Per policy, budget overages require FinOps team approval.",
  "policy_citation": {
    "policy_id": "unified-governance-v3",
    "policy_version": "3.0.0",
    "policy_hash": "sha256:abc123...",
    "rule_applied": "resource_quotas.budget.overage_requires_approval"
  },
  "escalation_id": "ESC-2025-456",
  "escalation_route": "finops_team",
  "escalation_details": {
    "assigned_to": ["finops-team@example.com", "budget-owner@example.com"],
    "sla_hours": 4,
    "timeout_action": "auto-deny",
    "approval_url": "https://governance.example.com/approve/ESC-2025-456",
    "notification_channels": ["slack:#finops-alerts", "email", "servicenow:INC789012"]
  },
  "next_steps": "Escalation ESC-2025-456 created. FinOps team and budget owner notified. Typical SLA: 4 hours. You will be notified when approved or denied.",
  "audit_log_id": "audit-2025-11-22-ghi789",
  "expires_at": "2025-11-22T23:03:22Z"
}
```

### 4.2 Decision Ledger Integration

**Requirement:** 100% of decision requests MUST be written to the Decision Ledger.

**Ledger Entry Schema:**
```json
{
  "decision_id": "dec-2025-11-22-abc123",
  "timestamp": "2025-11-22T19:03:22.123456Z",
  "agent_identity": "team-alpha-deploy-001",
  "namespace": "team-alpha",
  "action": "scale_deployment",
  "action_tier": 1,
  "decision": "AUTO-APPROVE",
  "policy_id": "unified-governance-v3",
  "policy_version": "3.0.0",
  "policy_hash": "sha256:abc123...",
  "justification": "Action within privileges and quotas",
  "cost_center": "CC-12345",
  "project_code": "PROJ-ALPHA-2025",
  "estimated_cost": 15.50,
  "actual_cost": null,
  "trace_id": "trace-xyz789",
  "operator": "system",
  "resource_affected": "deployment/web-app",
  "outcome": "success",
  "signature": "base64_encoded_signature",
  "ledger_sequence": 123456,
  "previous_hash": "sha256:prev_entry_hash"
}
```

**Integrity Verification:**
- Each entry includes hash of previous entry (blockchain-style chain)
- Cryptographic signature on each entry
- Periodic Merkle tree root publication for tamper detection
- Immutable storage with WORM guarantees

### 4.3 Financial Attribution

**Requirement:** Feed metadata to Attribution & Cost Engine for 100% consumption auto-tagging.

**Cost Attribution Flow:**
```
GPIS Decision → Decision Ledger → Attribution Engine → Chargeback Report
```

**Required Metadata:**
- `cost_center`: Business cost center code
- `project_code`: Project tracking code
- `estimated_cost`: Pre-execution cost estimate
- `actual_cost`: Post-execution actual cost (updated later)
- `resource_tags`: Auto-applied tags for cloud resources

**Chargeback Process:**
1. GPIS logs decision with cost metadata
2. Attribution Engine aggregates costs by cost_center and project_code
3. Monthly chargeback report auto-generated
4. Published to cost center owners
5. 30-day dispute window via governance team

---

## 5. Required Metrics and Monitoring

### 5.1 Policy Adherence Metrics

**Requirement:** Track agent compliance with policy inquiry requirements.

**Metrics:**

| Metric | Definition | Target | Alert Threshold |
|--------|------------|--------|-----------------|
| **Policy Hit Rate** | % of agent actions that query GPIS first | 100% | <95% |
| **Bypass Attempts** | # of actions executed without GPIS approval | 0 | >0 |
| **Policy Compliance** | % of actions that comply with policy | >99% | <98% |
| **Unauthorized Actions** | # of Tier 3 denials | <10/month | >10/month |

**Monitoring:**
```python
# Prometheus metrics
gpis_policy_hit_rate = Gauge('gpis_policy_hit_rate', 'Percentage of actions querying GPIS')
gpis_bypass_attempts = Counter('gpis_bypass_attempts', 'Actions executed without GPIS approval')
gpis_policy_violations = Counter('gpis_policy_violations', 'Policy violation attempts')
```

### 5.2 Approval Latency Metrics

**Requirement:** Track decision latency to ensure performance targets are met.

**Metrics:**

| Metric | Definition | Target | Alert Threshold |
|--------|------------|--------|-----------------|
| **Tier 0 Latency** | p95 latency for Tier 0 decisions | <50ms | >100ms |
| **Tier 1 Latency** | p95 latency for Tier 1 decisions | <100ms | >200ms |
| **Tier 2 Latency** | p95 latency for Tier 2 escalations | <2s | >5s |
| **Tier 3 Latency** | p95 latency for Tier 3 denials | <50ms | >100ms |

**Monitoring:**
```python
# Prometheus histogram
gpis_decision_latency = Histogram(
    'gpis_decision_latency_seconds',
    'GPIS decision latency',
    ['tier', 'decision']
)
```

### 5.3 Human Escalation Rate

**Requirement:** Track escalation rate to ensure ≥80% autonomy target.

**Metrics:**

| Metric | Definition | Target | Alert Threshold |
|--------|------------|--------|-----------------|
| **Autonomy Rate** | (Tier 0 + Tier 1) / Total Actions | ≥80% | <75% for 3 days |
| **Escalation Rate** | Tier 2 / Total Actions | ≤20% | >25% for 3 days |
| **Denial Rate** | Tier 3 / Total Actions | <5% | >10% |
| **Approval Time** | Avg time for Tier 2 human approval | <4 hours | >8 hours |

**Mandatory Redesign Triggers:**
- Autonomy rate <80% for 14 consecutive days
- >100 Tier 2 escalations per agent per week
- >10 Tier 3 denials per agent per month

### 5.4 Cost per Task/Session

**Requirement:** Track cost attribution for every decision and subsequent action.

**Metrics:**

| Metric | Definition | Target | Alert Threshold |
|--------|------------|--------|-----------------|
| **Cost per Decision** | Avg cost to process GPIS query | <$0.01 | >$0.05 |
| **Cost per Task** | Avg cost for approved action | Varies by tier | >Budget |
| **Budget Utilization** | % of monthly budget consumed | <100% | >80% |
| **Cost Anomaly** | Sudden cost spike detection | N/A | >2x baseline |

**Monitoring:**
```python
# Prometheus metrics
gpis_cost_per_decision = Histogram('gpis_cost_per_decision_usd', 'Cost per GPIS decision')
gpis_budget_utilization = Gauge('gpis_budget_utilization_percent', 'Budget utilization %', ['agent_identity'])
```

### 5.5 Policy Violation Alert Rate

**Requirement:** Track frequency of denied or out-of-scope actions.

**Metrics:**

| Metric | Definition | Target | Alert Threshold |
|--------|------------|--------|-----------------|
| **Tier 3 Denials** | # of prohibited action attempts | <10/month | >10/month |
| **Scope Violations** | # of out-of-namespace attempts | <5/month | >5/month |
| **Budget Overruns** | # of budget overage attempts | <20/month | >20/month |
| **Quota Violations** | # of quota exceeded attempts | <15/month | >15/month |

**Alert Routing:**
- Tier 3 denials → Security team (immediate)
- Scope violations → Governance team + namespace owner
- Budget overruns → FinOps team
- Quota violations → Namespace owner

---

## 6. Gap Analysis: Current vs. Required State

### 6.1 Existing Framework Strengths

**✅ Already Implemented:**

1. **Policy Engine Concept** (Section 2.2 of v3.0)
   - Action tier classification (0-3)
   - Approval routing logic
   - Policy versioning with hash verification
   - **Gap:** Not yet implemented as a standalone service

2. **Decision Ledger** (Section 2.5 of v3.0)
   - Immutable storage requirements defined
   - Required fields specified
   - Retention policies established
   - **Gap:** No production implementation

3. **Identity Issuer** (Section 2.1 of v3.0)
   - Identity requirements defined
   - Namespace binding specified
   - Rotation policies established
   - **Gap:** No integration with GPIS

4. **Attribution & Cost Engine** (Section 2.3 of v3.0)
   - Auto-tagging requirements defined
   - Budget tracking specified
   - Chargeback automation outlined
   - **Gap:** No real-time integration with GPIS

5. **Cross-Agent Communication** (Section 15 of v3.0)
   - Message format defined
   - Security requirements specified
   - **Gap:** No GPIS-specific protocol

6. **Governance Agent Architecture** (GOVERNANCE-AGENT-ARCHITECTURE.md)
   - AI-native governance concept
   - MCP protocol integration
   - Natural language policy evaluation
   - **Gap:** Not production-ready

### 6.2 Critical Gaps

**❌ Missing Components:**

1. **GPIS Service Implementation**
   - **Status:** Concept exists, no production code
   - **Required:** Standalone service with REST/gRPC API
   - **Priority:** CRITICAL
   - **Effort:** 4-6 weeks

2. **Real-Time Policy Evaluation Engine**
   - **Status:** Policy rules defined in YAML, no runtime engine
   - **Required:** OPA, Kyverno, or custom policy engine
   - **Priority:** CRITICAL
   - **Effort:** 2-3 weeks

3. **Decision Ledger Storage**
   - **Status:** Requirements defined, no implementation
   - **Required:** S3 + Object Lock or equivalent
   - **Priority:** CRITICAL
   - **Effort:** 1-2 weeks

4. **Identity Attestation Integration**
   - **Status:** Requirements defined, no integration
   - **Required:** SPIFFE/SPIRE, Vault PKI, or platform-native
   - **Priority:** HIGH
   - **Effort:** 2-3 weeks

5. **Real-Time Budget Tracking**
   - **Status:** Cost tracking scripts exist, no real-time integration
   - **Required:** Live budget API integration
   - **Priority:** HIGH
   - **Effort:** 2-3 weeks

6. **Escalation Workflow Automation**
   - **Status:** Jira integration exists, no GPIS integration
   - **Required:** Automated escalation routing
   - **Priority:** MEDIUM
   - **Effort:** 1-2 weeks

7. **Performance Optimization**
   - **Status:** No latency targets defined
   - **Required:** Caching, load balancing, circuit breakers
   - **Priority:** MEDIUM
   - **Effort:** 2-3 weeks

8. **Metrics and Monitoring**
   - **Status:** OpenTelemetry framework exists, no GPIS metrics
   - **Required:** Prometheus metrics, Grafana dashboards
   - **Priority:** MEDIUM
   - **Effort:** 1 week

### 6.3 Alignment Opportunities

**🔄 Leverage Existing Components:**

1. **Governance Agent (GOVERNANCE-AGENT-ARCHITECTURE.md)**
   - Use as GPIS decision engine
   - Integrate Claude/GPT-4 for natural language policy evaluation
   - Leverage MCP protocol for agent communication

2. **Gatekeeper Script (ai-project-gatekeeper-v2.py)**
   - Extend to GPIS policy evaluation logic
   - Reuse ROI calculator and project evaluator
   - Integrate with shared_utils.py

3. **Jira Integration (validate-jira-approval.py)**
   - Use for Tier 2 escalation workflow
   - Leverage PKI signature verification
   - Integrate webhook receiver for real-time approvals

4. **OpenTelemetry SIEM (otel-siem-emitter.py)**
   - Use for GPIS decision logging
   - Leverage OCSF mapping for compliance
   - Integrate with Decision Ledger

5. **Terraform Modules (terraform/modules/)**
   - Deploy GPIS infrastructure
   - Leverage KMS, Secrets Manager, CloudTrail modules
   - Use for production deployment

---

## 7. Implementation Roadmap

### Phase 1: Core GPIS Service (Weeks 1-4)

**Objective:** Deploy minimal viable GPIS with Tier 0/1 auto-approval.

**Deliverables:**
1. **GPIS API Service**
   - REST API with `/evaluate` endpoint
   - JWT authentication
   - Basic policy evaluation (Tier 0/1 only)
   - In-memory policy cache

2. **Policy Engine Integration**
   - OPA or custom policy engine
   - Load policies from Git
   - Hash verification

3. **Decision Ledger (Basic)**
   - S3 with Object Lock
   - Async write queue
   - Basic schema validation

4. **Identity Validation**
   - JWT signature verification
   - Namespace validation
   - Basic quota checks

**Success Criteria:**
- ≥95% of Tier 0/1 decisions <100ms latency
- 100% of decisions logged to ledger
- 0 unauthorized actions

### Phase 2: Human Escalation (Weeks 5-6)

**Objective:** Implement Tier 2 escalation workflow.

**Deliverables:**
1. **Escalation Routing**
   - Jira integration for Tier 2 approvals
   - Slack notifications
   - ServiceNow ticket creation

2. **Approval Workflow**
   - Human approval UI
   - Timeout handling (auto-deny)
   - Approval audit trail

3. **Budget Integration**
   - Real-time budget API
   - Overage detection
   - FinOps team routing

**Success Criteria:**
- Tier 2 escalations routed within 5 seconds
- 100% of escalations tracked in Jira
- <4 hour avg approval time

### Phase 3: Advanced Features (Weeks 7-8)

**Objective:** Implement Tier 3 denials, advanced safety checks, and optimization.

**Deliverables:**
1. **Tier 3 Denial Logic**
   - Prohibited action detection
   - Security team alerting
   - Incident logging

2. **Safety Checks**
   - Dry-run enforcement
   - Rollback plan validation
   - Idempotency checks

3. **Performance Optimization**
   - Policy caching
   - Load balancing
   - Circuit breakers

**Success Criteria:**
- Tier 3 denials <50ms latency
- 100% of destructive actions require dry-run
- ≥99.9% GPIS availability

### Phase 4: Production Hardening (Weeks 9-12)

**Objective:** Production deployment with full monitoring and compliance.

**Deliverables:**
1. **Monitoring & Metrics**
   - Prometheus metrics
   - Grafana dashboards
   - Alerting rules

2. **Compliance Integration**
   - NIST 800-53 control mapping
   - Audit report generation
   - Compliance dashboard

3. **High Availability**
   - Multi-region deployment
   - Geographic replication
   - Disaster recovery

**Success Criteria:**
- ≥80% autonomy rate achieved
- 99.9% GPIS uptime
- 100% compliance with audit requirements

---

## 8. Integration with Existing Framework

### 8.1 Mapping to v3.0 Components

**GPIS Integration Points:**

| v3.0 Component | GPIS Integration | Status |
|----------------|------------------|--------|
| **Identity Issuer** (2.1) | Provides agent identities for GPIS validation | ✅ Defined |
| **Policy Engine** (2.2) | **GPIS IS the Policy Engine** | ⚠️ To Implement |
| **Attribution & Cost Engine** (2.3) | Receives cost metadata from GPIS decisions | ✅ Defined |
| **Reconciliation Controller** (2.4) | Queries GPIS for drift remediation approval | ⚠️ To Integrate |
| **Decision Ledger** (2.5) | Stores all GPIS decisions immutably | ⚠️ To Implement |
| **Declarative Config** (2.6) | Sources policies for GPIS evaluation | ✅ Defined |

### 8.2 Agent Workflow Integration

**Before GPIS:**
```
Agent → Action → (Maybe) Audit Log
```

**After GPIS:**
```
Agent → GPIS Query → Decision → Action → Decision Ledger → Attribution Engine
```

**Example Flow:**
```python
# Agent requests action
response = gpis_client.evaluate({
    "agent_identity": "team-alpha-deploy-001",
    "action": "scale_deployment",
    "namespace": "team-alpha",
    "justification": "Traffic spike",
    "cost_center": "CC-12345",
    "project_code": "PROJ-ALPHA-2025"
})

if response["decision"] == "AUTO-APPROVE":
    # Execute action
    execute_action()
    
elif response["decision"] == "HUMAN-REQUIRED":
    # Wait for approval
    wait_for_approval(response["escalation_id"])
    
else:  # DENY
    # Log denial and halt
    log_denial(response["justification"])
```

### 8.3 Governance Agent Integration

**Leverage Existing Governance Agent:**

The GPIS can be implemented as an extension of the existing Governance Agent (GOVERNANCE-AGENT-ARCHITECTURE.md):

```python
class GPIS(GovernanceAgent):
    """GPIS extends Governance Agent with real-time policy enforcement"""
    
    def __init__(self):
        super().__init__()
        self.policy_engine = OPAPolicyEngine()
        self.decision_ledger = DecisionLedger()
        self.budget_tracker = BudgetTracker()
        
    async def evaluate_request(self, request: dict) -> dict:
        """Main GPIS evaluation endpoint"""
        
        # 1. Validate identity
        identity_check = await self.validate_identity(request)
        if not identity_check["valid"]:
            return self.deny(identity_check["reason"])
        
        # 2. Validate scope
        scope_check = await self.validate_scope(request)
        if not scope_check["valid"]:
            return self.escalate(scope_check["reason"])
        
        # 3. Check budget/quotas
        budget_check = await self.validate_budget(request)
        if not budget_check["within_quota"]:
            return self.escalate(budget_check["reason"])
        
        # 4. Classify action tier
        tier = await self.classify_action_tier(request)
        
        # 5. Make decision
        if tier == 0 or tier == 1:
            decision = await self.auto_approve(request, tier)
        elif tier == 2:
            decision = await self.escalate_to_human(request)
        else:  # tier == 3
            decision = await self.deny(request)
        
        # 6. Log to Decision Ledger
        await self.decision_ledger.log(decision)
        
        return decision
```

---

## Appendix A: Example GPIS Deployment (Kubernetes)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpis
  namespace: governance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gpis
  template:
    metadata:
      labels:
        app: gpis
    spec:
      containers:
      - name: gpis
        image: governance.ai/gpis:v1.0
        env:
        - name: POLICY_REPO_URL
          value: "https://github.com/org/governance-policies.git"
        - name: DECISION_LEDGER_BUCKET
          value: "s3://governance-decision-ledger"
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: anthropic-credentials
              key: api-key
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: gpis
  namespace: governance
spec:
  selector:
    app: gpis
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
```

---

## Appendix B: Example Policy Definition (OPA Rego)

```rego
package governance.gpis

import future.keywords.if
import future.keywords.in

# Tier 0: Auto-approve read-only operations
tier_0_actions := {
    "read_own_data",
    "list_resources_in_namespace",
    "status_check",
    "get_metrics"
}

# Tier 1: Auto-approve routine operations
tier_1_actions := {
    "write_to_own_workspace",
    "scale_within_quota",
    "normal_deployment",
    "create_resource_in_namespace"
}

# Tier 3: Always deny prohibited actions
tier_3_actions := {
    "credential_sharing",
    "audit_log_deletion",
    "policy_bypass",
    "rm_rf_root",
    "cross_namespace_modify"
}

# Main decision rule
decision := {
    "decision": decision_type,
    "tier": tier,
    "justification": justification
} if {
    tier := classify_tier(input.action)
    decision_type := make_decision(tier, input)
    justification := explain_decision(tier, decision_type, input)
}

# Classify action tier
classify_tier(action) := 3 if action in tier_3_actions
classify_tier(action) := 0 if action in tier_0_actions
classify_tier(action) := 1 if {
    action in tier_1_actions
    within_quota(input)
}
classify_tier(action) := 2  # Default to human approval

# Make decision based on tier
make_decision(0, _) := "AUTO-APPROVE"
make_decision(1, _) := "AUTO-APPROVE"
make_decision(2, _) := "HUMAN-REQUIRED"
make_decision(3, _) := "DENY"

# Check if within quota
within_quota(request) if {
    agent := data.agents[request.agent_identity]
    current_usage := data.usage[request.agent_identity]
    
    current_usage.cpu + request.cpu_required <= agent.quotas.cpu_cores
    current_usage.memory + request.memory_required <= agent.quotas.memory_gb
    current_usage.spending + request.estimated_cost <= agent.budget.monthly_limit_usd
}

# Explain decision
explain_decision(tier, decision, request) := msg if {
    tier == 0
    msg := sprintf("Read-only operation '%s' auto-approved", [request.action])
}

explain_decision(tier, decision, request) := msg if {
    tier == 1
    msg := sprintf("Action '%s' within privileges and quotas, auto-approved", [request.action])
}

explain_decision(tier, decision, request) := msg if {
    tier == 2
    msg := sprintf("Action '%s' requires human approval", [request.action])
}

explain_decision(tier, decision, request) := msg if {
    tier == 3
    msg := sprintf("Action '%s' is prohibited by policy", [request.action])
}
```

---

## Conclusion

The **Governance Policy Inquiry Service (GPIS)** is the critical missing component that transforms your governance framework from passive documentation into an active, real-time enforcement system. By implementing GPIS, you will achieve:

✅ **≥80% Autonomous Operation** through intelligent auto-approval  
✅ **100% Accountability** via immutable Decision Ledger  
✅ **Zero Trust Enforcement** with continuous verification  
✅ **Real-Time Policy Enforcement** with <100ms latency  
✅ **Complete Cost Attribution** with automatic tagging  

**Next Steps:**
1. Review this specification with stakeholders
2. Prioritize Phase 1 implementation (Weeks 1-4)
3. Allocate engineering resources (2-3 engineers)
4. Begin GPIS service development
5. Integrate with existing Governance Agent architecture

**Estimated Timeline:** 12 weeks to production-ready GPIS  
**Estimated Effort:** 6-8 engineer-months  
**Estimated Cost:** $50K-$100K (engineering + infrastructure)

---

**Document Status:** DRAFT - Awaiting Review  
**Review By:** Governance Authority, Security Team, FinOps Team  
**Approval Required:** CTO, CISO, CFO  
**Target Approval Date:** 2025-12-15
