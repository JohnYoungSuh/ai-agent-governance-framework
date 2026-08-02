---
trigger: always_on
---

# Agent Post-Goal Execution Validation & Documentation Rules

This rule defines the mandatory checklist that must be executed after any `/goal`, major feature, version bump, or compliance update. The agent must verify and synchronize documentation, tests, schemas, and configuration before completing work.

---

## 📋 Post-Goal Checklist & Update Targets

Whenever a new capability, compliance control, or production deployment is completed:

### 1. README Update (`README.md`)
- **What's New**: Add new capabilities to the "What's New" section
- **Feature List**: Update compliance status table (FedRAMP %, SOC 2 status)
- **Documentation Links**: Add links to any new docs under the appropriate category
- **Quick Start**: Update if new setup steps are required

### 2. NEXT_RELEASE_TODO.md
- Mark all completed items `[x]` with resolution date
- Add a new session entry to `## 📍 Session Log` (terse, 1-2 lines per item)
- Move any items discovered during implementation to appropriate priority tier

### 3. LESSONS_LEARNED.md
- If the session exposed a new root cause type, add a `## 📌 LL-NNN` entry
- Each entry must include: date, file, root cause, diagnostic playbook, and rule added
- Update agent rule files if the lesson changes how the agent should behave

### 4. Schema Validation (`policies/schemas/`)
- Run `pytest tests/compliance/test_schemas.py -v` — all 3 schemas must pass
- If schema changed: update all emitters (`otel-siem-emitter.py`) and validators
- If agent-manifest schema changed: re-validate all `agents/*/config/` YAML files

### 5. Security Documentation (`SECURITY.md` or equivalent)
- Update if any new secrets management patterns were added
- Ensure TruffleHog and pip-audit instructions are current
- If new CVE fixes were applied, document in CHANGELOG.md

### 6. Compliance Controls (`policies/control-mappings.md`)
- For every new feature, add or update the NIST 800-53 control mapping
- Update the SSP control count in `README.md` if controls were implemented
- Update `compliance/ssp/control-summary.md` if implementation status changed

### 7. Kubernetes/Helm Validation
- Run `helm lint deploy/helm/ai-agent/` — must pass 0 warnings
- If values files changed: run `helm template` and inspect output
- Run `kubectl apply --dry-run=server` against current kubeconfig if available

### 8. Token Efficiency Check
- Run `python3 scripts/benchmark_token_savings.py --format json`
- Target: ≥70% token reduction in conservative scenario
- If GovernanceRouter was changed: verify cache hit rate calculation is correct

### 9. Docker Container, Volume & Image Cleanup
- **Container Hygiene**: Automatically stop and remove all temporary test containers (`docker rm -f <test-container>`).
- **Build Cache Prune**: Execute `docker builder prune -f` after container builds to reclaim multi-GB build cache.
- **Dangling Artifact Prune**: Remove unused dangling images (`docker image prune -f`) and orphan volumes (`docker volume prune -f`).

---

## 🚀 Execution Loop & Hygiene Verification

Before declaring a goal complete, in order:
1. **Tests pass**: `pytest tests/ -v` → 0 failures, ≥80% coverage
2. **Schemas valid**: `pytest tests/compliance/ -v` → 0 failures
3. **Linting clean**: `ruff check . && mypy app/` → 0 errors
4. **No secrets**: `trufflehog filesystem . --only-verified` → 0 findings
5. **Helm valid**: `helm lint deploy/helm/ai-agent/` → 0 warnings
6. **SIEM emitter**: `./scripts/test-siem-emitter.sh` → 10/10 pass
7. **Version sync** (if bumped): All 5 version files updated in single commit
8. **Git push**: Commit with conventional commit message, push to `master`
9. **CI green**: GitHub Actions pipeline passes — this is the final authority

---

## Token-Efficient Session Habits

From lessons learned in both AWS-DFD-Visualizer and this project:

### Start Every Session:
1. Read `SESSION_START.md` (or `.agents/rules/`) — 60-second orientation
2. Check `NEXT_RELEASE_TODO.md` for the current top-priority item
3. Check `LESSONS_LEARNED.md` for any relevant root cause patterns

### During Work:
- Use `CODEMAP.md` (when created) to find files — don't re-explore the project every session
- Apply simple_rules before escalating to LLM — same principle as the GovernanceRouter
- Stop and document when you hit a recurring pattern that's wasted >1 session

### End Every Session:
- Log session in `NEXT_RELEASE_TODO.md` `## 📍 Session Log` (terse: 1-2 lines per item)
- Run the 9-step post-goal checklist above
- Only commit after CI passes
