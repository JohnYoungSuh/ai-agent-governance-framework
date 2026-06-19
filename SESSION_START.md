# Session Start — K8S AI DevSecOps Agent Governance Framework

> **Read this in 60 seconds. Then open `NEXT_RELEASE_TODO.md` and start working.**

---

## What This Project Is
An enterprise **AI Agent Governance Framework** (v2.1) for deploying and managing AI agents on Kubernetes with FedRAMP Moderate compliance. The core innovation is the **Atomic Governance Transaction (AGT)** system — a patent-pending mechanism that makes every agent action auditable, authorized, and compliant.

## The 3 Files You Must Read First
1. `LESSONS_LEARNED.md` — Root causes from past sessions. Read BEFORE debugging anything.
2. `NEXT_RELEASE_TODO.md` → `## 📍 Session Log` — What was done last session.
3. `NEXT_RELEASE_TODO.md` → First unchecked 🔴 item — Your task for this session.

## The Architecture in 30 Seconds
```
Agent Request
    ↓
GPIS (app/main.py) ← The ONLY Policy Decision Point
    ↓
GovernanceRouter (scripts/governance_router.py)
    ↓ Cache hit → 0 LLM tokens
    ↓ Simple rules → 0 LLM tokens
    ↓ Complex → Claude Sonnet (~600 tokens)
    ↓
JWT Token (short-lived, tier-stamped)
    ↓
Agent executes + emits audit event
    ↓
SIEM (Splunk/Datadog/CloudWatch via OTLP)
```

## Known P0 Issues (Fix These First)
1. **`app/main.py` line 11** — Hardcoded JWT secret. Replace with `os.getenv("GPIS_JWT_SECRET")`. See LL-001.
2. **`app/policy_engine.py` line 30** — CVE > 9.0 → APPROVED logic is ambiguous. See LL-002.
3. **`scripts/governance_router.py`** — LLM clients are mock stubs. See LL-003.

## Key Commands
```bash
pytest tests/ -v                          # Run all tests
ruff check . && mypy app/                 # Lint + type check
./scripts/test-siem-emitter.sh           # SIEM validation (10/10 must pass)
python3 scripts/benchmark_token_savings.py --format json  # Token efficiency
helm lint deploy/helm/ai-agent/          # Helm validation
```

## Compliance Numbers to Know
- **NIST 800-53**: 298/339 controls (88%) — target 100%
- **Patent anchor**: `policies/schemas/audit-trail.json` — DO NOT CHANGE SCHEMA
- **16 guardrail rules** in `GOVERNANCE_GUARDRAILS.md`
- **4 agent tiers**: Observer, Developer, Operations, Architect

## Rule: Never Repeat a Cosmetic Fix
Before closing any bug, ask:
1. Is the fix data-driven? (Not hardcoded)
2. Are all copies/files updated?
3. Was the output verified? (Test passing, SIEM emitting, Prometheus metric showing)
