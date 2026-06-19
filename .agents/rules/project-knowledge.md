---
trigger: always_on
---

# Project Knowledge Base — Architecture & Key Decisions

## Source File Map

| Path | Purpose |
|------|---------|
| `app/main.py` | GPIS FastAPI PDP — the single policy decision point |
| `app/policy_engine.py` | Policy evaluation logic (3 categories, needs expansion to 5) |
| `scripts/governance_router.py` | Token-efficient router template (LLM clients NOT yet wired) |
| `scripts/otel-siem-emitter.py` | OpenTelemetry SIEM event emitter (OCSF-compliant) |
| `scripts/validate-jira-approval.py` | PKI signature verification for Tier 3/4 CRs |
| `scripts/benchmark_token_savings.py` | Token efficiency benchmark (validates 70%+ target) |
| `scripts/compliance-check-enhanced.sh` | 12 AWS compliance checks with SIEM integration |
| `scripts/prompts/cache_classifier.txt` | Small model prompt: cache HIT/MISS routing (~100 tokens) |
| `scripts/prompts/intent_router.txt` | Small model prompt: 5-category intent routing (~200 tokens) |
| `scripts/prompts/distillation.txt` | Large model prompt: pattern → simple rule distillation |
| `policies/simple_rules.yml` | YAML lookup table for zero-token governance decisions |
| `policies/schemas/audit-trail.json` | ⭐ PATENT ANCHOR — Atomic Governance Transaction schema |
| `policies/schemas/siem-event.json` | SIEM event schema (OCSF mapping) |
| `policies/schemas/agent-cost-record.json` | Cost tracking schema |
| `agents/security/src/handlers/api_server.py` | Security Agent FastAPI server |
| `agents/it-ops/src/handlers/api_server.py` | IT-Ops Agent FastAPI server |
| `agents/ai/src/handlers/training_job.py` | AI Agent ML training CronJob |
| `agents/architect/src/handlers/api_server.py` | Architect Agent FastAPI server |
| `deploy/helm/ai-agent/` | Helm chart for all 4 agent types |
| `terraform/modules/` | AWS IaC: secrets_manager, cloudtrail, kms, s3_audit_logs |
| `compliance/ssp/control-implementation.md` | NIST 800-53 Rev 5 (88% complete, 298/339 controls) |
| `docs/US-PATENT-APPLICATION.md` | ⭐ Full USPTO patent application draft |
| `docs/PATENT-DISCLOSURE.md` | ⭐ Technical specification for AGT system |
| `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md` | Full token router implementation guide |
| `docs/GOVERNANCE-AGENT-ARCHITECTURE.md` | MCP-based AI governance agent architecture |
| `GOVERNANCE_GUARDRAILS.md` | The 16 active guardrail rules |
| `NEXT_RELEASE_TODO.md` | ⭐ Current backlog and session log |
| `LESSONS_LEARNED.md` | ⭐ Root cause playbooks — READ BEFORE DEBUGGING |

## Architecture Decisions (Do Not Reverse)

### Decision 1: GPIS as Universal PDP
All agent authorization flows through the single GPIS FastAPI endpoint. Agents do not implement their own authorization logic. This is required by the patent claims.

### Decision 2: JWT-Based Authorization Tokens
GPIS issues short-lived signed JWTs as "permission slips" that agents attach to downstream service calls. The token TTL is tier-dependent (Tier 1: 15min → Tier 4: 2min).

### Decision 3: Audit Trail = Append-Only + Schema-Validated
The `audit-trail.json` schema is immutable (patent anchor). Every governance decision emits one validated entry before execution, and one after. This supports FedRAMP AU family controls.

### Decision 4: Token Router Hierarchy is Ordered
The GovernanceRouter evaluates in strict order: Cache → Intent Router → Simple Rules → Large Model. Skipping levels breaks the token efficiency guarantee and must not be done.

### Decision 5: Simple Rules Are the Core IP
The `policies/simple_rules.yml` file represents distilled governance intelligence. High-confidence large model decisions are distilled into rules to eliminate repeat LLM calls. This is the mechanism that achieves 90% token savings.

### Decision 6: Monorepo with Helm Chart Variants
All 4 agents share a single Helm chart with agent-specific `values-<type>.yaml` overlays. New agents must use the shared chart, not custom charts.

## Key Numbers to Know
- **Compliance**: 298/339 NIST 800-53 controls (88%) — target 100% for FedRAMP
- **Token savings target**: 90.25% reduction (195 tokens/req vs 2000 baseline)
- **Agent tiers**: 4 (Observer, Developer, Operations, Architect)
- **Guardrail rules**: 16 active (see `GOVERNANCE_GUARDRAILS.md`)
- **Risk catalog**: 18 AI-specific risks
- **Mitigation controls**: 21 implementation-ready controls
- **SIEM test suite**: 10/10 must pass (`./scripts/test-siem-emitter.sh`)
- **Agent monthly costs**: Security $150, IT-Ops $300, AI $800, Architect $350

## Known Issues (From Code Review June 19, 2026)
1. **LL-001**: `app/main.py` line 11 has hardcoded JWT secret → P0 fix required
2. **LL-002**: `evaluate_security()` CVE > 9.0 → APPROVED logic is ambiguous
3. **LL-003**: GovernanceRouter LLM clients are mock stubs — not wired
4. **LL-004**: Agent manifests have no schema validation
5. **K8S-002**: NetworkPolicy resources missing from Helm chart
6. **GPIS-004**: No `/health` or `/ready` endpoints on GPIS

## Integration Points
- **Jira**: PKI-signed CRs via `validate-jira-approval.py` (required for Tier 3/4)
- **Splunk/Datadog/CloudWatch**: OTLP exporter in `otel-siem-emitter.py`
- **AWS Secrets Manager**: Terraform module in `terraform/modules/secrets_manager/`
- **Prometheus + Grafana**: Monitoring stack in `deploy/helm/` (metrics not yet instrumented in agents)
- **GitHub Actions**: CI workflows in `.github/workflows/` (missing Trivy, pip-audit, SBOM)

---

## GitHub Security & Quality Gates

The project targets FedRAMP Moderate and uses a combination of automated scanning tools to satisfy NIST 800-53 controls:

| Feature | Coverage | NIST Control | Status | Tools / Implementation |
|---------|----------|--------------|--------|------------------------|
| **Dependabot** | Weekly dependency check | RA-5, SI-2 | Planned | `.github/dependabot.yml` weekly check |
| **CodeQL** | Python static application security testing (SAST) | SA-11, SI-3 | Planned | GitHub Actions CodeQL analysis |
| **Secret Scanning** | Push protection for credentials | IA-5, SC-28 | Planned | GitHub Repository Advanced Security |
| **TruffleHog** | Pre-push and local secret scanning | IA-5 | Active | Local run and CI scan for secrets |
| **pip-audit** | Dependency vulnerability scanner | RA-5 | Active | Scans `requirements.txt` for known CVEs |
| **Trivy** | Container image vulnerability scanner | RA-5, SI-3 | Planned | Scan agent images in CI/CD before push |
| **SBOM (Syft)** | Software Bill of Materials generation | SR-3, SR-4 | Planned | Syft CycloneDX JSON artifact in release |

---

## PPSM Reference Registry (L4/L7)

Below is the Ports, Protocols, and Services Management (PPSM) profile baseline (DISA CAL standard) mapped to the framework namespaces:

### Egress Tiers & Network Policy
- **T1 (Internal Vault Tier):** Access to database and credentials.
  - Redis (`:6379`, TCP) - Short-term memory & HITL state
  - Chroma VectorDB (`:8002`, HTTP) - Long-term semantic memory
  - CyberArk Conjur (`:443`, mTLS HTTPS) - Secrets broker
- **T2 (Internal Service Tier):** Base infrastructure services.
  - GPIS PDP (`:8000`, HTTPS) - Authorization server
  - K8s API Server (`:6443`, HTTPS) - Orchestrator
  - OTEL SIEM (`:4317`, gRPC) - Observability collector
- **T3 (External LLM Egress):** Restricted LLM communication.
  - LLM Proxy (`:8443`, HTTPS) - GovernanceRouter outbound proxy
  - AWS Bedrock (`:443`, PrivateLink) - Production LLM endpoint
  - Google Vertex AI (`:443`, PSC) - Secondary LLM endpoint

### Known K8s Ports & Services Reference

| Service | Port | Protocol | Default Namespace | Access Constraint |
|---------|------|----------|-------------------|-------------------|
| GPIS (PDP) | 8000 | HTTPS | `ai-agents-prod` / `dev` | Allowed to all agents |
| GPIS Admin (PAP) | 8001 | HTTPS | `ai-agents-prod` / `dev` | Slack bot and webhooks only |
| Agent API Servers | 8080 | HTTPS | `ai-agents-prod` / `dev` | Ingress from GovernanceRouter only |
| Metrics Exporters | 9090 | HTTP | `ai-agents-prod` / `dev` | Scraped by Prometheus only |
| Redis (Memory) | 6379 | TCP | `ai-agents-prod` / `dev` | GovernanceRouter only; agent direct DENY |
| Chroma VectorDB | 8002 | HTTP | `ai-agents-prod` / `dev` | GovernanceRouter only; agent direct DENY |
| Conjur OSS | 443 | HTTPS | `ai-agents-infra` | Sidecar auth client and router only |
| K8s API Server | 6443 | HTTPS | `default` | Restricted via RBAC to agent roles |
| Traefik Ingress | 80/443 | HTTPS | `kube-system` | Ingress allowed to agent HTTP endpoints |

