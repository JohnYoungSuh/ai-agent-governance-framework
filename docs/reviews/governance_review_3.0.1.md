# Governance Policy & Feature Review — v3.0.1

**Date:** 2026-09-19  
**Personas:** Product / Compliance Manager + System Architect  
**Scope:** Full-repo SA review of whether backlog items are governance/policy that AI agents can iterate, plus token-efficiency best-practice check.  
**Live code basis:** `app/main.py`, `app/policy_engine.py`, `scripts/governance_router.py`, `policies/simple_rules.yml`  
**Patent guard:** `policies/schemas/audit-trail.json` was not modified.  
**Secrets guard:** No credentials added. Residual default JWT still present (see SEC-001).

---

## Executive verdict

**Partially yes.** This repository already has a policy-as-code surface AI agents can iterate (`policies/simple_rules.yml`, tool/PPSM registries, schemas, allow+deny tests). It is **not** a closed loop where runtime agents propose, validate, and apply policy.

Most `NEXT_RELEASE_TODO.md` items are platform or PDP-kernel engineering, not policy content. The four runtime agents under `agents/` never call GPIS. Token-efficiency **design** is strong; **runtime** savings claims are modeled, not measured on the authorize path. The live PDP is actually zero-LLM today (YAML + Python), which is cheaper than the documented router — but `escalate: true` becomes DENY instead of a real complex decision.

Treat remaining work as three lanes:

| Lane | Meaning | AI agents may |
|------|---------|---------------|
| **A** | Policy-as-code | Draft YAML/docs/tests; human merge |
| **B** | PDP kernel / patent | Propose diffs only; human-gated apply |
| **C** | Platform / CI / observability | Implement as engineering, not “policy iteration” |

---

## Product / Compliance Manager review

### NIST / FedRAMP posture

- Control mappings exist in `policies/control-mappings.md` (docs-only; not loaded by the PDP).
- SSP is documented at 298/339 NIST 800-53 Rev 5 controls. Remaining work (COMP-001, FIPS SC-28) is still a FedRAMP blocker, not an agent-policy iteration task.
- Tier 3/4 Jira CR is required in `app/main.py` (lines 128–149), which aligns with AC-6 / CM-3 intent. **Gap:** `validate_jira_approval()` is a string heuristic (`denied`/`expired` in the CR id), not `scripts/validate-jira-approval.py` PKI. Auditors will not accept this as IA-5 / change-control evidence.
- Audit trail schema is present and treated as a patent anchor. **Gap:** `/api/v1/authorize` does not emit a schema-validated audit record. AU-2/AU-12 are incomplete until every decision writes one event.
- Kill-switch admin APIs exist on the same process as the PDP (`POST /admin/v1/suspend/{agent_id}`) with no authentication. That is a FedRAMP Moderate finding (AC-3, AC-6) independent of policy YAML quality.

### Business risk

| Risk | Rating | Why it matters |
|------|--------|----------------|
| Agents can be described as “governed” while they never call GPIS | High | Demo vs production gap; false ATO narrative |
| Default JWT signing key in non-production (and any unset `ENVIRONMENT`) | High | Token forgery; SEC-001 residual |
| Dual policy engines (Python legacy vs YAML) | Medium | Agents iterating YAML do not change SECURITY/DEPLOYMENT/OPERATIONS |
| 90% token-savings used as a product claim | Medium | Benchmark is a model (`scripts/benchmark_token_savings.py`); live authorize uses 0 LLM tokens and never records savings |
| PPSM registry all `DRAFT_FOR_REVIEW` / `verified: false` | Medium | ZTA paperwork exists; enforcement does not |

### What PM will accept as “agent-iterated policy”

A change is a governance policy iteration only if it:

1. States the rule in English (`policies/agent-safety-policies.md`).
2. Maps to ≥1 NIST control (`policies/control-mappings.md`).
3. Lands as a versioned `simple_rules.yml` (or tool/PPSM) entry — fail-closed.
4. Has ALLOW and DENY tests.
5. Emits a SIEM / audit outcome.
6. Passes dual-persona review and human merge.

Anything that changes JWT issuance, schema field names, or fail-open behavior is **not** an agent self-serve item.

---

## System Architect review

### Live PDP (not the docs diagram)

```
Claimed: Agent → GPIS → Cache → Intent → Simple Rules → LLM → JWT
Live:    Agent stubs (no GPIS call)
         POST /api/v1/authorize
           → budget PIP (Redis optional)
           → in-memory SUSPENSIONS
           → Tier 3/4 jira_cr_id heuristic
           → evaluate_request()
                SECURITY|DEPLOYMENT|OPERATIONS → Python functions
                CREATE|MODIFY|DELETE|ACCESS|COMPLY → simple_rules.yml lookup
           → HS256 JWT on allow
         scripts/governance_router.py is never imported by app/main.py
```

**Endpoints** (`app/main.py`): `POST /api/v1/authorize` (96–190), `GET /api/v1/verify` (192–202), `GET /health` (204–206), `GET /ready` (208–210, always ready), suspension/admin (212–234).

**JWT claims issued:** `sub`, `category`, `authorized`, `tier`, `namespace`, `jira_cr_id`, `budget_status`, `exp` (tier TTL 15m / 5m / 2m). Missing vs GPIS-003 writeup: `guardrails_enforced`.

**Helm probe mismatch (GPIS-004 residual):** `deploy/helm/ai-agent/values.yaml` probes `/health/live` and `/health/ready`. GPIS serves `/health` and `/ready`. Ready never checks Redis, policy file, or LLM clients.

### Policy artifacts agents can iterate (Lane A)

| Artifact | Runtime? | Notes |
|----------|----------|--------|
| `policies/simple_rules.yml` (19 keys) | Yes, 5-category path | Copied into GPIS image. Conditions only partially evaluated (tier strings, production namespace, `escalate`). Path/quota/backup ignored. |
| `policies/tool-registry.yml` | Router only | Not used by `app/main.py`. |
| `policies/ppsm/*` | Schema tests only | All entries draft. |
| `policies/v3/*` (Rego, action-tier-rules) | Docs/template | Not imported. |
| `policies/schemas/*` except `audit-trail.json` structure | CI validate | New schemas OK; do not rename AGT required fields. |
| `frameworks/governance-framework.yaml` | Gatekeeper scripts | Not GPIS. |

**YAML `escalate: true` bug:** `policy_engine.py` 111–112 returns DENY (“escalates to large model”) and does **not** call an LLM. Production MODIFY/DELETE and secrets access cannot actually escalate.

**Legacy vs YAML:** Iterating `simple_rules.yml` does not change CVE patch, unsigned-commit, or maintenance-window logic. Those remain Python in `evaluate_security_patch_deployment`, `evaluate_deployment`, `evaluate_operations`.

### Standing guards (this review)

| Guard | Status |
|-------|--------|
| Patent — `audit-trail.json` intact | Pass (not modified). Emit-on-authorize still missing. |
| Token efficiency — new rules in `simple_rules.yml` | Pass as SOP. Live authorize does not use the Cache→Intent→LLM stack. |
| Zero secrets | Fail residual. `SECRET_KEY = os.getenv("GPIS_JWT_SECRET", "dev-gpis-jwt-secret-key-change-in-prod")` (`app/main.py` 17–19). Fail-closed only if `ENVIRONMENT == "production"`. |

### PDP / K8s / JWT impact of Lane A vs B

- Lane A YAML changes: **no** JWT claim change, **no** NetworkPolicy change, **zero** extra tokens on the live authorize path (lookup only).
- Wiring `GovernanceRouter` into `/authorize` (GPIS-001): **does** change PDP latency and token cost; must preserve fail-closed and never skip cache→rules before LLM.
- K8s NetworkPolicy / PSS / Conjur: Lane C; do not encode those as `simple_rules.yml` keys.

### Closed-loop gaps (why agents cannot iterate policy in production)

1. Runtime agents do not call GPIS.
2. Dual engines: YAML iteration misses legacy categories.
3. YAML conditions only partially evaluated.
4. Authorize does not emit audit-trail (patent loop incomplete).
5. PatternLearner / NL authoring / distillation queue are roadmap.
6. This skill had never produced a `governance_review_*.md` before this file.
7. `scripts/validate-manifest.py` is referenced in rules and still absent (CMDB-002).
8. Test pyramid dirs `tests/unit`, `tests/integration`, `tests/compliance` are documented but not populated; only `tests/qa_scenarios/` exists.

---

## Token efficiency — are we using AI-agent best practices?

**Short answer:** The **playbook** is best-practice. The **hot path does not run it**. Coding-agent context hygiene is only partly in place. Do not quote 90.25% savings as a measured production result.

### What “good” looks like (governance + coding agents)

| Practice | Why it saves tokens | This repo |
|----------|---------------------|-----------|
| Deterministic cache key **before** any model | 0 tokens on repeats | Configured in `config/cache_config.yml`; `GovernanceRouter` references `self.cache` without initializing it (`scripts/governance_router.py` ~230) — AttributeError on cacheable fallback. Live GPIS has no decision cache. |
| YAML / policy lookup before LLM | 0 tokens for known intents | Live GPIS does this for 5-category keys. Best part of the system. |
| Small model only to classify **unstructured** text | Cheap intent, not cache oracle | Documented Cache Classifier is a Gemini call (~100–300 tokens) **before** rules. That is weaker than hash lookup. Prompts are long (`scripts/prompts/cache_classifier.txt` is hundreds of lines, not a 100-token prompt). |
| Large model last, then distill to YAML | Pay once, never again | Distillation prompt exists; `policies/distilled_rules/` does not. `auto_distill` in `config/token_router.yml` is config-only. |
| Persistent cache (Redis) | Survive rollouts | Budget PIP may use Redis; decision cache remains memory/`{}`. TOKEN-002 still open. |
| Budget PIP / kill switch | Cap waste | Budget map in `app/main.py` 45–50; Redis optional. Kill switch is in-memory, unauthenticated. |
| Compact agent orientation (CODEMAP / SESSION_START / .agentignore) | Coding agents do not ingest build artifacts and duplicate docs | `.agentignore` and `CODEMAP.md` exist. `SESSION_START.md` still missing (DOC-001). `.agents/rules/project-knowledge.md` still lists LL-001/LL-002 as open P0s — wasted re-investigation. |
| Do **not** stuff the entire framework into a system prompt | Context tax every turn | `docs/GOVERNANCE-AGENT-ARCHITECTURE.md` still proposes the Unified Framework v3.0 as the Governance Agent system prompt. That contradicts the token-router design. |
| Measure, don’t model | Claims need production metrics | `scripts/benchmark_token_savings.py` uses assumed mix (60% cache / 35% rules / 5% large). `reports/token-savings-evaluation.json` is 2025-10-23 modeled ops (config load, docs sync) — not GPIS authorize. No Prometheus `token_usage_total` on GPIS. |
| Fail to rules, not to a mock LLM that looks live | Avoid silent cost and silent policy drift | Router instantiates Gemini/Anthropic if keys exist, else keyword fallbacks. Conjur can return `mock-ephemeral-conjur-token-value`. |

### Live vs claimed token cost (authorize)

| Path | Tokens per authorize | Status |
|------|----------------------|--------|
| Documented weighted average | ~195 vs 2000 baseline (90.25% “savings”) | Model only |
| Live GPIS 5-category hit in `simple_rules.yml` | 0 LLM tokens | Real |
| Live GPIS legacy SECURITY/DEPLOYMENT/OPERATIONS | 0 LLM tokens | Real (Python, not policy-as-code) |
| Live GPIS `escalate: true` | 0 LLM tokens, **DENY** | Real, wrong product behavior |
| `GovernanceRouter.process_request` with keys | Classifier ± router ± Opus | Not on PDP |
| Coding session reading `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md` (~1700 lines) + Unified v3.0 + patents | Large context every review | Anti-pattern for IDE agents |

### Best-practice gaps to close (priority order)

1. **Keep 0-token YAML on the PDP** as the default. Do not insert a small-model cache classifier in front of a deterministic key. Hash/key lookup first; LLM only on miss + no rule.
2. **Wire router after that order** (GPIS-001) and initialize `self.cache` (or Redis). Fix the AttributeError.
3. **Migrate legacy Python rules into `simple_rules.yml`** so Lane A iteration covers SECURITY/DEPLOYMENT/OPERATIONS (LL-002 already showed why policy-in-code is dangerous).
4. **Evaluate YAML conditions for real** (path, quota, backup). Partial string matching wastes later LLM escalations and produces false ALLOWs.
5. **Emit `tokens_used` + audit-trail on every decision** so the 70% benchmark gate is empirical.
6. **For Cursor/IDE agents:** add `SESSION_START.md`; shrink always-on rules; stop pointing agents at the 1700-line implementation guide as first read; fix stale P0s in `project-knowledge.md` / `.cursorrules`.
7. **Do not ship “Governance Agent with full framework in the prompt.”** Point that agent at `simple_rules.yml` + CODEMAP instead.

Token Guard for this review: no new policy was added outside YAML-capable files; no claim is made that GPIS-001 is done.

---

## Backlog classification (every open / stale item)

### Closed in live code (keep in session log; do not re-implement)

| ID | Evidence | Caveat |
|----|----------|--------|
| SEC-002 | `evaluate_security_patch_deployment` requires `action == emergency_patch` | Keep both allow+deny tests |
| GPIS-003 (mostly) | JWT `tier`, `namespace`, `jira_cr_id`, TTL, `/verify` | Missing `guardrails_enforced` |
| GPIS-004 (partial) | `/health`, `/ready` exist; Helm values have probes | Path mismatch `/health/live` vs `/health`; `/ready` is a stub |
| K8S-002 | `deploy/helm/ai-agent/templates/networkpolicy.yaml` | Per-agent allow lists still worth review |
| DOC-001 CODEMAP | `CODEMAP.md` exists | SESSION_START still missing |
| PPSM-001 files | `policies/ppsm/ppsm-registry.yml`, schema, tests | Draft status; not loaded by PDP |
| KILL-001 skeleton | Admin suspend/approve + `scripts/kill-switch-validator.py` | Unauthenticated admin API |

### Lane A — policy-as-code (agents draft; human merge)

- **PPSM-002** — keep `tool-registry.yml` as the source of truth; do not hardcode FQDNs in Python.
- **GUARD-001** — allow+deny tests for guardrails 13–16.
- **AUDIT-001** — validate emit against existing schema; **do not** change required fields.
- **COMP-001 / COMP-002** — mappings and evidence templates.
- **GT-001** — proposal → Pareto validator → human queue (policy proposals, not kernel).
- **PAT-001** — claim-to-file map (docs).
- **GPIS-002 remainder** — express remaining behaviors as YAML; retire Python conditionals once tests pass.
- **v3.0 NL authoring / PatternLearner** — draft rules only; never auto-apply.

### Lane B — PDP kernel (human-gated)

- **SEC-001 residual** — remove default JWT; fail closed whenever secret missing.
- **SEC-003 remainder** — payload size cap; mTLS or API key on `/authorize` and **all `/admin/*`**.
- **GPIS-001** — import router into authorize **after** deterministic cache + YAML; never skip levels.
- **TOKEN-001** — real clients with fail-to-rules (not fail-open mock allow).
- **KILL-001 auth** — authenticate admin; persist suspensions.
- **Jira PKI** — call `validate-jira-approval.py`, not substring checks.
- **Authorize audit emit** — one `audit-trail.json` record per decision.
- **`audit-trail.json` structure** — counsel only.

### Lane C — platform (not policy iteration)

- SEC-005 Conjur (sidecar template is a stub comment).
- K8S-001, K8S-003, K8S-004, K3S-001.
- CMDB-001 MCP sidecar (Mongo CMDB code exists under `cmdb/`; not wired to GPIS).
- CMDB-002 `validate-manifest.py`.
- TOKEN-002 Redis decision cache.
- OBS-001, OTEL-001, UI-001, CI-001, IR-001, PAR-001, COST-001, DOC-002.

---

## Recommended next execution (after this review)

Highest leverage for “AI agents iterate governance”:

1. SEC-001 residual (fail-closed JWT).
2. Emit audit-trail from authorize (patent + AU family).
3. Authenticate admin/kill-switch.
4. Full YAML condition evaluation + migrate legacy Python rules into `simple_rules.yml` with allow+deny tests.
5. Agents call GPIS before side effects.
6. Only then wire GovernanceRouter: **hash cache → simple_rules → small intent model → large model → distill**.

---

*Generated by the governance-policy-review skill. Dual-persona. No PDP or patent-schema mutations in this change.*
