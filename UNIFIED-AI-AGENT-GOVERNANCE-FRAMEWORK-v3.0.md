# Unified AI Agent Governance Framework v3.0

**Status:** SINGLE SOURCE OF TRUTH
**Version:** 3.0.0
**Last Updated:** 2025-11-21
**Supersedes:** v2.1.0 (strategic) and v2.0 (tactical)
**Policy Hash:** `<SHA256 to be computed on finalization>`
**Registry:** `https://governance.%domain%/registry/v3.0`

---

## Document Purpose

This framework establishes **mandatory operational boundaries** for AI agents operating in production DevSecOps environments. It unifies strategic architecture with tactical guardrails to enable **≥80% autonomous operation** while maintaining security, compliance, and reliability.

**Applies to all AI agents that:**
- Make decisions without continuous human supervision
- Consume resources (compute, storage, network, APIs, budget)
- Modify system or environment state
- Operate across build, deployment, or runtime phases

**No exceptions** without time-bound, written approval from the Governance Authority.

---

# PART I: STRATEGIC FOUNDATION

## 1. Scope, Authority & Core Principles

### 1.1 Authority
This framework is **mandatory and non-negotiable** for:
- All autonomous AI agents in production
- Agents in staging environments that access production resources
- Agents with privilege escalation capabilities
- Agents that consume billable resources

### 1.2 Core Principles

1. **Maximum Autonomy, Total Accountability**
   Target: ≥80% actions auto-approved, 100% actions traceable

2. **Zero Trust Always**
   Every request authenticated and authorized in real-time, regardless of source

3. **Immutable by Design**
   All configuration declarative and version-controlled

4. **Audit is Non-Negotiable**
   Every decision and consumption event recorded forever

5. **Cost Attribution Without Exception**
   Zero manual cost allocation allowed

6. **Security Through Architecture**
   Governance is the substrate agents run on, not an afterthought

7. **Fail Safe, Fail Visible**
   Default to deny; escalate with full context

---

## 2. Mandatory Architectural Components

**Minimum viable set:** Six abstract components required. Implementations may combine them but must satisfy all functions.

### 2.1 Identity Issuer
**Function:** Issues, rotates, attests, and revokes unique cryptographic identities bound to agent manifests.

**Requirements:**
- Each running instance gets unique, non-transferable identity
- Identity includes: namespace, permissions, quotas, budgets
- Supports JWT, mTLS, or platform-native attestation
- Automatic revocation on policy violation or drift

**Implementation Examples:** Vault PKI, SPIFFE/SPIRE, Azure Managed Identity, AWS IAM Roles for Service Accounts

---

### 2.2 Policy Engine
**Function:** Single decision point for admission control, runtime authorization, action tiering, and human-approval routing.

**Requirements:**
- All policies as code in version control
- Real-time policy evaluation per request
- Action tier classification (0-3)
- Approval routing with configurable SLAs
- Policy versioning with hash verification

**Implementation Examples:** Open Policy Agent (OPA), Kyverno, AWS IAM Policy Evaluation, custom policy service

---

### 2.3 Attribution & Cost Engine
**Function:** Automatically tags 100% of resource consumption with agent identity and business context; transforms into chargeback-ready allocations.

**Requirements:**
- Auto-tagging at resource creation (compute, storage, API calls)
- Real-time budget tracking per agent identity
- Version-controlled rate card for cost calculations
- Automated chargeback report generation
- Anomaly detection and alerting

**Implementation Examples:** Cloud provider tagging + FinOps platform, Kubecost, custom metering service

---

### 2.4 Reconciliation Controller
**Function:** Detects drift from declared state and either auto-remediates or terminates the agent.

**Requirements:**
- Continuous comparison of desired vs actual state
- Auto-remediation for Tier 0 drift
- Escalation for Tier 1+ drift
- Automatic termination on policy violation
- Drift audit trail

**Implementation Examples:** Kubernetes Operators, AWS Config Rules, Azure Policy, Terraform Cloud Drift Detection

---

### 2.5 Decision Ledger
**Function:** Append-only, cryptographically-verifiable record of all governance events.

**Requirements:**
- Immutable storage (write-once-read-many)
- Structured JSON format with required fields
- Cryptographic integrity (hash chain or signatures)
- Minimum 7-year retention for financial events
- Access control to authorized governance operators only

**Must Record:**
- Policy decisions & justifications
- Human approvals/denials
- Deployments & failures
- Resource attributions & chargebacks
- Identity lifecycle events
- Drift detections & remediations

**Implementation Examples:** AWS CloudTrail + S3 Object Lock, Azure Monitor + immutable storage, blockchain-based audit log, Splunk with write-once indexes

---

### 2.6 Declarative Configuration & Delivery System
**Function:** Version-controlled repository + pipeline as the **only allowed source** of agent configuration and deployment.

**Requirements:**
- All agent manifests in version control (Git)
- CI/CD pipeline with governance validation gates
- Admission control rejects non-compliant manifests
- Immutable deployment artifacts
- Rollback capability to previous manifest versions

**Implementation Examples:** GitOps (ArgoCD, FluxCD), Terraform Cloud, Azure DevOps Pipelines, GitHub Actions + OPA

---

## 3. Action Tiers & Autonomy Target (The 80/20 Rule)

Agents **MUST** achieve **≥80% auto-approval** in production. Sustained >20% human approval rate triggers **mandatory redesign**.

### 3.1 Tier Definitions

| Tier | Approval Mode | SLA | Examples | Escalation on Timeout |
|------|---------------|-----|----------|----------------------|
| **0** | Auto-approve | N/A | Read own data, list resources in namespace, routine status checks | N/A |
| **1** | Auto-approve + audit | N/A | Write to own workspace, scale within quota, normal deployments | N/A |
| **2** | Human approval required | 4 hours (configurable) | Budget overage, privilege escalation, cross-namespace access, production data read | Auto-deny |
| **3** | Always deny | N/A | Credential sharing, audit log deletion, policy bypass, production data deletion | Logged incident |

### 3.2 Approval Routing

**Tier 2 routing logic:**
- Budget overage → FinOps team + budget owner
- Security escalation → Security Operations Center (SOC)
- Compliance issue → Compliance team + legal (if regulatory)
- Cross-namespace → Namespace owner + governance team

**Approval requirements:**
- Structured request with: context, justification, impact analysis, rollback plan
- Approver identity logged with decision
- Timeout defaults to **deny** (never auto-approve on timeout)

### 3.3 Autonomy Metrics

**Required tracking:**
- `autonomy_rate = (Tier 0 + Tier 1 actions) / total_actions`
- Target: ≥80%
- Measurement period: Rolling 7-day window
- Alert threshold: <75% for 3 consecutive days

**Mandatory redesign triggers:**
- Autonomy rate <80% for 14 consecutive days
- >100 Tier 2 escalations per agent per week
- >10 Tier 3 denials per agent per month

---

## 4. Identity, Zero Trust & Least Privilege

### 4.1 Identity Requirements

**Every running agent instance:**
- Gets unique, cryptographically-signed identity at startup
- Identity bound to agent manifest (config hash)
- Identity encodes: namespace, permissions, quotas, budgets
- No identity delegation or sharing ever permitted

**Identity lifecycle:**
- Issued: On deployment by Identity Issuer
- Rotated: Per policy schedule (default: every 24 hours)
- Attested: On every protected resource access
- Revoked: On termination, drift, or policy violation

### 4.2 Zero Trust Implementation

**Per-request evaluation:**
- Trust is evaluated on **every request**, not at session start
- Location grants no privilege (network location irrelevant)
- Credentials expire rapidly (default max: 1 hour)
- All inter-agent communication authenticated

**Requirements:**
- mTLS for all inter-service communication
- JWT or platform attestation for API calls
- No hardcoded credentials anywhere
- No long-lived tokens

### 4.3 Least Privilege Enforcement

**Privilege declaration:**
- All required privileges declared in agent manifest
- Policy Engine validates at admission time
- Runtime enforcement by platform RBAC + Policy Engine

**Automatic privilege revocation:**
- Unused privileges revoked after 30 days
- Privilege usage tracked in Decision Ledger
- Manual privilege grants require time-bound expiration

---

## 5. Cost Attribution & Chargeback

### 5.1 Tagging Requirements

**100% auto-tagging** at resource creation with:
- `agent_identity`: Unique agent identifier
- `namespace`: Project/team namespace
- `cost_center`: Business cost center code
- `project_code`: Project tracking code
- `environment`: dev/staging/prod
- `owner`: Responsible team/individual

**Tag enforcement:**
- Resources without tags rejected at creation
- Tag immutability after creation
- Tag compliance monitoring

### 5.2 Real-Time Budget Tracking

**Per-agent budgets:**
- Declared in agent manifest
- Enforced by Policy Engine before resource allocation
- Real-time consumption tracking
- Alert at 80% budget utilization
- Block at 100% (or route to Tier 2 approval)

**Budget dimensions:**
- Compute hours
- Storage GB-months
- Network egress GB
- API call counts
- External service costs (LLM APIs, etc.)

### 5.3 Chargeback Automation

**Monthly chargeback process:**
1. Attribution Engine aggregates tagged consumption
2. Rate card applies current pricing
3. Chargeback report auto-generated
4. Published to cost_center and project_code owners
5. Dispute process via governance team (30-day window)

**Prohibited:** Manual cost allocation or adjustments without audit trail

---

# PART II: OPERATIONAL GUARDRAILS

## 6. Namespace & Scope Rules

### 6.1 Namespace Boundaries

**Strict isolation:**
- Agents operate **only** within assigned namespace (`%namespace%`)
- Namespace validated at startup via signed metadata
- Cross-namespace operations require explicit Tier 2 approval

**Namespace identity:**
- Encoded in cryptographic identity
- Validation: JWT claims, manifest hash, attestation signature
- Mismatch results in immediate termination

### 6.2 Scope Clarification

**Before action, agents must:**
- Confirm resource ownership via metadata/tags
- Verify resource is within namespace scope
- If uncertain, **escalate for clarification** (never assume)

**Prohibited:**
- Creating resources outside namespace
- Referencing or suggesting actions in other namespaces
- Assuming ownership of untagged resources

---

## 7. Safety & Destruction Prevention Rules

### 7.1 Inspect-First Protocol

**All operations begin with read-only inspection:**
```
1. List affected resources
2. Display current state
3. Identify dependencies
4. Assess blast radius
5. THEN propose modification
```

### 7.2 Destructive Operation Requirements

**Before any destructive action:**

**Required steps:**
1. **Scope confirmation:** Display exact resources to be affected
2. **Impact analysis:** Estimate blast radius and dependencies
3. **Idempotency check:** Verify operation can be safely retried
4. **Rollback plan:** Document recovery procedure
5. **Human confirmation:** Explicit approval required

**Required for confirmation:**
- Resource type and identifiers
- Expected outcome
- Rollback procedure
- Estimated downtime/impact
- Related dependencies

### 7.3 Sandbox Testing

**High-risk operations must:**
- Run first in simulation/dry-run mode (see Section 12)
- Execute in sandbox/staging before production
- Validate idempotency with repeated execution

**High-risk defined as:**
- Production data deletion
- Schema migrations
- Multi-resource cascading changes
- Network or security policy changes

### 7.4 Prohibited Actions

**Always Tier 3 (deny):**
- `rm -rf /` or equivalent root deletion
- Recursive deletion without explicit file list
- Credential/secret exposure in logs
- Audit log modification or deletion
- Policy bypass or circumvention
- Privilege escalation without approval flow
- Cross-namespace modification
- Manual cost allocation

---

## 8. Responsibility Separation (Build/Runtime/Orchestration)

### 8.1 Phase Definitions

| Phase | Responsibility | Allowed Operations | Prohibited Operations |
|-------|----------------|-------------------|----------------------|
| **Build-time** | Static setup | Install dependencies, compile code, create templates | Runtime environment variables, dynamic config, running services |
| **Runtime** | Application logic | Execute business logic, process requests | Environment variable generation, infrastructure changes |
| **Orchestration** | System composition | Declare env vars, ports, volumes, resources in manifests | Dynamic infrastructure changes, manual config injection |
| **Deployment** | Delivery | Apply manifests, run pipelines, validate compliance | Runtime code modification, direct server access |

### 8.2 Environment Variable Rules

**Declaration requirements:**
- All environment variables **declared in orchestration manifests**
- No runtime generation or modification of env vars
- Config changes require new manifest version + deployment

**Prohibited patterns:**
- `export VAR=value` in entrypoint scripts
- Runtime env var injection via APIs
- Config generation at container startup

**Correct pattern:**
```yaml
# docker-compose.yml or Kubernetes manifest
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: url
```

### 8.3 Entrypoint Script Rules

**Limits:**
- Maximum 50 lines (excluding comments)
- Only bootstrapping logic (wait-for dependencies, health checks)
- No business logic or complex conditionals

**Rejection criteria (CI/CD gate):**
- Large or opaque entrypoint scripts (>50 lines)
- Mixed build-time and runtime logic
- Environment variable generation
- Complex conditional logic

**Required instead:**
- Language-native startup functions
- Configuration via manifest
- Explicit dependency waiting

---

## 9. Directory, File & Memory Rules

### 9.1 Directory Scope

**Allowed paths:**
- Project directory: `~/projects/%namespace%/` (Linux/WSL)
- Project directory: `C:\Users\%user%\Projects\%namespace%\` (Windows)
- Temporary: `/tmp/%namespace%-*` with automatic cleanup
- Declared volumes: Per orchestration manifest

**Prohibited operations:**
- Actions outside project directory
- Absolute destructive commands (`rm -rf /`, `rm -rf *` without path)
- Modifications to system directories (`/etc`, `/usr`, `/var` except declared mounts)

### 9.2 File Operation Rules

**Before file deletion:**
- List files to be deleted
- Confirm each file or provide pattern match count
- Require human confirmation for >10 files

**File permissions:**
- Least privilege enforcement (no world-writable: `chmod 777`)
- Respect existing ownership
- Use umask 027 for new files

**Temporary files:**
- Store in `/tmp/%namespace%-<random>` or project-local `.tmp/`
- Automatic cleanup at session end
- No persistent data in temp directories

### 9.3 Memory & State Rules

**Prohibited:**
- Assuming persistent memory across sessions
- Direct system memory manipulation
- Cache data without explicit ephemeral designation

**Allowed persistence:**
- Declared storage mounts in orchestration manifest
- Container volumes with explicit lifecycle
- Agent state stored in approved state backends (etcd, Redis with TTL)

**Ephemeral memory:**
- In-memory caches cleared at session end
- Stateless operation by default
- Persistent checkpoints require human authorization (Tier 2)

---

## 10. Secrets Management

### 10.1 Retrieval Rules

**Approved secret stores only:**
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Kubernetes Secrets (with encryption at rest)

**Prohibited:**
- Hardcoded secrets in code
- Secrets in environment variables (except orchestration-managed)
- Secrets in logs or stdout
- Secrets in version control (even in history)

### 10.2 Secrets Handling

**In-memory only:**
- Secrets loaded into memory at startup
- Never written to disk
- Never logged or serialized

**Least privilege scope:**
- Secrets scoped to specific agent identity
- Access controlled via Policy Engine
- Unused secrets access revoked automatically

### 10.3 Rotation & Lifecycle

**Mandatory rotation:**
- Per policy schedule (default: 90 days for long-lived, 24h for ephemeral)
- Automatic rotation without service interruption
- Old secrets invalidated after grace period (default: 24h)

**No local caching:**
- Secrets fetched per session
- Not persisted between agent runs
- Re-authentication required for each access

---

## 11. Audit & Traceability

### 11.1 Structured Logging

**Format:** JSON with required fields

**Required fields:**
```json
{
  "timestamp": "ISO8601",
  "namespace": "string",
  "agent_identity": "string",
  "action": "string",
  "action_tier": "0|1|2|3",
  "justification": "string",
  "outcome": "success|failure|escalated|denied",
  "operator": "human_identity or 'system'",
  "resource_affected": "string or array",
  "cost_impact": "float (if applicable)",
  "policy_version": "string",
  "trace_id": "string for distributed tracing"
}
```

### 11.2 Log Storage

**Requirements:**
- Immutable, append-only storage
- AWS S3 with Object Lock, Azure Blob immutable storage, or equivalent
- Geographic replication for disaster recovery
- Access restricted to governance operators via IAM

**Retention:**
- Financial events: ≥7 years
- Security events: ≥3 years (or per regulatory requirement)
- Operational events: ≥1 year
- All events: Indefinite for high-risk agents

### 11.3 Sensitive Data Masking

**Before logging:**
- Passwords → `***REDACTED***`
- API keys → `***KEY-REDACTED***`
- Tokens → First 4 + last 4 chars: `abcd...wxyz`
- PII → Hash or mask per privacy policy

---

## 12. Resource Governance & Quotas

### 12.1 Quota Declaration

**All resource quotas in agent manifest:**
```yaml
resource_quotas:
  compute:
    cpu_cores: 4
    memory_gb: 16
    gpu_count: 0
  storage:
    persistent_gb: 100
    ephemeral_gb: 50
  network:
    egress_gb_per_month: 1000
  api_calls:
    llm_calls_per_hour: 100
    external_api_calls_per_day: 10000
```

### 12.2 Pre-Execution Validation

**Before resource allocation:**
1. Check requested resources against declared quotas
2. Check current consumption vs quotas
3. If within quota → auto-approve (Tier 0/1)
4. If exceeds quota → escalate (Tier 2)

### 12.3 Overage Handling

**On quota violation:**
- **Soft limit (80% quota):** Warning logged, owner alerted
- **Hard limit (100% quota):**
  - Operation aborted
  - Policy violation alert emitted
  - Tier 2 approval required to proceed
- **Critical overage (>120% quota):** Agent terminated

**Override process:**
- Signed approval from budget owner + governance
- Time-bound exception (max 7 days)
- Exception logged in Decision Ledger

---

## 13. Simulation & Dry-Run Mode

### 13.1 Dry-Run Requirements

**Enabled by default for:**
- All Tier 2 actions
- All destructive operations
- First-time execution of new operations

**Simulation output:**
```json
{
  "simulation": true,
  "timestamp": "ISO8601",
  "action": "description",
  "affected_resources": ["list"],
  "expected_outcome": "description",
  "estimated_cost": "float",
  "rollback_procedure": "description",
  "command_manifest": {
    "commands": ["array of commands"],
    "idempotent": true,
    "dependencies": ["list"]
  }
}
```

### 13.2 Dry-Run Override

**Requirements to disable:**
- Signed human approval
- Override reason logged
- Override time-limited (expires after execution)

**Never disable for:**
- Production data deletion
- Multi-tenant operations
- Compliance-sensitive actions

---

## 14. Human Escalation Protocols

### 14.1 Escalation Triggers

**Mandatory escalation when:**
- Scope is ambiguous or ownership unclear
- Action is destructive and not in allowed list
- Policy violation detected
- Resource quota exceeded
- Anomaly detected (cost spike, unusual access pattern)
- Cross-namespace operation required

### 14.2 Escalation Content

**Structured incident report:**
```json
{
  "escalation_id": "unique_id",
  "timestamp": "ISO8601",
  "namespace": "string",
  "agent_identity": "string",
  "trigger": "reason for escalation",
  "context": {
    "current_state": "description",
    "intended_action": "description",
    "risk_assessment": "low|medium|high|critical",
    "affected_resources": ["list"],
    "alternatives_considered": ["list"]
  },
  "request": {
    "approval_type": "tier_2 or exception",
    "urgency": "routine|urgent|critical",
    "sla": "4h (or custom)"
  },
  "human_readable_summary": "Plain English explanation"
}
```

### 14.3 Routing Logic

**Routing destinations:**
- Budget issues → FinOps team + budget owner
- Security concerns → SOC + security team
- Compliance issues → Compliance team (+ legal if regulatory)
- Operational issues → On-call engineer + namespace owner
- Policy questions → Governance team

**Routing channels:**
- ServiceNow ticket (for tracking and SLA)
- SlackOps webhook (for real-time notification)
- Email alias (for async review)
- PagerDuty (for critical/urgent escalations)

---

## 15. Cross-Agent Communication

### 15.1 Message Format

**Schema-validated messages:**
```json
{
  "message_id": "unique_id",
  "timestamp": "ISO8601",
  "source_namespace": "string",
  "source_agent_identity": "string",
  "destination_namespace": "string",
  "destination_agent_identity": "string",
  "action": "request|response|notification",
  "payload": {
    "operation": "string",
    "parameters": {},
    "justification": "string"
  },
  "signature": "cryptographic signature",
  "trace_id": "string for distributed tracing"
}
```

### 15.2 Communication Security

**Requirements:**
- mTLS for all inter-agent communication
- Message signing via agent identity
- Timestamp validation (reject messages >5 minutes old)
- Replay protection via message_id tracking

**Rejection criteria:**
- Unsigned messages
- Invalid signatures
- Expired timestamps
- Replayed message_ids
- Malformed schema

### 15.3 Communication Channels

**Approved channels:**
- gRPC over mTLS
- HTTPS with mutual TLS
- Secured message bus (Kafka, RabbitMQ with TLS + SASL)
- Platform-native service mesh (Istio, Linkerd)

**Prohibited:**
- Unencrypted HTTP
- Direct TCP without authentication
- Shared filesystems for message passing
- Database-based queues without encryption

---

## 16. Policy Versioning & Attestation

### 16.1 Policy Verification at Startup

**Agent startup sequence:**
1. Load policy version from manifest
2. Fetch current policy from governance registry
3. Verify policy hash matches expected value
4. If mismatch → refuse execution, log error, escalate
5. If match → proceed with policy enforcement

### 16.2 Policy Metadata

**Required in every agent manifest:**
```yaml
policy_attestation:
  framework_version: "3.0.0"
  policy_id: "unified-governance-v3"
  policy_hash: "sha256:abc123..."
  registry_url: "https://governance.example.com/registry"
  last_validated: "2025-11-21T12:00:00Z"
```

### 16.3 Policy Update Process

**Controlled rollout:**
1. New policy version published to governance registry
2. Staging agents updated first (automatic via pipeline)
3. Production agents updated in waves (blue/green or canary)
4. Agents verify new policy hash before adoption
5. Rollback capability if issues detected

**Version compatibility:**
- Breaking changes require major version bump
- Agents refuse execution if policy version not supported
- Deprecation notices: Minimum 90 days before removal

---

# PART III: IMPLEMENTATION PATTERNS

## 17. Required Deployment Patterns

### Pattern 1: Fail Fast with Explicit Error Handling

**Required in all deployment scripts:**
```bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
```

**Rationale:** Prevents cascading failures; provides clear failure points for debugging.

**Anti-Pattern:** ❌ Silent failures that cause cryptic downstream errors.

---

### Pattern 2: Dependency Ordering with Wait Conditions

**Required pattern:**
```bash
# Deploy dependency first
kubectl apply -f certificate.yaml

# Wait for readiness
kubectl wait --for=condition=ready certificate/ai-ops-agent-cert --timeout=120s

# Now safe to deploy dependent
kubectl apply -f deployment.yaml
```

**Rationale:** Prevents race conditions where pods try to mount secrets/configmaps that don't exist yet.

**Anti-Pattern:** ❌ Deploying all resources simultaneously (`kubectl apply -f .`)

---

### Pattern 3: Bottom-Up Architecture (Foundation First)

**Required deployment order:**
```
1. Infrastructure (Kubernetes cluster, networking, storage)
2. Foundation Layer (DNS, PKI/cert-manager, secrets management)
3. Platform Services (monitoring, logging, service mesh)
4. Application Layer (AI agents, business services)
```

**Rationale:** Each layer provides services to the layer above. Building top-down requires constant rework.

**Anti-Pattern:** ❌ Deploying applications first, then retrofitting infrastructure (leads to self-signed certs, manual secrets, DNS issues)

---

### Pattern 4: Defensive Prerequisite Validation

**Required in deployment scripts:**
```bash
# Check dependencies exist before proceeding
if ! kubectl get clusterissuer vault-issuer &>/dev/null; then
    echo "ERROR: cert-manager not deployed. Required dependency missing."
    echo "Action: cd foundation/cert-manager && ./deploy.sh"
    exit 1
fi
```

**Rationale:** Provides actionable error messages instead of cryptic failures.

**Anti-Pattern:** ❌ Assuming dependencies exist; failing with unclear errors.

---

### Pattern 5: FQDN for Cross-Namespace Communication

**Required service reference format:**
```yaml
env:
  - name: VAULT_ADDR
    value: "http://vault.vault.svc.cluster.local:8200"
    #              └─┬──┘ └─┬┘ └─┬┘ └──────┬───────┘
    #            service  ns  type   cluster domain
```

**Rationale:**
- Works reliably across namespaces
- Explicit and unambiguous
- Handled by CoreDNS

**Anti-Pattern:** ❌ Using short names (`http://vault:8200`) that only work within the same namespace.

---

### Pattern 6: Multi-Stage Builds for Reproducibility

**Required Dockerfile structure:**
```dockerfile
# Stage 1: Build dependencies (build-time)
FROM python:3.11-slim AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime (minimal)
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY app/ /app
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "/app/main.py"]
```

**Rationale:** Separates build-time from runtime; smaller images; reproducible builds.

**Anti-Pattern:** ❌ Single-stage builds with build tools in production images.

---

## 18. Security & Certificate Patterns

### Pattern 7: Certificate Automation via cert-manager

**Required pattern:**
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: ai-agent-cert
  namespace: ai-ops
spec:
  secretName: ai-agent-tls
  issuerRef:
    name: vault-issuer
    kind: ClusterIssuer
  dnsNames:
    - ai-agent.ai-ops.svc.cluster.local
  duration: 720h        # 30 days
  renewBefore: 240h     # Renew 10 days before expiry
```

**Rationale:**
- Automatic issuance and renewal
- Centralized PKI management via Vault
- No manual certificate operations

**Anti-Pattern:** ❌ Manual certificate generation and distribution.

---

### Pattern 8: Secrets Injection via CSI Driver

**Required pattern (for Vault):**
```yaml
volumes:
  - name: secrets
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "vault-db-creds"
```

**Rationale:** Secrets never touch etcd; pulled directly from Vault at pod start.

**Anti-Pattern:** ❌ Kubernetes Secrets without external secret management.

---

## 19. CI/CD Enforcement Rules

### 19.1 Rejection Conditions (Pipeline Gates)

**Pipelines MUST reject manifests with:**
- Large or opaque `entrypoint.sh` scripts (>50 lines)
- Mixed build-time and runtime logic
- Missing explicit environment variable declarations
- Lack of idempotency tests for startup routines
- Missing resource quotas
- Missing policy attestation metadata
- Invalid policy hash
- No cost attribution tags

### 19.2 Required Practices (Pipeline Validation)

**Pipelines MUST validate:**
- Language-native startup functions used (not shell wrappers)
- Multi-stage builds employed
- Explicit volume mounts declared
- Idempotency tests pass
- Namespace boundary tests pass
- Governance compliance scan passes (OPA, Kyverno)

**Compliance report format:**
```json
{
  "scan_id": "unique_id",
  "timestamp": "ISO8601",
  "manifest": "path/to/manifest",
  "framework_version": "3.0.0",
  "result": "pass|fail",
  "violations": [
    {
      "rule": "resource_quotas_required",
      "severity": "critical",
      "message": "Resource quotas not declared"
    }
  ],
  "passed_checks": ["list"],
  "score": 95
}
```

### 19.3 Integration Tests

**Required test coverage:**
- Namespace boundary enforcement (cannot access other namespaces)
- Policy compliance (action tiers enforced)
- Resource quota enforcement (cannot exceed limits)
- Idempotency (repeated execution safe)
- Rollback capability (can revert to previous state)

---

## 20. Anti-Patterns to Reject

### 20.1 Code Anti-Patterns

**Reject these in code reviews:**

❌ **Hardcoded credentials**
```python
# BAD
api_key = "sk-abc123xyz"
```

✅ **Correct**
```python
# GOOD
api_key = os.environ["API_KEY"]  # Injected by orchestrator
```

---

❌ **Runtime environment variable generation**
```bash
# BAD: entrypoint.sh
export DATABASE_URL="postgres://..."
```

✅ **Correct**
```yaml
# GOOD: docker-compose.yml
services:
  app:
    environment:
      DATABASE_URL: ${DATABASE_URL}
```

---

❌ **Assuming persistence across sessions**
```python
# BAD
cache = {}
def get_data():
    if "key" in cache:
        return cache["key"]
```

✅ **Correct**
```python
# GOOD
def get_data():
    cache = redis.get("key")  # Explicit external state
    if cache:
        return cache
```

### 20.2 Deployment Anti-Patterns

❌ **Deploying without dependency validation**
```bash
# BAD
kubectl apply -f deployment.yaml
```

✅ **Correct**
```bash
# GOOD
if ! kubectl get secret db-credentials; then
    echo "ERROR: Missing db-credentials secret"
    exit 1
fi
kubectl apply -f deployment.yaml
```

---

❌ **Opaque shell scripts**
```bash
# BAD: 200-line entrypoint.sh with business logic
```

✅ **Correct**
```bash
# GOOD: Minimal entrypoint, logic in app code
#!/bin/bash
set -euo pipefail
# Wait for dependencies
wait-for-it postgres:5432 -t 30
# Start app via language runtime
exec python /app/main.py
```

---

## 21. Workflow Expectations

### Standard Operating Procedure for AI Agents

**Phase 1: Inspection**
1. Identify current environment and context
2. List relevant resources in namespace
3. Verify namespace identity and scope
4. Check current resource consumption vs quotas

**Phase 2: Planning**
5. Propose safe, read-only actions first
6. Classify intended actions by tier (0-3)
7. Identify dependencies and prerequisites
8. Assess blast radius and risk

**Phase 3: Validation**
9. Run simulation/dry-run for Tier 2+ actions
10. Validate idempotency of operations
11. Confirm rollback procedure exists
12. Check policy compliance

**Phase 4: Execution (Tier 0/1)**
13. Execute auto-approved actions
14. Log every step with structured JSON
15. Tag resources with cost attribution
16. Monitor for errors or drift

**Phase 4-Alt: Escalation (Tier 2/3)**
13. Generate structured escalation report
14. Route to appropriate approval channel
15. Wait for human decision (with SLA timeout)
16. If approved → execute with logging
17. If denied → log denial, inform user

**Phase 5: Audit & Cleanup**
18. Verify expected outcome achieved
19. Log final state and outcome
20. Clean up temporary resources
21. Update cost attribution records

**Phase 6: Rollback (on failure)**
22. Detect failure condition
23. Execute rollback procedure
24. Verify system restored to safe state
25. Escalate with failure context

---

# PART IV: MACHINE-READABLE POLICIES

## 22. Agent Manifest Schema (YAML)

```yaml
# ai-agent-manifest.yaml
apiVersion: governance.ai/v3
kind: AgentManifest

metadata:
  name: example-ai-agent
  namespace: team-alpha
  labels:
    cost_center: "CC-1234"
    project_code: "PROJ-5678"
    environment: production

spec:
  # Policy Attestation
  compliance:
    framework_version: "3.0.0"
    policy_id: "unified-governance-v3"
    policy_hash: "sha256:abcdef1234567890..."
    last_validated: "2025-11-21T12:00:00Z"

  # Identity & Purpose
  identity:
    agent_identity: "team-alpha-agent-001"
    purpose: "Automate deployment pipeline for web services"
    owner: "team-alpha@example.com"
    on_call: "https://oncall.example.com/team-alpha"

  # Autonomy Target
  autonomy:
    target_auto_approval_rate: 0.85  # 85%
    measurement_window_days: 7
    alert_threshold: 0.75

  # Resource Quotas
  resource_quotas:
    compute:
      cpu_cores: 4
      memory_gb: 16
      gpu_count: 0
    storage:
      persistent_gb: 100
      ephemeral_gb: 50
    network:
      egress_gb_per_month: 1000
    api_calls:
      llm_calls_per_hour: 100
      external_api_calls_per_day: 10000

  # Budget
  budget:
    monthly_limit_usd: 500.00
    alert_at_percent: 80
    block_at_percent: 100
    overage_approval_tier: 2

  # Declared Privileges
  privileges:
    namespaces:
      - team-alpha
    operations:
      - read:pods
      - create:pods
      - delete:pods
      - read:secrets/db-credentials
      - read:configmaps
    external_apis:
      - "https://api.github.com"
      - "https://api.openai.com"

  # Action Tier Overrides (optional)
  action_overrides:
    - pattern: "kubectl delete pod .*"
      default_tier: 1
      override_tier: 0  # Auto-approve pod deletion in this namespace
      justification: "Routine cleanup operation"

  # Escalation Routing
  escalation:
    budget_issues:
      - slack_channel: "#team-alpha-alerts"
      - email: "team-alpha-leads@example.com"
    security_issues:
      - slack_channel: "#security-ops"
      - pagerduty: "P5SECURITY"
    operational_issues:
      - slack_channel: "#team-alpha-oncall"
      - pagerduty: "P5ALPHA"

  # Audit Configuration
  audit:
    log_level: "info"  # debug|info|warn|error
    retention_days: 365
    sensitive_fields_to_mask:
      - "password"
      - "api_key"
      - "secret"
      - "token"
```

---

## 23. Action Tier Decision Matrix (JSON)

```json
{
  "action_tier_rules": {
    "version": "3.0.0",
    "default_tier": 2,
    "rules": [
      {
        "rule_id": "read-own-namespace",
        "tier": 0,
        "pattern": "^(get|list|describe) .* --namespace=%namespace%$",
        "description": "Read operations in own namespace",
        "examples": ["kubectl get pods --namespace=team-alpha"]
      },
      {
        "rule_id": "write-own-workspace",
        "tier": 1,
        "pattern": "^(create|apply|patch) .* --namespace=%namespace%$",
        "conditions": [
          "resource_quota_check:pass",
          "cost_attribution_tags:present"
        ],
        "description": "Write operations in own namespace within quota",
        "examples": ["kubectl apply -f deployment.yaml --namespace=team-alpha"]
      },
      {
        "rule_id": "delete-pods",
        "tier": 1,
        "pattern": "^kubectl delete pod .* --namespace=%namespace%$",
        "conditions": [
          "blast_radius:<=5_pods"
        ],
        "description": "Delete up to 5 pods in own namespace",
        "examples": ["kubectl delete pod myapp-abc123 --namespace=team-alpha"]
      },
      {
        "rule_id": "scale-within-quota",
        "tier": 1,
        "pattern": "^kubectl scale .* --replicas=([0-9]+) --namespace=%namespace%$",
        "conditions": [
          "resource_quota_check:pass",
          "replicas:<=10"
        ],
        "description": "Scale up to 10 replicas within quota"
      },
      {
        "rule_id": "budget-overage",
        "tier": 2,
        "pattern": ".*",
        "conditions": [
          "budget_remaining:<0"
        ],
        "description": "Any action when budget exceeded",
        "approval_routing": "finops_team"
      },
      {
        "rule_id": "cross-namespace-read",
        "tier": 2,
        "pattern": "^(get|list|describe) .* --namespace=(?!%namespace%).*$",
        "description": "Read operations in other namespaces",
        "approval_routing": "namespace_owner"
      },
      {
        "rule_id": "privilege-escalation",
        "tier": 2,
        "pattern": ".*(sudo|su -|chmod \\+s).*",
        "description": "Privilege escalation attempts",
        "approval_routing": "security_team"
      },
      {
        "rule_id": "production-data-delete",
        "tier": 2,
        "pattern": "^(delete|drop|truncate) .* (database|table|collection).*",
        "conditions": [
          "environment:production"
        ],
        "description": "Delete production data",
        "approval_routing": "data_owner",
        "requires_simulation": true
      },
      {
        "rule_id": "credential-exposure",
        "tier": 3,
        "pattern": ".*(echo|cat|print).*(password|api_key|secret|token).*",
        "description": "Attempting to expose credentials",
        "action": "deny"
      },
      {
        "rule_id": "audit-log-modification",
        "tier": 3,
        "pattern": ".*(rm|delete|truncate|modify).*(audit|log).*",
        "description": "Attempting to modify audit logs",
        "action": "deny"
      },
      {
        "rule_id": "policy-bypass",
        "tier": 3,
        "pattern": ".*(skip|bypass|disable).*(policy|governance|validation).*",
        "description": "Attempting to bypass governance",
        "action": "deny"
      },
      {
        "rule_id": "root-deletion",
        "tier": 3,
        "pattern": "^rm -rf /.*",
        "description": "Root filesystem deletion",
        "action": "deny"
      }
    ]
  },
  "condition_evaluators": {
    "resource_quota_check": "Check current consumption vs declared quotas",
    "cost_attribution_tags": "Verify required tags present on resources",
    "blast_radius": "Estimate number of affected resources",
    "budget_remaining": "Current budget remaining",
    "environment": "dev|staging|production from manifest"
  }
}
```

---

## 24. Auto-Approval Rules (OPA Policy)

```rego
# policy/governance-v3.rego
package governance.v3

import future.keywords

# Default deny
default allow = false
default tier = 2

# Helper: Extract namespace from agent identity
agent_namespace := split(input.agent_identity, "-")[0]

# Tier 0: Read operations in own namespace
allow {
    tier == 0
}

tier := 0 {
    input.operation in ["get", "list", "describe", "read"]
    input.namespace == agent_namespace
}

# Tier 1: Write operations in own namespace within quota
tier := 1 {
    input.operation in ["create", "apply", "patch", "update", "write"]
    input.namespace == agent_namespace
    quota_check_pass
    cost_tags_present
}

tier := 1 {
    input.operation == "delete"
    input.resource_type == "pod"
    input.namespace == agent_namespace
    count(input.affected_resources) <= 5
}

tier := 1 {
    input.operation == "scale"
    input.namespace == agent_namespace
    input.target_replicas <= 10
    quota_check_pass
}

# Tier 1: Auto-approve if within quota and has tags
allow {
    tier == 1
}

# Tier 2: Budget overage
tier := 2 {
    input.budget_remaining_usd < 0
}

# Tier 2: Cross-namespace operations
tier := 2 {
    input.namespace != agent_namespace
}

# Tier 2: Privilege escalation
tier := 2 {
    regex.match(".*(sudo|su -|chmod \\+s).*", input.command)
}

# Tier 2: Production data deletion
tier := 2 {
    input.operation in ["delete", "drop", "truncate"]
    input.resource_type in ["database", "table", "collection"]
    input.environment == "production"
}

# Tier 3: Always deny
tier := 3 {
    credential_exposure_attempt
}

tier := 3 {
    audit_log_modification_attempt
}

tier := 3 {
    policy_bypass_attempt
}

tier := 3 {
    regex.match("^rm -rf /.*", input.command)
}

# Helper functions
quota_check_pass {
    input.current_cpu_usage < input.declared_cpu_quota
    input.current_memory_usage < input.declared_memory_quota
}

cost_tags_present {
    input.resource_tags.cost_center
    input.resource_tags.project_code
    input.resource_tags.agent_identity
}

credential_exposure_attempt {
    regex.match(".*(echo|cat|print).*(password|api_key|secret|token).*", input.command)
}

audit_log_modification_attempt {
    regex.match(".*(rm|delete|truncate|modify).*(audit|log).*", input.command)
}

policy_bypass_attempt {
    regex.match(".*(skip|bypass|disable).*(policy|governance|validation).*", input.command)
}

# Approval routing
approval_channel := "finops_team" {
    tier == 2
    input.budget_remaining_usd < 0
}

approval_channel := "security_team" {
    tier == 2
    regex.match(".*(sudo|su -).*", input.command)
}

approval_channel := "namespace_owner" {
    tier == 2
    input.namespace != agent_namespace
}

approval_channel := "data_owner" {
    tier == 2
    input.operation in ["delete", "drop", "truncate"]
    input.environment == "production"
}
```

---

## 25. Escalation Routing Configuration (YAML)

```yaml
# escalation-routing-config.yaml
apiVersion: governance.ai/v3
kind: EscalationConfig

metadata:
  name: default-escalation-routing

spec:
  routing_rules:
    - name: budget-overage
      condition:
        tier: 2
        trigger: budget_remaining < 0
      destinations:
        - type: slack
          channel: "#finops-alerts"
          message_template: |
            🚨 Budget Overage Alert
            Agent: {{.agent_identity}}
            Namespace: {{.namespace}}
            Budget Remaining: ${{.budget_remaining}}
            Action: {{.intended_action}}
            Approval Required: {{.approval_url}}
        - type: email
          recipients:
            - finops-team@example.com
            - "{{.budget_owner}}"
          subject: "Budget Approval Required: {{.agent_identity}}"
        - type: servicenow
          assignment_group: "FinOps"
          priority: 3
          category: "Budget Management"
      sla:
        response_time_hours: 4
        escalate_to: "finops-manager@example.com"
        escalate_after_hours: 6

    - name: security-escalation
      condition:
        tier: 2
        trigger: security_concern == true
      destinations:
        - type: slack
          channel: "#security-ops"
          mention: "@security-oncall"
          message_template: |
            🔒 Security Escalation
            Agent: {{.agent_identity}}
            Concern: {{.security_concern_description}}
            Command: `{{.command}}`
            Risk: {{.risk_level}}
            Approval: {{.approval_url}}
        - type: pagerduty
          service_key: "P5SECURITY"
          severity: "warning"
          dedup_key: "{{.agent_identity}}-{{.timestamp}}"
      sla:
        response_time_hours: 2
        escalate_to: "security-manager@example.com"
        escalate_after_hours: 4

    - name: cross-namespace-request
      condition:
        tier: 2
        trigger: target_namespace != agent_namespace
      destinations:
        - type: slack
          channel: "#namespace-{{.target_namespace}}"
          message_template: |
            📬 Cross-Namespace Access Request
            Requesting Agent: {{.agent_identity}}
            Target Namespace: {{.target_namespace}}
            Operation: {{.operation}}
            Justification: {{.justification}}
            Approval: {{.approval_url}}
        - type: email
          recipients:
            - "{{.target_namespace_owner}}"
            - governance-team@example.com
      sla:
        response_time_hours: 4

    - name: production-data-deletion
      condition:
        tier: 2
        trigger: operation in [delete, drop, truncate] AND environment == production
      destinations:
        - type: slack
          channel: "#data-ops"
          mention: "@data-oncall"
          message_template: |
            ⚠️ PRODUCTION DATA DELETION REQUEST
            Agent: {{.agent_identity}}
            Operation: {{.operation}}
            Affected Resources: {{.affected_resources}}
            Blast Radius: {{.blast_radius_estimate}}
            Rollback Plan: {{.rollback_procedure}}
            **SIMULATION REQUIRED**
            Approval: {{.approval_url}}
        - type: servicenow
          assignment_group: "Data Operations"
          priority: 2
          category: "Data Management"
      sla:
        response_time_hours: 8
        requires_simulation: true

    - name: tier-3-denial
      condition:
        tier: 3
      destinations:
        - type: slack
          channel: "#governance-incidents"
          message_template: |
            🛑 POLICY VIOLATION - Action Denied
            Agent: {{.agent_identity}}
            Attempted Action: {{.command}}
            Violation: {{.violation_description}}
            Incident ID: {{.incident_id}}
        - type: servicenow
          assignment_group: "Governance"
          priority: 1
          category: "Policy Violation"
      action: deny_and_log

  default_routing:
    destinations:
      - type: slack
        channel: "#governance-general"
      - type: email
        recipients:
          - governance-team@example.com
    sla:
      response_time_hours: 24

  timeout_behavior:
    tier_2: "auto_deny"  # Never auto-approve on timeout
    tier_3: "deny"

  notification_preferences:
    aggregate_similar_requests: true
    aggregation_window_minutes: 10
    max_notifications_per_hour: 50
```

---

# PART V: AUTONOMY OPTIMIZATION

## 26. Metrics & Monitoring for 80% Target

### 26.1 Key Performance Indicators (KPIs)

**Primary Metric: Autonomy Rate**
```
autonomy_rate = (tier_0_actions + tier_1_actions) / total_actions
```
- **Target:** ≥80%
- **Measurement window:** Rolling 7 days
- **Alert threshold:** <75% for 3 consecutive days
- **Critical threshold:** <70% for 7 consecutive days → Mandatory redesign

**Secondary Metrics:**
- `tier_2_escalation_rate = tier_2_actions / total_actions`
  - Target: <15%
- `tier_3_denial_rate = tier_3_actions / total_actions`
  - Target: <5%
- `approval_wait_time_p50` (median time waiting for human approval)
  - Target: <2 hours
- `approval_wait_time_p95`
  - Target: <6 hours
- `escalation_timeout_rate = timeouts / tier_2_actions`
  - Target: <2%

### 26.2 Monitoring Dashboard

**Required dashboard panels:**

1. **Autonomy Rate Trend**
   - 7-day rolling average
   - Per-agent breakdown
   - Color-coded: Green (>80%), Yellow (75-80%), Red (<75%)

2. **Action Distribution by Tier**
   - Stacked bar chart: Tier 0/1/2/3 counts
   - Daily granularity
   - Compare to target distribution

3. **Top Escalation Triggers**
   - List of most common Tier 2 escalation reasons
   - Count and percentage of total
   - Identify optimization opportunities

4. **Approval Wait Time Heatmap**
   - Hour of day vs day of week
   - Identify staffing gaps

5. **Cost Efficiency**
   - Cost per autonomous action vs escalated action
   - Human time spent on approvals (estimated)

6. **Agent Health Score**
   - Combined metric: `(autonomy_rate * 0.5) + (1 - escalation_rate) * 0.3 + (1 - denial_rate) * 0.2`
   - Target: >85%

### 26.3 Alerting Rules

**Critical Alerts:**
- Autonomy rate <70% for 7 days
- Tier 3 denial rate >10%
- >100 Tier 2 escalations per agent per day

**Warning Alerts:**
- Autonomy rate <75% for 3 days
- Approval wait time p95 >8 hours
- Same escalation reason >20 times per week (optimization opportunity)

**Info Alerts:**
- Autonomy rate improvement >5% week-over-week
- New escalation pattern detected

---

## 27. Common Escalation Triggers to Eliminate

### 27.1 Analysis Process

**Monthly review:**
1. Query Decision Ledger for all Tier 2 escalations in past 30 days
2. Group by escalation reason/pattern
3. Identify top 10 most frequent triggers
4. For each trigger, determine:
   - Is it safe to auto-approve with additional guardrails?
   - Can resource quotas be adjusted to accommodate?
   - Is pattern legitimately high-risk or false positive?

### 27.2 Common Patterns to Address

**Pattern 1: Temporary budget spike during deployments**
- **Problem:** Deployment causes brief spike above daily budget
- **Solution:** Allow 20% budget buffer for 1-hour windows, auto-approve if returns to normal
- **Implementation:** Add condition to action tier rules

**Pattern 2: Cross-namespace read for monitoring**
- **Problem:** Agents need to read metrics from other namespaces for dashboards
- **Solution:** Pre-authorize specific read-only cross-namespace patterns
- **Implementation:** Add to privilege declarations in manifest

**Pattern 3: Scaling beyond static quota during traffic surge**
- **Problem:** Legitimate traffic surge requires temporarily exceeding quota
- **Solution:** Dynamic quota based on observed load patterns
- **Implementation:** Policy Engine with time-series analysis

**Pattern 4: First-time resource creation**
- **Problem:** Creating new resource types triggers escalation due to unfamiliarity
- **Solution:** Simulation mode + auto-approval after successful dry-run
- **Implementation:** Two-phase deployment pattern

**Pattern 5: Weekend/off-hours operations**
- **Problem:** Escalations timing out due to no approvers online
- **Solution:** Pre-approved maintenance windows or follow-the-sun approval routing
- **Implementation:** Time-based policy overrides

### 27.3 Optimization Workflow

```
For each common escalation pattern:
1. Assess risk level (low/medium/high)
2. If low risk:
   - Draft auto-approval rule with guardrails
   - Test in staging for 14 days
   - Monitor false positive rate
   - If <1% false positive → promote to production
3. If medium risk:
   - Implement enhanced monitoring
   - Require simulation mode
   - Allow auto-approval with stricter conditions
4. If high risk:
   - Keep Tier 2, but optimize approval routing
   - Reduce SLA response time
   - Provide better context in escalation

Document rationale in Decision Ledger
```

---

## 28. Continuous Improvement Process

### 28.1 Quarterly Governance Review

**Agenda:**
1. Autonomy rate achievement across all agents
2. Top 10 escalation patterns analysis
3. Policy effectiveness review
4. Cost efficiency metrics
5. Security incident correlation
6. Agent redesign recommendations

**Outputs:**
- Policy updates (version bump if needed)
- Manifest template improvements
- Training for agent developers
- Budget/quota adjustments

### 28.2 Agent Lifecycle Feedback Loop

**Per-agent review (monthly):**
```
1. Generate agent report card:
   - Autonomy rate trend
   - Escalation breakdown
   - Cost efficiency
   - Policy compliance score
   - Incidents/violations

2. If autonomy <80%:
   - Root cause analysis
   - Identify top 3 escalation triggers
   - Propose mitigations

3. If violations >0:
   - Incident review
   - Determine if policy gap or agent defect
   - Remediation plan

4. Best practices:
   - Agents >90% autonomy → Case study
   - Share patterns with other teams
```

### 28.3 Policy Evolution

**Version management:**
- Minor version (3.x): Add rules, clarify language, fix bugs
- Major version (x.0): Breaking changes, architecture changes

**Deprecation process:**
1. Announce deprecated feature (Governance blog/Slack)
2. 90-day grace period (both old and new supported)
3. Warning phase: Agents get warnings using deprecated features
4. Enforcement: Old policy no longer accepted

---

## 29. Real-World Scenarios & Decision Trees

### Scenario 1: Agent Wants to Delete 100 Old Log Files

**Decision tree:**
```
Q: What tier is file deletion?
A: Depends on context and scope

Q: Are files in agent's own namespace directory?
A: Yes → Continue

Q: Are files >30 days old and non-critical?
A: Yes → Continue

Q: Is total size <1GB?
A: Yes → Tier 1 (auto-approve with audit)
A: No → Tier 2 (human approval due to large blast radius)

Q: Are files in production data directory?
A: Yes → Tier 2 (human approval required)
```

**Action:** Auto-approve if Tier 1 conditions met; escalate otherwise.

---

### Scenario 2: Agent Needs to Scale Deployment from 3 to 15 Replicas

**Decision tree:**
```
Q: Is this within resource quota?
A: Check declared CPU/memory quota

Q: Current usage: 12 cores / 16 cores quota
   New usage would be: 20 cores
A: No, exceeds quota → Tier 2 (budget owner approval)

Q: Is this a response to legitimate traffic surge?
A: Check observability data for traffic increase

Q: Traffic increased 400% in last 10 minutes (alert threshold: 200%)
A: Yes → Pre-authorized pattern → Tier 1 with temporary quota override

Action: Auto-approve with temporary quota increase; flag for post-incident review
```

---

### Scenario 3: Agent Receives Request to Access Another Namespace

**Decision tree:**
```
Q: Is target namespace explicitly listed in agent manifest privileges?
A: No → Tier 2 (cross-namespace approval required)

Q: Is this a read-only operation?
A: Yes → Route to namespace owner for approval

Q: Is this a write/modify operation?
A: Yes → Route to namespace owner + governance team for approval

Escalation includes:
- Source agent identity
- Target namespace
- Requested operation
- Justification
- Duration (temporary access request?)
```

**Action:** Escalate with full context; wait for approval (4-hour SLA).

---

### Scenario 4: Agent Detects Configuration Drift

**Decision tree:**
```
Q: What is the nature of drift?
A: Actual state differs from declared state in manifest

Q: Is drifted resource in agent's own namespace?
A: Yes → Continue

Q: Is drift in Tier 0 resource (e.g., ConfigMap)?
A: Yes → Auto-remediate (Tier 1: reapply manifest)

Q: Is drift in Tier 2 resource (e.g., production database schema)?
A: Yes → Escalate for human review (potential incident)

Q: Can drift be safely auto-remediated?
A: Run simulation/dry-run of remediation
A: If simulation succeeds and blast radius <5 resources → Auto-remediate (Tier 1)
A: Otherwise → Escalate (Tier 2)
```

**Action:** Auto-remediate Tier 1 drift; escalate Tier 2 with simulation results.

---

## 30. Success Criteria & Graduation

### 30.1 Agent Maturity Levels

**Level 1: Initial (Not Production-Ready)**
- Autonomy rate: 0-60%
- Frequent manual interventions
- High escalation rate

**Level 2: Developing**
- Autonomy rate: 60-75%
- Some manual interventions
- Moderate escalation rate
- Ready for staging

**Level 3: Mature (Production-Ready)**
- Autonomy rate: 75-85%
- Infrequent manual interventions
- Low escalation rate
- Can operate in production with human oversight

**Level 4: Advanced (Fully Autonomous)**
- Autonomy rate: >85%
- Rare manual interventions
- Very low escalation rate
- Operates in production with minimal oversight

**Level 5: Optimized**
- Autonomy rate: >90%
- Self-optimizing
- Predictive escalation (escalates before issues occur)
- Reference implementation for other agents

### 30.2 Graduation Requirements

**To promote agent to production:**
- Minimum 14 days in staging at Level 3
- Zero Tier 3 violations in staging
- Autonomy rate ≥80% in staging
- All CI/CD gates passing
- Security review completed
- Incident runbook documented
- On-call team trained

**To declare agent "fully autonomous":**
- 90 days in production at Level 4
- Autonomy rate ≥90% sustained
- Zero critical incidents caused
- Positive cost/benefit analysis
- Case study documented

---

## 31. Governance Authority & Contacts

### 31.1 Governance Team

**Role:** Maintain this framework, approve exceptions, investigate violations

**Contacts:**
- Email: `governance-team@%domain%`
- Slack: `#ai-governance`
- On-call: PagerDuty → `P5GOVERNANCE`

### 31.2 Exception Request Process

**For time-bound exceptions to this framework:**
1. Submit request via: `https://governance.%domain%/exception-request`
2. Required information:
   - Agent identity
   - Policy section requiring exception
   - Business justification
   - Risk mitigation plan
   - Requested duration (max 90 days)
   - Approvers: Governance + Security + affected team leads
3. Decision SLA: 5 business days
4. If approved:
   - Exception logged in Decision Ledger
   - Expiration date set
   - Automatic revocation at expiration

### 31.3 Policy Feedback

**To propose changes to this framework:**
- Open issue: `https://github.com/%org%/governance-framework/issues`
- Tag: `policy-change-request`
- Include:
  - Current policy gap or issue
  - Proposed change
  - Impact analysis
  - Implementation plan

**Review cadence:** Monthly triage, quarterly major updates

---

## 32. Document Control

### 32.1 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 3.0.0 | 2025-11-21 | Unified strategic + tactical frameworks; added machine-readable policies | Governance Team |
| 2.1.0 | 2025-11-20 | Strategic framework with 6 components | Governance Team |
| 2.0.0 | 2025-11-21 | Tactical guardrails with Day 7 patterns | Operations Team |

### 32.2 Approval

**Approved by:**
- Chief Information Security Officer (CISO)
- Chief Technology Officer (CTO)
- VP Engineering
- VP Finance (for cost attribution sections)
- Legal/Compliance (for audit retention sections)

**Next review:** 2025-05-21 (6 months)

### 32.3 Related Documents

- `agent-manifest-template.yaml` (reference implementation)
- `policy-engine-rules.rego` (OPA policies)
- `ci-cd-governance-gates.yaml` (pipeline validation)
- `incident-runbook.md` (governance violation response)
- `agent-developer-guide.md` (how to build compliant agents)

---

## Appendix A: Glossary

- **Action Tier:** Classification (0-3) of operations based on risk and approval requirements
- **Agent Manifest:** Declarative YAML document describing agent identity, quotas, privileges
- **Attestation:** Cryptographic proof of identity and policy compliance
- **Autonomy Rate:** Percentage of actions auto-approved without human intervention
- **Blast Radius:** Estimated scope of impact from an operation
- **Cost Attribution:** Automatic tagging of resource consumption to agent identity
- **Decision Ledger:** Immutable audit log of all governance events
- **Declarative Configuration:** Version-controlled manifests as single source of truth
- **Drift:** Divergence between declared state and actual state
- **Escalation:** Routing of Tier 2 actions to human approvers
- **Identity Issuer:** Component that issues cryptographic identities to agents
- **Idempotency:** Property where repeated execution produces same result
- **Least Privilege:** Minimum necessary permissions for required function
- **Namespace:** Logical isolation boundary for agent operations
- **Policy Engine:** Decision point for authorization and action tiering
- **Reconciliation Controller:** Component that detects and remediates drift
- **Simulation/Dry-Run:** Non-destructive preview of operation effects
- **Zero Trust:** Security model requiring authentication/authorization per request

---

## Appendix B: Quick Reference Card

**For AI Agents: Pre-Flight Checklist**

Before taking any action:
- [ ] Is my namespace identity valid and verified?
- [ ] Is the target resource in my namespace?
- [ ] Have I inspected current state (read-only first)?
- [ ] What is the action tier for this operation?
  - Tier 0/1 → Proceed
  - Tier 2 → Escalate with context
  - Tier 3 → Denied, log and inform
- [ ] If destructive:
  - [ ] Can I list exact resources affected?
  - [ ] Is there a rollback plan?
  - [ ] Is this idempotent?
  - [ ] Have I run simulation first?
- [ ] Are resource quotas sufficient?
- [ ] Will this operation stay within budget?
- [ ] Am I logging this action with all required fields?
- [ ] Are secrets masked in all outputs?

**When in doubt:** Escalate with full context. Never assume.

---

**END OF UNIFIED AI AGENT GOVERNANCE FRAMEWORK v3.0**

*This document is the single source of truth for AI agent governance.*
*All agents must comply. No exceptions without written approval.*
*Questions? Contact governance-team@%domain%*
