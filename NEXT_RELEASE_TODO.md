# K8S AI DevSecOps Agent Governance Framework — Next Release Backlog

This list is based on a full code review (June 19, 2026) against the current v2.1 implementation, gap analysis across the GPIS/CMDB/Compliance layers, and token-efficiency lessons learned from the AWS-DFD-Visualizer and this project's own `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md`.

---
## 📍 Session Log

### ✅ Session: August 2, 2026 (Antigravity Goal Execution)
- [x] **SEC-001 (P0)** — Enforced `GPIS_JWT_SECRET` env var in `app/main.py` and test fixtures. Removed hardcoded JWT key.
- [x] **SEC-002 (P0)** — Resolved CVE policy logic ambiguity in `app/policy_engine.py`. Renamed to `evaluate_security_patch_deployment()` requiring `action: emergency_patch` for critical CVE approvals; blocks otherwise.
- [x] **GPIS-003 & GPIS-004 (Epic)** — Added `/health` and `/ready` probes and `/api/v1/verify` token verification endpoint to `app/main.py`. Updated JWT claims payload with tier, namespace, and Jira CR details.
- [x] **K8S-002 (Epic)** — Validated default-deny Kubernetes `NetworkPolicy` template (`deploy/helm/ai-agent/templates/networkpolicy.yaml`).
- [x] **IP Boundary & Zero Trust Architecture** — Created `scripts/export-external-sdk.sh` for safe external SDK bundle export with zero secret findings (112 clean files). Documented ZT architecture & 152 ZTOM controls in `docs/ARCHITECTURE-RECOMMENDATIONS-ZT.md`. Updated `.agents/rules/` and `.agentignore`.

### 🔄 Session: June 19, 2026 (Antigravity Phase 2 Execution - Part 1)
- [/] **Zero Trust & Hardening Execution** — Started executing Phase 2 plan. Bootstrapped namespaces and service accounts (`scripts/identity-bootstrap.sh`), updated `values.yaml` and `serviceaccount.yaml` to enforce `automountServiceAccountToken: false` by default, consolidated `.claude/prompts/` rules to `.agents/rules/`, and updated `README.md` and `CODEMAP.md` indexes.

### ✅ Session: June 19, 2026 (Antigravity Code Review)
- [x] **Full Project Audit & Backlog Creation** — Reviewed all source code, docs, agents, .claude prompts, scripts, Helm charts, Terraform modules, and compliance artifacts. Created this `NEXT_RELEASE_TODO.md`, the `.agents/rules/` directory with 8 structured rule files, and upgraded the `.claude/prompts/` context with token-efficient, IDE-agnostic patterns. Merged the best patterns from AWS-DFD-Visualizer (session log discipline, lessons-learned playbooks, post-goal validation) with this project's governance kernel (GPIS, CMDB, PAR-PROTO, token router). See `LESSONS_LEARNED.md` for root causes.
- [x] **Critical Security Bug Identified: Hardcoded JWT Secret** — `app/main.py` line 11 contains `SECRET_KEY = "suhlabs-super-secret-governance-key"` hardcoded in source. This is a P0 security vulnerability that violates Guardrail #8, NIST IA-5, and any FedRAMP Moderate baseline. Logged in `LESSONS_LEARNED.md` as LL-001.
- [x] **Critical Logic Bug Identified: CVE Score Policy Inversion** — `app/policy_engine.py` `evaluate_security()` comment documents that `CVE score > 9.0 → APPROVED` which is the *inverse* of correct security logic (critical CVE should BLOCK, not approve). The actual intent was likely "APPROVED for emergency patch deployment when score > 9.0". This ambiguity must be resolved and documented. Logged as LL-002.

---

## 🔴 Critical (P0 — Security & Correctness)

### SEC-001: Hardcoded JWT Secret in `app/main.py`
- **Context**: `SECRET_KEY = "suhlabs-super-secret-governance-key"` is committed in plaintext to source control. Any token signed by the GPIS server can be forged by anyone with repository access. This breaks authentication for all Tier 3/4 agent operations.
- **Action**:
  1. Remove the hardcoded secret immediately.
  2. Replace with `os.getenv("GPIS_JWT_SECRET")` with a startup-time assertion that the env var exists.
  3. Add `GPIS_JWT_SECRET` to the Kubernetes `ExternalSecret` manifest in `deploy/helm/ai-agent/`.
  4. Add a `pre-commit` hook using `detect-secrets` or TruffleHog to prevent regression.
  5. Add a `pytest` test asserting no hardcoded secrets exist in `app/`.
- **Guardrails**: #8 (Secrets), #6 (Audit), NIST IA-5, FedRAMP IA-5(1)
- **See also**: [LL-001](LESSONS_LEARNED.md)

### SEC-002: CVE Policy Logic Ambiguity Must Be Resolved
- **Context**: `evaluate_security()` in `app/policy_engine.py` approves requests when `cve_score > 9.0` per its docstring. This is the inverse of standard security posture (critical CVEs should block, not pass). The *intent* appears to be approving emergency remediation pipelines, but the ambiguity means a misconfigured caller could accidentally allow unpatched critical vulnerabilities.
- **Action**:
  1. Rename the function to `evaluate_security_patch_deployment()` to make intent explicit.
  2. Add a `require_action == "emergency_patch"` guard: if the payload does not include `action: emergency_patch`, any CVE > 9.0 returns DENIED.
  3. Add integration tests for both the patch-approval and block-on-unpatched paths.
  4. Document the rule in `policies/agent-safety-policies.md` under "Security Policy Category Rules."
- **See also**: [LL-002](LESSONS_LEARNED.md)

### SEC-003: FastAPI Missing Input Validation & Rate Limiting
- **Context**: `app/main.py` `POST /api/v1/authorize` has no input length limits, no rate limiting, and no request authentication (any caller can hit the PDP endpoint). A malicious agent could flood requests or inject oversized payloads.
- **Action**:
  1. Add Pydantic field validators: `agent_id` max 64 chars, alphanumeric+hyphen only. `payload` max 2KB.
  2. Add `slowapi` rate limiter: 100 req/min per IP, 10 req/min per `agent_id`.
  3. Add mTLS or API key header validation as a prerequisite to PDP evaluation.
  4. Write Pytest integration tests for oversized payloads and rate-limit breach.

### SEC-005: Ephemeral Credential Lifecycle (CyberArk Conjur Sidecar)
- **Context**: Static K8s secrets are a major security risk. Agents must fetch short-lived ephemeral tokens from CyberArk Conjur via a sidecar pattern based on Projected ServiceAccount tokens.
- **Action**:
  1. Create `deploy/helm/ai-agent/templates/conjur-sidecar.yaml`.
  2. Implement `_fetch_ephemeral_credential()` in `scripts/governance_router.py`.
  3. Define conjur policy template in `terraform/modules/secrets_manager/conjur_policy.hcl`.

### PPSM-001: Implement Ports, Protocols & Services Management (PPSM) Registry
- **Context**: System must document and validate all allowed internal connections for ZTA compliance.
- **Action**:
  1. Create `policies/ppsm/ppsm-registry.yml`.
  2. Create validation schema `policies/schemas/ppsm-entry.json`.
  3. Add `policies/ppsm/zero-trust-components.md` mapping table.

### PPSM-002: App-Layer L7 Egress Method Validation
- **Context**: Enforce tool use restrictions (FQDNs, allowed methods) in the GovernanceRouter before migrating to eBPF/Cilium CNI.
- **Action**:
  1. Create `policies/tool-registry.yml` defining tools and FQDNs.
  2. Wire checks into `scripts/governance_router.py` method `execute_tool()`.

### KILL-001: GPIS Admin API & Kill Switch Validation
- **Context**: Need a secure mechanism to suspend or revoke compromised agents with automated alerts + human approval gates.
- **Action**:
  1. Create `app/admin_api.py` with suspend/revoke/status endpoints.
  2. Create `scripts/kill-switch-validator.py` validation runner.


---

## 🏛️ Epic: Governance Policy Inquiry Service (GPIS) — Production Hardening

*The GPIS FastAPI PDP is the central policy decision point for all agent authorization. It is currently a ~80-line prototype. This epic upgrades it to production grade.*

### GPIS-001: Token-Efficient Governance Router Integration
- **Context**: `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md` documents a full Cache → Intent Router → Simple Rules → Large Model escalation architecture capable of 90%+ token reduction. The `scripts/governance_router.py` template exists but LLM clients are not wired up.
- **Action**:
  1. Integrate `GovernanceRouter` class into the FastAPI `/api/v1/authorize` endpoint as the primary evaluation path.
  2. Wire up Gemini Flash 2.0 as the small model (cache classifier + intent router, ~300 tokens/request).
  3. Wire up Claude Sonnet as the large model for complex/Tier 4 escalations (~600 tokens).
  4. Connect `policies/simple_rules.yml` to the router with the 20+ rules defined in the TOKEN-EFFICIENT doc.
  5. Emit Prometheus metrics for cache hit rate, token savings, and latency.
  6. Target: ≥75% cache hit rate after 48h warmup.

### GPIS-002: Policy Category Expansion (5 categories → current 3)
- **Context**: The GPIS currently supports only `SECURITY`, `DEPLOYMENT`, `OPERATIONS`. The token router architecture defines 5 categories: `CREATE`, `MODIFY`, `DELETE`, `ACCESS`, `COMPLY`. These align better with agent action patterns.
- **Action**:
  1. Migrate `PolicyCategory` enum to the 5-category model.
  2. Update `evaluate_request()` routing to handle all 5 categories.
  3. Add `COMPLY` category for audit/report generation actions (always ALLOW with audit log).
  4. Preserve backward compatibility with a legacy category mapping shim.

### GPIS-003: Signed JWT Tier Claims (Agent Tier in Token Payload)
- **Context**: JWT tokens issued by GPIS currently contain `category` and `authorized` but not `agent_tier` or expiry context. Downstream services cannot verify tier without re-querying GPIS.
- **Action**:
  1. Add `tier`, `guardrails_enforced`, `namespace`, and `jira_cr_id` (if applicable) to JWT payload.
  2. Set `exp` claim to tier-based TTL: Tier 1/2 → 15 min, Tier 3 → 5 min, Tier 4 → 2 min.
  3. Add `/api/v1/verify` endpoint for downstream services to validate GPIS tokens without re-authorization.

### GPIS-004: GPIS Health & Readiness Probes
- **Context**: The GPIS app has no `/health` or `/ready` endpoint. Kubernetes liveness probes are not configured.
- **Action**:
  1. Add `GET /health` → 200 OK with version + uptime.
  2. Add `GET /ready` → 200 if LLM clients initialized and policy cache warm, 503 otherwise.
  3. Add Kubernetes `livenessProbe` and `readinessProbe` to the GPIS Helm values.

### TEST-002: Re-validate Oct 2025 Test Suite against v2.1 Code
- **Context**: The historical test suites need to be re-run and confirmed passing against current v2.1 code to prevent regression.
- **Action**:
  1. Execute all unit and compliance tests.
  2. Remediate any API mismatches or structural updates in the test assertions.

### GUARD-001: Automated Enforcement Tests for Guardrails 13–16
- **Context**: Guardrail policies 13 through 16 lack automated test paths.
- **Action**:
  1. Write tests in `tests/compliance/test_security_controls.py` targeting budget restrictions, tool use, and validation.

---


## 🏛️ Epic: Agent Runtime — K8s Deployment Hardening

### K8S-001: Security Agent API Server Hardening
- **Context**: `agents/security/src/handlers/api_server.py` is a FastAPI server with no documented authentication, input validation, or rate limiting for the `/scan` endpoint. Container image is not pinned to a digest.
- **Action**:
  1. Add mTLS authentication using a Kubernetes `ServiceAccount` token as the bearer.
  2. Pin the base Docker image to a SHA256 digest in `agents/security/docker/Dockerfile`.
  3. Add `securityContext.readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false` in Helm values.
  4. Run `trivy image` as part of the CI/CD pipeline before any push to GHCR.

### K8S-002: Helm Chart — Missing Network Policies
- **Context**: The Helm chart at `deploy/helm/ai-agent/` does not include Kubernetes `NetworkPolicy` resources. All agents in `ai-agents-prod` namespace can communicate with each other and the Internet without restriction.
- **Action**:
  1. Add default-deny `NetworkPolicy` for the `ai-agents-prod` namespace.
  2. Add allow rules per agent: Security Agent → GPIS only, IT-Ops → GPIS + Kubernetes API, Architect → GPIS + internet egress.
  3. Enforce via `kube-bench` check in CI.

### K8S-003: Pod Security Standards Enforcement
- **Context**: Pods are not labeled with `pod-security.kubernetes.io/enforce: restricted`. The restricted PSS prevents privilege escalation, host path mounts, and root containers.
- **Action**:
  1. Label the `ai-agents-prod` namespace with `pod-security.kubernetes.io/enforce: restricted`.
  2. Update all Helm `securityContext` blocks to run as non-root UID 65534, read-only filesystem, drop ALL capabilities.
  3. Validate with `kubectl auth can-i --as=system:serviceaccount:ai-agents-prod:security-agent`.

### K8S-004: Kustomize Overlays for Dev/Staging/Prod Missing
- **Context**: The `deploy/` structure references Kustomize overlays in the Kubernetes Deployment Guide but they are not present in the repository.
- **Action**:
  1. Create `deploy/kustomize/base/` with shared resources.
  2. Create `deploy/kustomize/overlays/dev/`, `staging/`, `prod/` with environment-specific patches.
  3. Add a `make kustomize-validate` target that runs `kubectl apply --dry-run=server`.

### K3S-001: K3s Ingress NetworkPolicy Configuration
- **Context**: K3s Traefik ingress runs in the `kube-system` namespace. By default, namespace-isolated NetworkPolicies deny ingress from other namespaces.
- **Action**:
  1. Add an ingress rule to `networkpolicy.yaml` allowing traffic from `kube-system` matching Traefik ingress label.
  2. Add `kube-system` namespace selector override to dev values overlay.

---


## 🏛️ Epic: CMDB Integration — MCP-First Architecture

*Based on `docs/CMDB-ARCHITECTURE.md` and `docs/AI-GATEKEEPER-SYSTEM.md`.*

### CMDB-001: MCP Server for CMDB Queries
- **Context**: The CMDB architecture document describes a CMDB as the authoritative source for agent manifests, resource quotas, and namespace ownership. Currently, agents read static YAML config files; there is no runtime CMDB query path.
- **Action**:
  1. Implement `cmdb/mcp_server.py` — a FastMCP server exposing: `get_agent_manifest(agent_id)`, `get_namespace_quota(namespace)`, `check_resource_ownership(agent_id, resource)`.
  2. Wire GPIS `GovernanceRouter._classify_for_cache()` to call the CMDB MCP server for dynamic namespace verification.
  3. Deploy as a sidecar in the GPIS pod.
  4. Add CMDB population script: `scripts/cmdb-sync.sh` — syncs `agents/*/config/` YAML into the CMDB on startup.

### CMDB-002: Agent Manifest Schema Enforcement
- **Context**: Agent manifests (`agents/*/config/`) are unstructured YAML. There is no schema validation — invalid manifests silently pass through.
- **Action**:
  1. Define `policies/schemas/agent-manifest.json` with required fields: `agent_id`, `tier`, `namespace`, `resource_quotas`, `allowed_actions`, `budget`.
  2. Add `scripts/validate-manifest.py` that validates all manifests on `git push`.
  3. Add a GitHub Actions step that runs manifest validation on every PR.

---

## 🟡 High (P1 — Usability & Core Integration)

### TOKEN-001: Wire Up LLM Clients in GovernanceRouter
- **Context**: `scripts/governance_router.py` has `# TODO: Replace with your actual LLM client imports` throughout. The router is non-functional without real API calls.
- **Action**:
  1. Wire `google.generativeai.GenerativeModel("gemini-2.0-flash-thinking-exp")` as `self.small_model`.
  2. Wire `anthropic.Anthropic()` with `claude-sonnet-4-5` as `self.large_model`.
  3. Add retry logic with exponential backoff for API failures.
  4. Add fallback: if both LLMs are unavailable, apply `simple_rules` only and log a `DEGRADED` audit event.

### TOKEN-002: Redis Cache Backend for Production
- **Context**: The in-memory `{}` cache in `GovernanceRouter` is reset on every pod restart. Cache hit rate drops to 0% after any rolling deployment.
- **Action**:
  1. Replace `self.cache = {}` with a Redis client backed by the `redis.redis-master` service in `ai-agents-monitoring`.
  2. Add `config/cache_config.yml` TTL rules (already defined in CHANGELOG.md).
  3. Add `CACHE_BACKEND=redis` env var toggle; fall back to in-memory if not set.

### OBS-001: Prometheus Metrics for All Agents
- **Context**: The Kubernetes Deployment Guide mentions Prometheus metrics on `:9090/metrics`, but the agent source code has no instrumentation.
- **Action**:
  1. Add `prometheus_client` to each agent's `requirements.txt`.
  2. Instrument: `request_count`, `request_latency_seconds`, `governance_decision_total{outcome}`, `token_usage_total`, `cache_hit_rate`.
  3. Expose metrics endpoint in each FastAPI agent at `GET /metrics`.
  4. Add Prometheus `ServiceMonitor` to Helm charts.

### AUDIT-001: Audit Trail JSON Schema Enforcement at Runtime
- **Context**: `policies/schemas/audit-trail.json` defines the schema, but `scripts/otel-siem-emitter.py` does not validate emitted events against it before publishing.
- **Action**:
  1. Add `jsonschema.validate()` call in `otel-siem-emitter.py` before emitting any SIEM event.
  2. If validation fails, log a `SCHEMA_VIOLATION` SIEM event (separate from the failed event).
  3. Add unit tests for all 3 schemas (audit-trail, siem-event, agent-cost-record).

### CI-001: GitHub Actions — Security Pipeline Gaps
- **Context**: `.github/workflows/` lacks container image scanning (Trivy), dependency audit (pip-audit), and SBOM generation (Syft/CycloneDX). AWS-DFD-Visualizer has a more complete pipeline.
- **Action**:
  1. Add `trivy` container scan step to each `build-*.yml` workflow.
  2. Add `pip-audit` step for Python dependency scanning on every PR.
  3. Add `syft` SBOM generation and attach as a workflow artifact.
  4. Add `TruffleHog` secret scan on `push` (already exists in AWS-DFD; port pattern here).
  5. Enforce: no merge if any critical CVE found.
  6. **GH-001**: Enable GitHub Repository Secret Scanning & Push Protection.
  7. **GH-002**: Create `.github/dependabot.yml` to schedule weekly dependency checks.
  8. **GH-003**: Create `.github/workflows/codeql.yml` for CodeQL SAST.
  9. **GH-004**: Establish a weekly schedule for Dependabot security updates.

### DOC-001: SESSION_START.md & CODEMAP.md (Port from AWS-DFD)
- **Context**: AWS-DFD-Visualizer has a `SESSION_START.md` that orients new agents in 60 seconds and a `CODEMAP.md` that maps source files to features. This project has neither.
- **Action**:
  1. Create `SESSION_START.md` at project root (modeled on AWS-DFD pattern).
  2. Create `CODEMAP.md` mapping: `app/` → GPIS PDP; `agents/*/src/handlers/` → agent implementations; `scripts/` → automation; `deploy/` → K8s/Helm; `terraform/` → AWS IaC.
  3. Reference both from `README.md` Quick Start section.

---

## 🟢 Medium (P2 — Compliance & Observability)

### IR-001: IT-Ops Agent Incident Response Automation
- **Context**: The IT-Ops agent requires integrated runbook automation to handle security alerts and compliance violations (e.g. revoking compromised credentials or locking pods).
- **Action**:
  1. Define standard incident handling playbooks in `workflows/incident-response/`.
  2. Wire the incident trigger endpoints on the IT-Ops agent `/api/v1/incident`.

### COMP-001: SSP Control Gap Closure (11.6% Remaining)
- **Context**: The SSP is 88% complete (298/339 NIST 800-53 Rev 5 controls). The POA&M in `compliance/ssp/poam.md` lists the remaining 41 controls.
- **Action**:
  1. Prioritize the FIPS 140-2/140-3 controls (SC-28, SC-28(1)) — required for FedRAMP.
  2. Implement `scripts/fips-compliance-check.sh` to validate KMS key type is FIPS-compliant.
  3. Add evidence artifacts to `compliance/ssp/attachments/` for the 10 highest-priority open controls.


### COMP-002: SOC 2 Type II Readiness (2026 Q2 Target)
- **Context**: `README.md` lists "SOC 2 Type II — Scheduled 2026 Q2". No SOC 2 evidence collection is currently automated.
- **Action**:
  1. Map SOC 2 Trust Service Criteria to existing NIST 800-53 controls in `policies/control-mappings.md`.
  2. Create `compliance/soc2/` directory with evidence templates for CC6, CC7, CC8, CC9 (security, availability, confidentiality).
  3. Automate daily evidence collection: CloudTrail export, access review logs, change management records.

### GT-001: Game Theory Validator — Production Wiring
- **Context**: `scripts/game_theory/cooperative_improvement_validator.py` and `raci_game_validator.py` exist but are disconnected from the GPIS workflow. Improvement proposals are not routed through Pareto validation before human review.
- **Action**:
  1. Add `POST /api/v1/proposals` endpoint to GPIS that accepts improvement proposals.
  2. Auto-run `cooperative_improvement_validator.py` on each proposal.
  3. Only forward Pareto-efficient proposals to human approval queue.
  4. Log rejected proposals as `PROPOSAL_DENIED_NON_PARETO` SIEM events.

### OTEL-001: Distributed Tracing End-to-End
- **Context**: `scripts/otel-siem-emitter.py` emits OTLP spans but agent-to-agent traces are not correlated by a shared `trace_id`. Each agent starts a new root span.
- **Action**:
  1. Propagate W3C `traceparent` header through all MCP and REST calls between agents.
  2. Add `opentelemetry-sdk` and `opentelemetry-exporter-otlp-proto-grpc` to agent requirements.
  3. Instrument GPIS and each agent with `@tracer.start_as_current_span()` decorators on handler functions.
  4. Update Grafana dashboard to show cross-agent waterfall traces.

### PAR-001: PAR-PROTO Multi-Agent Workflow Automation
- **Context**: `workflows/PAR-PROTO/` documents the Copilot → Claude → Gemini development pattern but it is a manual process. No CI/CD step enforces the handoff sequence.
- **Action**:
  1. Create `scripts/par-proto-handoff.py` — reads a `par-proto.yml` task definition, auto-assigns roles by tier, and creates GitHub Issues for each agent phase.
  2. Add webhook receiver that auto-closes the current phase issue when a PR is merged.
  3. Integrate with Jira: auto-create PAR-PROTO sub-tasks linked to the parent CR.

---

## 🔵 Low (P3 — Polish & Future)

### UI-001: Governance Dashboard (Grafana)
- **Context**: Prometheus metrics are planned but no Grafana dashboard JSON exists. Operations teams have no visibility into governance decisions.
- **Action**: Create `deploy/monitoring/grafana-dashboard.json` showing: token usage/savings, cache hit rate, governance decision distribution (ALLOW/DENY/ESCALATE), agent cost trends, and SLA compliance.

### DOC-002: Interactive API Documentation (Swagger/OpenAPI)
- **Context**: FastAPI auto-generates Swagger UI at `/docs`, but it is not documented in the README or agent deployment guides. Developers don't know how to test the GPIS.
- **Action**: Add API documentation section to `README.md` and `docs/QUICK-REFERENCE.md` with example `curl` commands for all 3 GPIS endpoints.

### COST-001: FinOps — Agent Cost Anomaly Detection
- **Context**: `scripts/cost-report.sh` generates cost reports but there is no alerting when an agent exceeds its budget. `policies/schemas/agent-cost-record.json` defines the cost record schema.
- **Action**:
  1. Add `scripts/cost-anomaly-detector.py` — reads cost records, compares against agent manifest budget, emits SIEM alert if > 80% consumed.
  2. Wire to Prometheus alertmanager rule: `alert: AgentBudgetWarning` at 80%, `AgentBudgetCritical` at 95%.

### PAT-001: Patent Claim Implementation Traceability
- **Context**: `docs/US-PATENT-APPLICATION.md` and `docs/PATENT-DISCLOSURE.md` define the Atomic Governance Transaction system. No code artifact directly maps implementation to patent claims.
- **Action**: Create `docs/PATENT-IMPLEMENTATION-MAP.md` — a claim-by-claim table mapping each patent claim to the exact file, function, and line range that implements it. This is critical for USPTO prosecution and FTO analysis.

---

## 🔮 v3.0 Roadmap Backlog

### Section A: AI-Native Governance Agent (MCP-First)
- [ ] **GovernanceAgentV4 — Pattern Learning** — Implement `PatternLearner` class from `GOVERNANCE-AGENT-ARCHITECTURE.md` Phase 4. Auto-propose policy optimizations after 10+ identical escalations.
- [ ] **Agent-to-Agent mTLS Authentication** — Replace REST API calls with MCP protocol over mTLS using Kubernetes cert-manager issued certificates.
- [ ] **Governance Agent HA Deployment** — 3-replica `governance-agent` deployment with leader election for policy cache writes.

### Section B: Multi-Region & Air-Gap Support
- [ ] **Air-Gap Mode** — Fully offline governance decision path: local LLM (Ollama/llama3) + Redis cache only, zero external API calls. Required for DoD IL5 environments.
- [ ] **Multi-Region Failover** — Active-passive GPIS deployment across two AWS regions with DynamoDB Global Tables for audit log replication.

### Section C: Autonomous Policy Optimization
- [ ] **Reinforcement Learning Policy Tuner** — Use historical decision data to auto-tune simple_rules thresholds, minimizing unnecessary escalations while maintaining <1% false-positive allow rate.
- [ ] **Natural Language Policy Authoring** — Allow governance operators to describe new policies in plain English; GPIS converts to `simple_rules.yml` entries with validation.

### Section D: Platform Extensions
- [ ] **GitHub App Integration** — GPIS as a GitHub App: auto-block PRs that introduce new agent capabilities without a corresponding governance policy update.
- [ ] **Slack Governance Bot** — Tier 2 escalations auto-post to Slack with approve/deny buttons backed by GPIS webhook.
- [ ] **ITSM Integration (ServiceNow)** — Auto-create ServiceNow change requests for Tier 3/4 operations, replacing the current manual Jira CR flow.

---

## 🩺 Lessons Learned — Quick Reference

See [LESSONS_LEARNED.md](LESSONS_LEARNED.md) for full diagnostic playbooks.

| ID | Summary | Root Cause |
|----|---------|------------|
| LL-001 | Hardcoded JWT secret in `app/main.py` | No secrets scanning gate in CI/CD |
| LL-002 | CVE > 9.0 policy returns APPROVED — intent unclear | Missing business context in docstring; no integration test for both branches |
| LL-003 | GovernanceRouter LLM clients never wired up | Template code delivered as documentation artifact, not implementation |
| LL-004 | Agent manifests unvalidated — invalid YAML silently accepted | No schema + no pre-commit hook |

---

*Maintained by the Antigravity engineering agent. Session logs go at the top of `## 📍 Session Log`. Completed items marked `[x]` with resolution date. All critical bugs must be logged in `LESSONS_LEARNED.md` before closing.*
