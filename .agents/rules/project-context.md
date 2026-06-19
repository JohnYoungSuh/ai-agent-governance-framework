---
# AI Agent Governance Framework — Claude Project Context
# Zero Trust Policy Framework: PEP | PIP | PDP | PAP | PE | PA
# Token-efficient layered context. Read top-to-bottom. Stop when you have enough context for your task.
---

## 🎯 Quick Identity (30 seconds)

**Project:** AI Agent Governance Framework v2.1 — K8S AI DevSecOps Agent  
**Purpose:** Enterprise governance for AI agents on Kubernetes with FedRAMP Moderate + NIST SP 800-207 Zero Trust compliance  
**Core Innovation:** Atomic Governance Transaction (AGT) — patent-pending system for auditable, authorized agent operations  
**Start here:** `SESSION_START.md` → `NEXT_RELEASE_TODO.md` → `LESSONS_LEARNED.md`

---

## 🔴 P0 Bugs (Fix Before Anything Else)

| ID | File | Issue |
|----|------|-------|
| LL-001 | `app/main.py:11` | **Hardcoded JWT secret** — replace with `os.getenv("GPIS_JWT_SECRET")` |
| LL-002 | `app/policy_engine.py:30` | **CVE > 9.0 → APPROVED** — ambiguous policy logic, needs intent clarification |
| LL-003 | `scripts/governance_router.py` | **LLM clients are mock stubs** — not wired to any real API |

---

## 🏗️ Zero Trust Architecture — Full Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZERO TRUST CONTROL PLANE                     │
│                                                                 │
│  PA (Policy Administrator)          PAP (Policy Admin Point)    │
│  ┌──────────────────────────┐       ┌─────────────────────┐    │
│  │ Human operator           │       │ GPIS admin API      │    │
│  │ Jira CR approver         │──────▶│ simple_rules.yml    │    │
│  │ Kill-switch PA approver  │       │ policies/ editor    │    │
│  └──────────────────────────┘       └────────┬────────────┘    │
│                                              │                  │
│  PDP (Policy Decision Point)    PE (Policy Engine)             │
│  ┌──────────────────────────────┐  ┌────────────────────────┐  │
│  │ GPIS (app/main.py)           │  │ GovernanceRouter       │  │
│  │ POST /api/v1/authorize       │──▶│ Cache → SimpleRules   │  │
│  │ Issues signed JWTs           │  │ → Gemini Flash         │  │
│  │ Tier 1: 15min TTL            │  │ → Claude Sonnet        │  │
│  │ Tier 4: 2min TTL + PA human  │  │ → Distillation Queue  │  │
│  └──────────────────────────────┘  └────────────────────────┘  │
│                                                                 │
│  PIP (Policy Information Point)                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ CMDB (agent manifests)  │ Prometheus metrics             │   │
│  │ K8s RBAC               │ CyberArk/AWS SM (identity)     │   │
│  │ GitHub secret scanning  │ NIST NVD (CVE feeds)          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │ JWT (signed, tier-stamped)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ZERO TRUST DATA PLANE                        │
│                                                                 │
│  PEP (Policy Enforcement Points)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ K8s Network  │  │ JWT Middleware│  │ CyberArk Conjur    │   │
│  │ Policy (L4)  │  │ (per-agent)  │  │ Sidecar (identity) │   │
│  │ Egress tiers │  │ mTLS verify  │  │ Ephemeral tokens   │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
│                              │                                  │
│              ┌───────────────┼───────────────┐                 │
│              ▼               ▼               ▼                 │
│        Security Agent   IT-Ops Agent    Architect Agent        │
│        (Tier 2)         (Tier 3)        (Tier 4)               │
│              │               │               │                 │
│              └───────────────┼───────────────┘                 │
│                              ▼                                  │
│                    Append-Only Audit Trail                      │
│                    (SIEM via OTLP/OpenTelemetry)                │
└─────────────────────────────────────────────────────────────────┘
```

### Zero Trust Component → File Mapping

| ZT Component | Role | Primary File | NIST 800-207 §Ref | Controls |
|---|---|---|---|---|
| **PDP** | Policy Decision Point | `app/main.py` `/api/v1/authorize` | §4.1 | AC-3, AC-6 |
| **PE** | Policy Engine | `scripts/governance_router.py` + `policies/simple_rules.yml` | §4.1 | SI-2, AC-24 |
| **PAP** | Policy Administration | `app/admin_api.py` (planned) + `policies/` editor | §4.2 | CM-3, CM-6 |
| **PEP** | Enforcement at Agent | K8s NetworkPolicy + JWT middleware + CyberArk sidecar | §4.3 | SC-7, AC-17 |
| **PIP** | Policy Information | CMDB + Prometheus + K8s RBAC + AWS SM/Conjur + CVE feeds | §4.4 | AU-2, RA-5 |
| **PA** | Policy Administrator | Human operator via Jira CR + Slack kill-switch approval | §4.5 | AC-5, PE-2 |

---

## 🔑 Secretless Brokerage — Ephemeral Credential Flow

```
Agent Pod Start → K8s ServiceAccount Token (audience=conjur, TTL=900s)
    → CyberArk Conjur Sidecar validates (namespace + SA + image hash)
    → GovernanceRouter._fetch_ephemeral_credential() [in-memory only]
    → Agent executes with ephemeral token (NEVER stored to disk/env)
    → Pod terminates → Conjur session auto-invalidated
```

**No static K8s Secrets for LLM API keys, JWT secrets, or DB credentials.**  
Fallback for EKS: AWS Secrets Manager + IRSA (IAM Roles for Service Accounts).

---

## 🌐 Egress Tier Model (NetworkPolicy)

| Tier | Destination | Protocol | Who Can Access | Threat Mitigated |
|------|------------|----------|---------------|-----------------|
| **T1** | CyberArk/Vault (internal) | mTLS gRPC | All agent pods | Credential theft |
| **T2** | GPIS `:8000` (internal) | mTLS HTTPS | All agent pods | Unauthorized action |
| **T3** | LLM APIs (external via proxy) | HTTPS/proxy | GovernanceRouter pod only | Prompt injection exfiltration |
| **DENY** | All other egress | — | All pods | Lateral movement, C2 |

> **Prompt Injection + Exfiltration Defense:** An agent compromised via prompt injection cannot POST a checked-out Conjur token to `attacker.com` — direct external egress is blocked. The only external path is via the LLM proxy, which strips credential-pattern strings from outbound payloads.

---

## 📋 Agent Tier System

| Tier | Role | Environments | JWT TTL | Requires |
|------|------|-------------|---------|---------|
| 1 | Observer | All (READ-ONLY) | 15 min | GPIS JWT |
| 2 | Developer | Dev only | 10 min | GPIS JWT + confirmation |
| 3 | Operations | Dev+Staging; approved prod | 5 min | GPIS JWT + Jira CR |
| 4 | Architect | Design + approved | 2 min | GPIS JWT + Jira CR + human PA |

---

## ⚖️ Governance Principles (NEVER Violate)

1. **GPIS = Single PDP** — one policy decision point for all agents
2. **Audit trail = Append-only** — immutable, schema-validated, emits on every decision
3. **Tier 3/4 = Jira CR required** — no JWT without validated `jira_cr_id`
4. **Secrets = Conjur/IRSA only** — `os.getenv()` for non-sensitive config only; credentials via GovernanceRouter checkout
5. **Patent schema = frozen** — `policies/schemas/audit-trail.json` structure is immutable
6. **Token router = ordered** — Cache → Simple Rules → LLM, never skip levels
7. **Kill switch = human PA** — automated suspend, human-approved revoke

---

## 🔑 Key Commands

```bash
pytest tests/ -v                                          # All tests (0 failures)
python3 scripts/qa-agent.py --env dev                     # QA score ≥ 80
python3 scripts/qa-agent.py --env staging                 # QA score ≥ 90
python3 scripts/qa-agent.py --env prod                    # QA score ≥ 95
ruff check . && mypy app/                                 # Lint + type check
./scripts/test-siem-emitter.sh                            # SIEM 10/10
helm lint deploy/helm/ai-agent/ -f deploy/helm/ai-agent/values-k3s.yaml
helm lint deploy/helm/ai-agent/ -f deploy/helm/ai-agent/values-eks.yaml
./scripts/compliance-check-enhanced.sh                   # 12 AWS checks
```

---

## 📏 Compliance Numbers

- NIST 800-53 Rev 5: **298/339 (88%)** — target 100% for FedRAMP
- NIST SP 800-207 Zero Trust: 6/6 components mapped (PEP/PIP/PDP/PAP/PE/PA)
- NIST AI RMF: ✅ Complete
- FedRAMP Moderate: 📋 Ready for 3PAO
- SOC 2 Type II: 🔄 Target 2026 Q2
- 16 guardrails, 18 AI risks, 21 mitigation controls

---

## 🏁 Session Checklist (Every Session)

**Start:** `SESSION_START.md` → `NEXT_RELEASE_TODO.md` top item → `LESSONS_LEARNED.md`  
**End:** Check `[x]` → log `## 📍 Session Log` → `python3 scripts/qa-agent.py --env dev` → push → CI green

---

## 🔗 Extended Context (Load Only If Needed)

| Topic | File |
|-------|------|
| Full agent rules | `.agents/rules/` (8 rule files) |
| Zero Trust component details | `policies/ppsm/zero-trust-components.md` |
| CyberArk integration | `policies/ppsm/cyberark-integration.md` |
| PPSM port registry | `policies/ppsm/ppsm-registry.yml` |
| K3s vs K8s decision | `docs/K3S-VS-K8S-DECISION.md` |
| Token efficiency guide | `docs/TOKEN-EFFICIENT-IMPLEMENTATION.md` |
| Patent application | `docs/US-PATENT-APPLICATION.md` |
| Patent evidence (RTP) | `docs/archive/VERIFICATION-EVIDENCE.md` |
