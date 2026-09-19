# Production-scale implementation plan

**Date:** 2026-09-19  
**Baseline:** `master` @ `4bcfc84` (`sec: fail-closed GPIS kernel so agents cannot act without a token`)  
**Goal:** A company can run AI agents in a real cluster where **no side effect happens without a GPIS JWT**, the decision is **durable and auditable**, and ops can **operate, scale, and kill** the system.

This is not “finish every line in NEXT_RELEASE_TODO.” Theater (152 ZTOM, modeled 90% token savings) is not a production gate.

---

## Current baseline (already on master)

| Capability | Status |
|------------|--------|
| Fail-closed `GPIS_JWT_SECRET` / `GPIS_ADMIN_API_KEY` | Done |
| Audit-trail emit on allow and deny (`app/audit.py`) | Done (local files under `GPIS_AUDIT_DIR`) |
| Admin kill-switch header auth | Done (in-memory `SUSPENSIONS`) |
| YAML condition evaluation | Done |
| Agents call `require_gpis_token()` before work | Done (app-layer only) |
| Allow+deny tests for every `simple_rules.yml` key | Done |
| Helm probe aliases `/health/live`, `/health/ready` | Done |

**Still not production:** authorize itself is unauthenticated (any pod that can reach :8000 can ask for a JWT), audit is a tmp file, kill-switch dies on pod restart, NetworkPolicy does not force all egress through GPIS, JWT is HS256 (shared secret), Jira is a string heuristic, SECURITY/DEPLOYMENT/OPERATIONS still bypass YAML.

```
Target production loop

Agent  --mTLS-->  GPIS (3 replicas)
                     | hash cache (Redis)
                     | simple_rules.yml
                     | optional small/large model
                     |-- JWT (RS256, short TTL)
                     |-- audit-trail --> SIEM + object store
                     |-- budget / suspend --> Redis
Agent uses JWT on downstream calls; NetworkPolicy denies everything else.
```

---

## Phase 0 — Prove the kernel (1 week)

Do this before any “scale” work. If CI is red, production talk is fiction.

1. Run `pytest tests/unit tests/qa_scenarios -v` in CI on every PR. Fix failures from `4bcfc84`.
2. Add a GitHub Actions job: schema validate + `scripts/kill-switch-validator.py` with test secrets.
3. Secret scan (TruffleHog / push protection) so SEC-001 cannot regress.
4. Document local run: `GPIS_JWT_SECRET`, `GPIS_ADMIN_API_KEY`, `GPIS_URL`, `JIRA_CR_ID`.

**Exit:** green CI on master; kill-switch e2e script passes.

---

## Phase 1 — Production kernel (3–4 weeks)  [Lane B]

Make GPIS a service you can trust, not a prototype that writes `/tmp`.

| ID | Work | Why |
|----|------|-----|
| 1.1 | **Caller auth on `/api/v1/authorize`** — mTLS (cert-manager) or per-agent API key mapped in CMDB. Admin key is not enough. | Today any client on the network can mint JWTs. |
| 1.2 | **RS256/ES256 JWT** — GPIS signs with private key; `/verify` and agents use public key. Rotate via ExternalSecret. | HS256 forces every agent to hold the signing secret. |
| 1.3 | **Redis for budget + suspensions** | In-memory kill-switch resets on every rollout. |
| 1.4 | **Durable audit** — write the same `audit-trail.json` record to object store (S3/MinIO) **and** `otel-siem-emitter.py`. Fail closed if emit fails (already true). | Files on one pod are not AU-2 evidence. |
| 1.5 | **Wire `validate-jira-approval.py` PKI** into authorize for Tier 3/4. Remove the `denied`/`expired` substring check. | Auditors will fail the heuristic. |
| 1.6 | **Per-`agent_id` rate limit** (10/min) on top of 100/min IP. Payload 2KB already exists. | SEC-003 remainder. |
| 1.7 | **Move SECURITY / DEPLOYMENT / OPERATIONS into `simple_rules.yml`** with allow+deny tests; keep Python as a deprecated shim. | Lane A iteration must hit every category. |
| 1.8 | **Enforce `tool-registry.yml` on the authorize/tool path** (PPSM-002), not only `GovernanceRouter.execute_tool()`. | Agents can still call FQDNs if they skip the router. |

**Do not** import `GovernanceRouter` as a Gemini cache classifier in front of YAML (TOKEN-003). Hash cache → YAML → small model → large model only after 1.1–1.4.

**Exit:** two GPIS pods, Redis down → `/ready` is 503; suspend survives restart; audit events in SIEM; forged HS256 tokens fail.

---

## Phase 2 — Cluster runtime (3–4 weeks)  [Lane C]

Put the kernel on Kubernetes so bypass is a network failure, not a code comment.

| ID | Work | Why |
|----|------|-----|
| 2.1 | Dedicated Helm release for **GPIS** (not mixed with a generic agent chart): 3 replicas, PDB, HPA, ClusterIP only. | PDP must outlive any one agent. |
| 2.2 | **ExternalSecrets** for `GPIS_JWT_SECRET` / signing keys / `GPIS_ADMIN_API_KEY`. No K8s Secret YAML in git. | Matches SEC-001 remaining Helm action. |
| 2.3 | **NetworkPolicy default-deny** per namespace. Allow: DNS; agent → GPIS:8000; GPIS → Redis, Jira, SIEM. Deny agent internet except via a GPIS tool proxy. | App-layer GPIS call is skippable without this. |
| 2.4 | **PSS `restricted`**, non-root 65534, read-only rootfs, drop ALL caps (K8S-003). Pin images by digest + Trivy in CI (K8S-001). | FedRAMP/SOC2 hygiene even if ATO is later. |
| 2.5 | **Prod overlay** (`deploy/kustomize/overlays/prod` or `values-eks.yaml`) with real probe paths, resource requests, `ENVIRONMENT=production`. | Dev values must not ship. |
| 2.6 | **Downstream JWT check** — IT-Ops deploy / Security scan / training job attach `Authorization: Bearer` and a sidecar or API gateway calls `/api/v1/verify`. | Token on the agent is useless if APIs ignore it. |

**Exit:** `kubectl` delete GPIS pod → agents fail closed; agent cannot curl the internet; images have no CRITICAL CVEs.

---

## Phase 3 — Operate at scale (2–3 weeks)  [Lane C]

| ID | Work |
|----|------|
| 3.1 | Prometheus `/metrics` on GPIS: `governance_decision_total{outcome,agent,category}`, `authorize_latency_seconds`, `audit_emit_failures_total`, `cache_hit_rate`. |
| 3.2 | Grafana dashboard (UI-001): allow/deny/escalate, budget, kill-switch events. |
| 3.3 | Alerts: deny spike, audit emit fail, budget 80/95/100, replica < 2, Redis down. |
| 3.4 | W3C `traceparent` through GPIS and agents (OTEL-001). |
| 3.5 | Runbooks: suspend agent, rotate signing key, restore from audit store (`workflows/incident-response/`). |

**Exit:** on-call can suspend an agent and see the deny in Grafana without SSH.

---

## Phase 4 — Token efficiency (only after Phases 1–2)  [Lane B]

Keep 0-LLM YAML as the default. Then:

1. Deterministic Redis cache key (`config/cache_config.yml` format). Initialize `self.cache` (today it can AttributeError).
2. YAML miss → small model **intent only**.
3. No-rule / `escalate: true` → large model, then **human-gated** distill into `simple_rules.yml`.
4. `benchmark_token_savings.py` reads live Prometheus, not assumed 60/35/5 mix.

**Exit:** ≥70% of authorize calls are cache or YAML; live JSON report, not the 2025 spreadsheet.

---

## Phase 5 — Compliance overlay (parallel, not blocking commercial prod)  [Lane A]

Do this if the buyer is FedRAMP/DoD. Do **not** block Phase 2.

- COMP-001: FIPS/KMS evidence (SC-28), close the POA&M that maps to **running** GPIS controls first (AU, AC, IA).
- COMP-002: SOC 2 CC6/CC7 mapped to GPIS audit + kill-switch + CI.
- PAT-001: claim-to-file map now that emit exists.
- PPSM registry `verified: true` only after NetworkPolicy matches the YAML.

---

## What not to do in the next 90 days

- Do not put the Unified Framework v3.0 into a Governance Agent system prompt.
- Do not auto-apply NL-authored policies (v3.0 PatternLearner stays human-gated).
- Do not treat CMDB Mongo / eMASS mock as the PDP.
- Do not claim 90% token savings or 152 ZTOM until Phase 4 metrics and Phase 2 NetworkPolicy exist.
- Do not expose GPIS on a public LoadBalancer.

---

## Suggested 12-week sequence

| Weeks | Phase | Owner skill |
|-------|-------|-------------|
| 1 | Phase 0 CI green | QA + platform |
| 2–5 | Phase 1 kernel | GPIS / SA |
| 5–8 | Phase 2 cluster | Platform / K8s |
| 8–10 | Phase 3 observe | SRE |
| 10–12 | Phase 4 tokens (optional) | GPIS |
| Ongoing | Phase 5 evidence | Compliance |

Staffing that matches the code: one person on GPIS (B), one on Helm/NetworkPolicy (C), policy YAML (A) in the same PRs as tests.

---

## Product Manager & Compliance Review Guidance (2026-09-19)

Full review artifact: [docs/reviews/pm_review_production_scale_plan.md](reviews/pm_review_production_scale_plan.md) (Status: **Approved with Strategic Guidance**).

### Enterprise Value Proposition & Buying Persona
- **Target Buyer:** CISO, VP of Platform Engineering, Head of AI/ML.
- **Customer Need:** Eliminate fear of autonomous agents executing destructive actions or leaking credentials in production.
- **Core Value:** Transforming GPIS into an auditable, durable, multi-replica fail-closed gate with an instant survivable kill-switch.

### ⚠️ PM Blind Spots & Risk Mitigations
1. **Downstream PEP Adoption Friction (Phase 2.6):** A token issued by GPIS is ineffective if downstream services don't validate it. Deliver turn-key PEP integrations (Envoy/Traefik sidecar, Istio `RequestAuthentication`) and keep `agents/shared/gpis_client.py` zero-friction with automatic token fetching and retries.
2. **High Availability & Fail-Closed Blast Radius (Phase 2.1):** Fail-closed for Tier 3/4 write operations is mandatory, but Tier 1 read operations require 99.99% availability. Enforce 3 replicas, PDB (`minAvailable: 2`), topology spread constraints, and strict readiness probe contracts.
3. **Developer Experience (DevX) & Local Testing:** If mTLS and PKI require complex setup locally, developers will bypass GPIS. Provide `make dev-up` with self-signed test certs and mock keys for instantaneous local testing loops.

---

## First PR after this plan (Milestone 1)

Phase 1.1 + 1.3 together: **authenticate authorize** and **persist suspensions in Redis**. That is the smallest change that turns “agents call GPIS in happy path” into “agents cannot skip GPIS after a restart or from a random pod.”

### Milestone 1 Acceptance Criteria (Definition of Done):
- [ ] Any call to `/api/v1/authorize` without a registered caller identity (mTLS SAN or CMDB-mapped API key) returns `401 Unauthorized`.
- [ ] A kill-switch suspension issued via `/admin/v1/suspend/{agent_id}` is written to Redis with TTL/persistence.
- [ ] When the GPIS pod is deleted (`kubectl delete pod`) and restarted, previously suspended agents remain suspended (DENIED) on restart.
- [ ] End-to-end integration test passes in CI without manual environment intervention.
