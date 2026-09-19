# K8S AI DevSecOps Agent Governance Framework — Next Release Backlog

This list is based on a full code review (June 19, 2026) against the current v2.1 implementation, gap analysis across the GPIS/CMDB/Compliance layers, and token-efficiency lessons learned from the AWS-DFD-Visualizer and this project's own `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md`.

---
## 📍 Session Log

### ✅ Session: September 19, 2026 (Kernel hardening — company-minimum gaps)
- [x] **SEC-001 residual** — `GPIS_JWT_SECRET` is required with no default; published defaults are rejected (`app/main.py` `get_jwt_secret()`).
- [x] **AUDIT-002** — every `/api/v1/authorize` allow and deny emits a schema-validated `audit-trail.json` record (`app/audit.py`). Schema fields unchanged.
- [x] **KILL-001 auth** — `/admin/v1/*` requires `X-GPIS-Admin-Key` / `GPIS_ADMIN_API_KEY`.
- [x] **YAML conditions** — `evaluate_condition()` enforces path, namespace, tier, quota, labels, backup, cost, read-only (fail-closed on unknown conditions).
- [x] **Agents call GPIS** — Security, IT-Ops, Architect, and AI training/scan paths call `require_gpis_token()` before side effects (`agents/shared/gpis_client.py`).
- [x] **Allow+deny tests** — `tests/unit/test_simple_rules_allow_deny.py` covers every `simple_rules.yml` key. Probe aliases `/health/live` and `/health/ready` added.

### ✅ Session: September 19, 2026 (SA dual-persona review + token-efficiency check)
- [x] **SA / PM review** — Produced `docs/reviews/governance_review_3.0.1.md`. Classified remaining work as Lane A (policy-as-code agents may draft), Lane B (PDP kernel human-gated), Lane C (platform, not policy iteration).
- [x] **Token-efficiency assessment** — Playbook is Cache → Intent → Simple Rules → Large Model, but `app/main.py` does not import `scripts/governance_router.py`. Live authorize is 0 LLM tokens (YAML + Python). Do not treat 90.25% modeled savings as a measured GPIS result. Coding-agent hygiene: `CODEMAP.md` + `.agentignore` exist; `SESSION_START.md` still missing.
- [x] **Stale backlog retag** — SEC-002, GPIS-003 (mostly), GPIS-004 (probes exist), K8S-002 marked complete in live code. Reopened **SEC-001 residual** (default JWT unless `ENVIRONMENT=production`). Recorded GPIS-004 probe path mismatch (`/health` vs Helm `/health/live`).
- Standing guards: `policies/schemas/audit-trail.json` not mutated. No secrets committed.

### ✅ Session: August 2, 2026 (Antigravity Goal Execution)
- [x] **SEC-001 (P0)** — Enforced `GPIS_JWT_SECRET` env var in `app/main.py` and test fixtures. Removed hardcoded JWT key.
- [x] **SEC-002 (P0)** — Resolved CVE policy logic ambiguity in `app/policy_engine.py`. Renamed to `evaluate_security_patch_deployment()` requiring `action: emergency_patch` for critical CVE approvals; blocks otherwise.
- [x] **GPIS-003 & GPIS-004 (Epic)** — Added `/health` and `/ready` probes and `/api/v1/verify` token verification endpoint to `app/main.py`. Updated JWT claims payload with tier, namespace, and Jira CR details.
- [x] **K8S-002 (Epic)** — Validated default-deny Kubernetes `NetworkPolicy` template (`deploy/helm/ai-agent/templates/networkpolicy.yaml`).
- [x] **IP Boundary & Zero Trust Architecture** — Created `scripts/export-external-sdk.sh` for safe external SDK bundle export with zero secret findings (112 clean files). Documented ZT architecture & 152 ZTOM controls in `docs/ARCHITECTURE-RECOMMENDATIONS-ZT.md`. Updated `.agents/rules/` and `.agentignore`.
- [x] **eMASS Mock Server & E2E Splunk TA Integration** — Created `emass-mock-server` repository with 11 endpoints, seeded 10+ POA&Ms using real NIST control numbers, and implemented E2E validation (`tests/test_e2e_emass_integration.sh`) for Splunk TA-suhlabs-eMASS ingestion.


### 🔄 Session: June 19, 2026 (Antigravity Phase 2 Execution - Part 1)
- [/] **Zero Trust & Hardening Execution** — Started executing Phase 2 plan. Bootstrapped namespaces and service accounts (`scripts/identity-bootstrap.sh`), updated `values.yaml` and `serviceaccount.yaml` to enforce `automountServiceAccountToken: false` by default, consolidated `.claude/prompts/` rules to `.agents/rules/`, and updated `README.md` and `CODEMAP.md` indexes.

### ✅ Session: June 19, 2026 (Antigravity Code Review)
- [x] **Full Project Audit & Backlog Creation** — Reviewed all source code, docs, agents, .claude prompts, scripts, Helm charts, Terraform modules, and compliance artifacts. Created this `NEXT_RELEASE_TODO.md`, the `.agents/rules/` directory with 8 structured rule files, and upgraded the `.claude/prompts/` context with token-efficient, IDE-agnostic patterns. Merged the best patterns from AWS-DFD-Visualizer (session log discipline, lessons-learned playbooks, post-goal validation) with this project's governance kernel (GPIS, CMDB, PAR-PROTO, token router). See `LESSONS_LEARNED.md` for root causes.
- [x] **Critical Security Bug Identified: Hardcoded JWT Secret** — `app/main.py` line 11 contains `SECRET_KEY = "suhlabs-super-secret-governance-key"` hardcoded in source. This is a P0 security vulnerability that violates Guardrail #8, NIST IA-5, and any FedRAMP Moderate baseline. Logged in `LESSONS_LEARNED.md` as LL-001.
- [x] **Critical Logic Bug Identified: CVE Score Policy Inversion** — `app/policy_engine.py` `evaluate_security()` comment documents that `CVE score > 9.0 → APPROVED` which is the *inverse* of correct security logic (critical CVE should BLOCK, not approve). The actual intent was likely "APPROVED for emergency patch deployment when score > 9.0". This ambiguity must be resolved and documented. Logged as LL-002.

---

## Lane index (SA review 2026-09-19)

Use these tags when picking work. Full evidence: [docs/reviews/governance_review_3.0.1.md](docs/reviews/governance_review_3.0.1.md).

| Lane | Meaning | AI agents |
|------|---------|-----------|
| **A** | Policy-as-code (`simple_rules.yml`, registries, mappings, allow+deny tests) | Draft; human merge |
| **B** | GPIS PDP kernel, JWT, audit-trail schema, admin/kill-switch | Propose only; human-gated apply |
| **C** | K8s, CI, CMDB wiring, Redis, metrics, docs polish | Engineering; not “iterate policy” |

**Do first (closes the agent-policy loop):** SEC-001 residual (B) → authorize audit emit (B) → admin auth (B) → full YAML condition eval + migrate legacy Python rules (A+B) → agents call GPIS (B) → then GPIS-001 router with hash cache before any LLM (B).

---

## 🔴 Critical (P0 — Security & Correctness)

### [x] SEC-001: Hardcoded JWT Secret in `app/main.py` **[Lane B] [closed 2026-09-19]**
- **Context**: Fail-closed. `get_jwt_secret()` requires `GPIS_JWT_SECRET` and rejects published defaults.
- **Done**: startup assertion, pytest coverage, no default in `os.getenv`.
- **Guardrails**: #8 (Secrets), #6 (Audit), NIST IA-5, FedRAMP IA-5(1)
- **See also**: [LL-001](LESSONS_LEARNED.md)

### [x] SEC-002: CVE Policy Logic Ambiguity Must Be Resolved (closed 2026-08-02; confirmed live 2026-09-19)
- **Context**: `evaluate_security()` in `app/policy_engine.py` approves requests when `cve_score > 9.0` per its docstring. This is the inverse of standard security posture (critical CVEs should block, not pass). The *intent* appears to be approving emergency remediation pipelines, but the ambiguity means a misconfigured caller could accidentally allow unpatched critical vulnerabilities.
- **Action**:
  1. Rename the function to `evaluate_security_patch_deployment()` to make intent explicit.
  2. Add a `require_action == "emergency_patch"` guard: if the payload does not include `action: emergency_patch`, any CVE > 9.0 returns DENIED.
  3. Add integration tests for both the patch-approval and block-on-unpatched paths.
  4. Document the rule in `policies/agent-safety-policies.md` under "Security Policy Category Rules."
- **See also**: [LL-002](LESSONS_LEARNED.md)

### SEC-003: FastAPI Missing Input Validation & Rate Limiting **[Lane B] [partial]**
- **Context**: Live GPIS has `slowapi` 100/min per IP and `agent_id` charset/length validation. Remaining gaps: no payload size cap, no per-agent rate limit, no caller auth on authorize or admin.
- **Action** (remaining; rate limit + `agent_id` regex already in live `app/main.py` / `policy_engine.py`):
  1. Cap `payload` size (2KB) on `PolicyRequest`.
  2. Add per-`agent_id` rate limit (10 req/min) in addition to 100/min per IP.
  3. Add mTLS or API key header validation on `/api/v1/authorize` **and** `/admin/v1/*`.
  4. Write Pytest integration tests for oversized payloads and rate-limit breach.

### SEC-005: Ephemeral Credential Lifecycle (CyberArk Conjur Sidecar) **[Lane C]**
- **Context**: Static K8s secrets are a major security risk. Agents must fetch short-lived ephemeral tokens from CyberArk Conjur via a sidecar pattern based on Projected ServiceAccount tokens.
- **Action**:
  1. Create `deploy/helm/ai-agent/templates/conjur-sidecar.yaml`.
  2. Implement `_fetch_ephemeral_credential()` in `scripts/governance_router.py`.
  3. Define conjur policy template in `terraform/modules/secrets_manager/conjur_policy.hcl`.

### [x] PPSM-001: Implement Ports, Protocols & Services Management (PPSM) Registry (files + schema tests exist; registry still DRAFT — enforcement is PPSM-002 / GPIS load) **[Lane A follow-on]**
- **Context**: System must document and validate all allowed internal connections for ZTA compliance.
- **Action**:
  1. Create `policies/ppsm/ppsm-registry.yml`.
  2. Create validation schema `policies/schemas/ppsm-entry.json`.
  3. Add `policies/ppsm/zero-trust-components.md` mapping table.

### PPSM-002: App-Layer L7 Egress Method Validation **[Lane A]**
- **Context**: Enforce tool use restrictions (FQDNs, allowed methods) in the GovernanceRouter before migrating to eBPF/Cilium CNI.
- **Action**:
  1. Create `policies/tool-registry.yml` defining tools and FQDNs.
  2. Wire checks into `scripts/governance_router.py` method `execute_tool()`.

### KILL-001: GPIS Admin API & Kill Switch Validation **[Lane B] [partial — admin key required 2026-09-19; still in-memory]**
- **Context**: Need a secure mechanism to suspend or revoke compromised agents with automated alerts + human approval gates.
- **Action**:
  1. Create `app/admin_api.py` with suspend/revoke/status endpoints.
  2. Create `scripts/kill-switch-validator.py` validation runner.


---

## 🏛️ Epic: Governance Policy Inquiry Service (GPIS) — Production Hardening

*The GPIS FastAPI PDP is the central policy decision point for all agent authorization. It is currently a ~80-line prototype. This epic upgrades it to production grade.*

### GPIS-001: Token-Efficient Governance Router Integration **[Lane B]**
- **Context**: `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md` documents a Cache → Intent Router → Simple Rules → Large Model escalation architecture. `scripts/governance_router.py` is **not imported** by `app/main.py`. Live authorize is already 0 LLM tokens (YAML + Python). Integrating the router the wrong way (small-model cache classifier first) would **increase** tokens. See TOKEN-003.
- **Action**:
  1. Integrate `GovernanceRouter` into `/api/v1/authorize` only after TOKEN-003 order is implemented (hash cache → YAML → small model → large model).
  2. Wire Gemini Flash as the small model for unstructured intent only (~300 tokens/request when used).
  3. Wire Claude as the large model for unmatched / high-risk escalations.
  4. Keep `policies/simple_rules.yml` as the 0-token path; do not skip it.
  5. Emit Prometheus metrics for cache hit rate, token savings, and latency.
  6. Target: ≥75% cache hit rate after 48h warmup, measured on live authorize — not the spreadsheet model.

### GPIS-002: Policy Category Expansion (5 categories → current 3) **[Lane A+B] [partial — enum + YAML exist; legacy Python still first]**
- **Context**: The GPIS currently supports only `SECURITY`, `DEPLOYMENT`, `OPERATIONS`. The token router architecture defines 5 categories: `CREATE`, `MODIFY`, `DELETE`, `ACCESS`, `COMPLY`. These align better with agent action patterns.
- **Action**:
  1. Migrate `PolicyCategory` enum to the 5-category model.
  2. Update `evaluate_request()` routing to handle all 5 categories.
  3. Add `COMPLY` category for audit/report generation actions (always ALLOW with audit log).
  4. Preserve backward compatibility with a legacy category mapping shim.

### [x] GPIS-003: Signed JWT Tier Claims (Agent Tier in Token Payload) (closed 2026-08-02; residual: add `guardrails_enforced` claim) **[Lane B residual]**
- **Context**: JWT tokens issued by GPIS currently contain `category` and `authorized` but not `agent_tier` or expiry context. Downstream services cannot verify tier without re-querying GPIS.
- **Action**:
  1. Add `tier`, `guardrails_enforced`, `namespace`, and `jira_cr_id` (if applicable) to JWT payload.
  2. Set `exp` claim to tier-based TTL: Tier 1/2 → 15 min, Tier 3 → 5 min, Tier 4 → 2 min.
  3. Add `/api/v1/verify` endpoint for downstream services to validate GPIS tokens without re-authorization.

### GPIS-004: GPIS Health & Readiness Probes **[Lane C] [residual 2026-09-19]**
- **Context**: GPIS now has `GET /health` and `GET /ready`, but `/ready` always returns ready. Helm `values.yaml` probes `/health/live` and `/health/ready` (path mismatch).
- **Action** (remaining):
  1. Align probe paths (`/health` + `/ready`, or add aliases `/health/live` and `/health/ready`).
  2. Make `/ready` fail when the policy file is missing or (if Redis is required) Redis is down.
  3. Confirm Helm `livenessProbe` / `readinessProbe` hit the live GPIS routes.

### TEST-002: Re-validate Oct 2025 Test Suite against v2.1 Code **[Lane C]**
- **Context**: The historical test suites need to be re-run and confirmed passing against current v2.1 code to prevent regression.
- **Action**:
  1. Execute all unit and compliance tests.
  2. Remediate any API mismatches or structural updates in the test assertions.

### GUARD-001: Automated Enforcement Tests for Guardrails 13–16 **[Lane A]**
- **Context**: Guardrail policies 13 through 16 lack automated test paths.
- **Action**:
  1. Write tests in `tests/compliance/test_security_controls.py` targeting budget restrictions, tool use, and validation.

---


## 🏛️ Epic: Agent Runtime — K8s Deployment Hardening

### K8S-001: Security Agent API Server Hardening **[Lane C]**
- **Context**: `agents/security/src/handlers/api_server.py` is a FastAPI server with no documented authentication, input validation, or rate limiting for the `/scan` endpoint. Container image is not pinned to a digest.
- **Action**:
  1. Add mTLS authentication using a Kubernetes `ServiceAccount` token as the bearer.
  2. Pin the base Docker image to a SHA256 digest in `agents/security/docker/Dockerfile`.
  3. Add `securityContext.readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false` in Helm values.
  4. Run `trivy image` as part of the CI/CD pipeline before any push to GHCR.

### [x] K8S-002: Helm Chart — Missing Network Policies (template exists; review per-agent allow lists) **[Lane C]**
- **Context**: The Helm chart at `deploy/helm/ai-agent/` does not include Kubernetes `NetworkPolicy` resources. All agents in `ai-agents-prod` namespace can communicate with each other and the Internet without restriction.
- **Action**:
  1. Add default-deny `NetworkPolicy` for the `ai-agents-prod` namespace.
  2. Add allow rules per agent: Security Agent → GPIS only, IT-Ops → GPIS + Kubernetes API, Architect → GPIS + internet egress.
  3. Enforce via `kube-bench` check in CI.

### K8S-003: Pod Security Standards Enforcement **[Lane C]**
- **Context**: Pods are not labeled with `pod-security.kubernetes.io/enforce: restricted`. The restricted PSS prevents privilege escalation, host path mounts, and root containers.
- **Action**:
  1. Label the `ai-agents-prod` namespace with `pod-security.kubernetes.io/enforce: restricted`.
  2. Update all Helm `securityContext` blocks to run as non-root UID 65534, read-only filesystem, drop ALL capabilities.
  3. Validate with `kubectl auth can-i --as=system:serviceaccount:ai-agents-prod:security-agent`.

### K8S-004: Kustomize Overlays for Dev/Staging/Prod Missing **[Lane C] [partial — `deploy/kustomize/base/` exists]**
- **Context**: The `deploy/` structure references Kustomize overlays in the Kubernetes Deployment Guide but they are not present in the repository.
- **Action**:
  1. Create `deploy/kustomize/base/` with shared resources.
  2. Create `deploy/kustomize/overlays/dev/`, `staging/`, `prod/` with environment-specific patches.
  3. Add a `make kustomize-validate` target that runs `kubectl apply --dry-run=server`.

### K3S-001: K3s Ingress NetworkPolicy Configuration **[Lane C]**
- **Context**: K3s Traefik ingress runs in the `kube-system` namespace. By default, namespace-isolated NetworkPolicies deny ingress from other namespaces.
- **Action**:
  1. Add an ingress rule to `networkpolicy.yaml` allowing traffic from `kube-system` matching Traefik ingress label.
  2. Add `kube-system` namespace selector override to dev values overlay.

---


## 🏛️ Epic: CMDB Integration — MCP-First Architecture

*Based on `docs/CMDB-ARCHITECTURE.md` and `docs/AI-GATEKEEPER-SYSTEM.md`.*

### CMDB-001: MCP Server for CMDB Queries **[Lane C] [partial — `cmdb/` Mongo API exists; not a GPIS sidecar]**
- **Context**: The CMDB architecture document describes a CMDB as the authoritative source for agent manifests, resource quotas, and namespace ownership. Currently, agents read static YAML config files; there is no runtime CMDB query path.
- **Action**:
  1. Implement `cmdb/mcp_server.py` — a FastMCP server exposing: `get_agent_manifest(agent_id)`, `get_namespace_quota(namespace)`, `check_resource_ownership(agent_id, resource)`.
  2. Wire GPIS `GovernanceRouter._classify_for_cache()` to call the CMDB MCP server for dynamic namespace verification.
  3. Deploy as a sidecar in the GPIS pod.
  4. Add CMDB population script: `scripts/cmdb-sync.sh` — syncs `agents/*/config/` YAML into the CMDB on startup.

### CMDB-002: Agent Manifest Schema Enforcement **[Lane A+C]**
- **Context**: Agent manifests (`agents/*/config/`) are unstructured YAML. There is no schema validation — invalid manifests silently pass through.
- **Action**:
  1. Define `policies/schemas/agent-manifest.json` with required fields: `agent_id`, `tier`, `namespace`, `resource_quotas`, `allowed_actions`, `budget`.
  2. Add `scripts/validate-manifest.py` that validates all manifests on `git push`.
  3. Add a GitHub Actions step that runs manifest validation on every PR.

---

## 🟡 High (P1 — Usability & Core Integration)

### TOKEN-001: Wire Up LLM Clients in GovernanceRouter **[Lane B]**
- **Context**: `scripts/governance_router.py` has `# TODO: Replace with your actual LLM client imports` throughout. The router is non-functional without real API calls.
- **Action**:
  1. Wire `google.generativeai.GenerativeModel("gemini-2.0-flash-thinking-exp")` as `self.small_model`.
  2. Wire `anthropic.Anthropic()` with `claude-sonnet-4-5` as `self.large_model`.
  3. Add retry logic with exponential backoff for API failures.
  4. Add fallback: if both LLMs are unavailable, apply `simple_rules` only and log a `DEGRADED` audit event.

### TOKEN-002: Redis Cache Backend for Production **[Lane C]**
- **Context**: The in-memory `{}` cache in `GovernanceRouter` is reset on every pod restart. Cache hit rate drops to 0% after any rolling deployment. Live code also references `self.cache` without initializing it (`scripts/governance_router.py` cache fallback).
- **Action**:
  1. Replace `self.cache = {}` with a Redis client backed by the `redis.redis-master` service in `ai-agents-monitoring`.
  2. Add `config/cache_config.yml` TTL rules (already defined in CHANGELOG.md).
  3. Add `CACHE_BACKEND=redis` env var toggle; fall back to in-memory if not set.

### TOKEN-003: Deterministic cache before any LLM (SA 2026-09-19) **[Lane B]**
- **Context**: Documented architecture calls a small model as the cache classifier. Best practice is hash/key lookup (0 tokens), then `simple_rules.yml`, then a small model only for unstructured intent, then a large model. Using Gemini to decide cacheability adds tokens and the classifier prompt is far larger than the ~100-token budget.
- **Action**:
  1. Compute a deterministic cache key first (see `config/cache_config.yml` format).
  2. On miss, evaluate `simple_rules.yml` before any LLM.
  3. Call the small model only when no rule matches; large model last; distill repeats into YAML.
  4. Record `tokens_used` on every `/api/v1/authorize` response and make `benchmark_token_savings.py` read live metrics, not only assumed mix rates.
  5. Initialize `self.cache` (or Redis) so the fallback path cannot AttributeError.

### AUDIT-002: Emit audit-trail on every GPIS decision (SA 2026-09-19) **[Lane B] [x closed 2026-09-19]**
- **Context**: `app/audit.py` emits one schema-validated record per authorize allow/deny. Required fields unchanged.
- **Follow-on**: durable store (not only `GPIS_AUDIT_DIR` files) and SIEM forward.

### OBS-001: Prometheus Metrics for All Agents **[Lane C]**
- **Context**: The Kubernetes Deployment Guide mentions Prometheus metrics on `:9090/metrics`, but the agent source code has no instrumentation.
- **Action**:
  1. Add `prometheus_client` to each agent's `requirements.txt`.
  2. Instrument: `request_count`, `request_latency_seconds`, `governance_decision_total{outcome}`, `token_usage_total`, `cache_hit_rate`.
  3. Expose metrics endpoint in each FastAPI agent at `GET /metrics`.
  4. Add Prometheus `ServiceMonitor` to Helm charts.

### AUDIT-001: Audit Trail JSON Schema Enforcement at Runtime **[Lane A+B]**
- **Context**: `policies/schemas/audit-trail.json` defines the schema, but `scripts/otel-siem-emitter.py` does not validate emitted events against it before publishing.
- **Action**:
  1. Add `jsonschema.validate()` call in `otel-siem-emitter.py` before emitting any SIEM event.
  2. If validation fails, log a `SCHEMA_VIOLATION` SIEM event (separate from the failed event).
  3. Add unit tests for all 3 schemas (audit-trail, siem-event, agent-cost-record).

### CI-001: GitHub Actions — Security Pipeline Gaps **[Lane C]**
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

### DOC-001: SESSION_START.md & CODEMAP.md (Port from AWS-DFD) **[Lane C] [partial — CODEMAP.md exists]**
- **Context**: AWS-DFD-Visualizer has a `SESSION_START.md` that orients new agents in 60 seconds and a `CODEMAP.md` that maps source files to features. This project has neither.
- **Action**:
  1. Create `SESSION_START.md` at project root (modeled on AWS-DFD pattern).
  2. Create `CODEMAP.md` mapping: `app/` → GPIS PDP; `agents/*/src/handlers/` → agent implementations; `scripts/` → automation; `deploy/` → K8s/Helm; `terraform/` → AWS IaC.
  3. Reference both from `README.md` Quick Start section.

---

## 🟢 Medium (P2 — Compliance & Observability)

### IR-001: IT-Ops Agent Incident Response Automation **[Lane C]**
- **Context**: The IT-Ops agent requires integrated runbook automation to handle security alerts and compliance violations (e.g. revoking compromised credentials or locking pods).
- **Action**:
  1. Define standard incident handling playbooks in `workflows/incident-response/`.
  2. Wire the incident trigger endpoints on the IT-Ops agent `/api/v1/incident`.

### COMP-001: SSP Control Gap Closure (11.6% Remaining) **[Lane A]**
- **Context**: The SSP is 88% complete (298/339 NIST 800-53 Rev 5 controls). The POA&M in `compliance/ssp/poam.md` lists the remaining 41 controls.
- **Action**:
  1. Prioritize the FIPS 140-2/140-3 controls (SC-28, SC-28(1)) — required for FedRAMP.
  2. Implement `scripts/fips-compliance-check.sh` to validate KMS key type is FIPS-compliant.
  3. Add evidence artifacts to `compliance/ssp/attachments/` for the 10 highest-priority open controls.


### COMP-002: SOC 2 Type II Readiness (2026 Q2 Target) **[Lane A]**
- **Context**: `README.md` lists "SOC 2 Type II — Scheduled 2026 Q2". No SOC 2 evidence collection is currently automated.
- **Action**:
  1. Map SOC 2 Trust Service Criteria to existing NIST 800-53 controls in `policies/control-mappings.md`.
  2. Create `compliance/soc2/` directory with evidence templates for CC6, CC7, CC8, CC9 (security, availability, confidentiality).
  3. Automate daily evidence collection: CloudTrail export, access review logs, change management records.

### GT-001: Game Theory Validator — Production Wiring **[Lane A]**
- **Context**: `scripts/game_theory/cooperative_improvement_validator.py` and `raci_game_validator.py` exist but are disconnected from the GPIS workflow. Improvement proposals are not routed through Pareto validation before human review.
- **Action**:
  1. Add `POST /api/v1/proposals` endpoint to GPIS that accepts improvement proposals.
  2. Auto-run `cooperative_improvement_validator.py` on each proposal.
  3. Only forward Pareto-efficient proposals to human approval queue.
  4. Log rejected proposals as `PROPOSAL_DENIED_NON_PARETO` SIEM events.

### OTEL-001: Distributed Tracing End-to-End **[Lane C]**
- **Context**: `scripts/otel-siem-emitter.py` emits OTLP spans but agent-to-agent traces are not correlated by a shared `trace_id`. Each agent starts a new root span.
- **Action**:
  1. Propagate W3C `traceparent` header through all MCP and REST calls between agents.
  2. Add `opentelemetry-sdk` and `opentelemetry-exporter-otlp-proto-grpc` to agent requirements.
  3. Instrument GPIS and each agent with `@tracer.start_as_current_span()` decorators on handler functions.
  4. Update Grafana dashboard to show cross-agent waterfall traces.

### PAR-001: PAR-PROTO Multi-Agent Workflow Automation **[Lane C]**
- **Context**: `workflows/PAR-PROTO/` documents the Copilot → Claude → Gemini development pattern but it is a manual process. No CI/CD step enforces the handoff sequence.
- **Action**:
  1. Create `scripts/par-proto-handoff.py` — reads a `par-proto.yml` task definition, auto-assigns roles by tier, and creates GitHub Issues for each agent phase.
  2. Add webhook receiver that auto-closes the current phase issue when a PR is merged.
  3. Integrate with Jira: auto-create PAR-PROTO sub-tasks linked to the parent CR.

---

## 🔵 Low (P3 — Polish & Future)

### UI-001: Governance Dashboard (Grafana) **[Lane C]**
- **Context**: Prometheus metrics are planned but no Grafana dashboard JSON exists. Operations teams have no visibility into governance decisions.
- **Action**: Create `deploy/monitoring/grafana-dashboard.json` showing: token usage/savings, cache hit rate, governance decision distribution (ALLOW/DENY/ESCALATE), agent cost trends, and SLA compliance.

### DOC-002: Interactive API Documentation (Swagger/OpenAPI) **[Lane C]**
- **Context**: FastAPI auto-generates Swagger UI at `/docs`, but it is not documented in the README or agent deployment guides. Developers don't know how to test the GPIS.
- **Action**: Add API documentation section to `README.md` and `docs/QUICK-REFERENCE.md` with example `curl` commands for all 3 GPIS endpoints.

### COST-001: FinOps — Agent Cost Anomaly Detection **[Lane C]**
- **Context**: `scripts/cost-report.sh` generates cost reports but there is no alerting when an agent exceeds its budget. `policies/schemas/agent-cost-record.json` defines the cost record schema.
- **Action**:
  1. Add `scripts/cost-anomaly-detector.py` — reads cost records, compares against agent manifest budget, emits SIEM alert if > 80% consumed.
  2. Wire to Prometheus alertmanager rule: `alert: AgentBudgetWarning` at 80%, `AgentBudgetCritical` at 95%.

### PAT-001: Patent Claim Implementation Traceability **[Lane A]**
- **Context**: `docs/US-PATENT-APPLICATION.md` and `docs/PATENT-DISCLOSURE.md` define the Atomic Governance Transaction system. No code artifact directly maps implementation to patent claims.
- **Action**: Create `docs/PATENT-IMPLEMENTATION-MAP.md` — a claim-by-claim table mapping each patent claim to the exact file, function, and line range that implements it. This is critical for USPTO prosecution and FTO analysis.

---

## 🔮 v3.0 Roadmap Backlog

### Section A: AI-Native Governance Agent (MCP-First) **[Lane A future — human-gated apply]**
- [ ] **GovernanceAgentV4 — Pattern Learning** — Implement `PatternLearner` class from `GOVERNANCE-AGENT-ARCHITECTURE.md` Phase 4. Auto-propose policy optimizations after 10+ identical escalations.
- [ ] **Agent-to-Agent mTLS Authentication** — Replace REST API calls with MCP protocol over mTLS using Kubernetes cert-manager issued certificates.
- [ ] **Governance Agent HA Deployment** — 3-replica `governance-agent` deployment with leader election for policy cache writes.

### Section B: Multi-Region & Air-Gap Support **[Lane C]**
- [ ] **Air-Gap Mode** — Fully offline governance decision path: local LLM (Ollama/llama3) + Redis cache only, zero external API calls. Required for DoD IL5 environments.
- [ ] **Multi-Region Failover** — Active-passive GPIS deployment across two AWS regions with DynamoDB Global Tables for audit log replication.

### Section C: Autonomous Policy Optimization **[Lane A — draft only; never auto-apply]**
- [ ] **Reinforcement Learning Policy Tuner** — Use historical decision data to auto-tune simple_rules thresholds, minimizing unnecessary escalations while maintaining <1% false-positive allow rate.
- [ ] **Natural Language Policy Authoring** — Allow governance operators to describe new policies in plain English; GPIS converts to `simple_rules.yml` entries with validation.

### Section D: Platform Extensions **[Lane C]**
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
