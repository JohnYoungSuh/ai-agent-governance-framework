---
trigger: always_on
---

# IDE-Agnostic Rules — Gemini, Cursor, Copilot, Windsurf

These rules are loaded by any AI coding assistant to maintain consistent coding guidelines, architecture constraints, and quality standards across all IDE integrations.

> [!IMPORTANT]
> **IDE-Agnostic Mirroring Rule**: If any major architectural, security, testing, or governance rules in `.agents/rules/` are changed, those changes **MUST** be mirrored to `.cursorrules` in the project root to keep the project accessible across all AI assistants.

---

## 🏛️ Key Architectural Decisions

1. **GPIS is the Single PDP**: `app/main.py` is the ONLY policy decision point. Agents do NOT self-authorize. Every Tier 2+ operation requires a GPIS JWT.

2. **Token Router Hierarchy is Sacred**: Requests flow Cache → Intent Router → Simple Rules → Large Model. Never skip levels. The 90% token savings target depends on this order.

3. **Audit Trail Schema is a Patent Anchor**: `policies/schemas/audit-trail.json` field structure must not change without patent counsel review. Every governance decision emits a schema-validated event.

4. **JWT Secrets via Environment Only**: `SECRET_KEY = os.getenv("GPIS_JWT_SECRET")`. No exceptions. See LL-001 in `LESSONS_LEARNED.md`.

5. **Python Policy Files Over Hardcoded Logic**: All governance rules go in `policies/simple_rules.yml` or `policies/agent-safety-policies.md`, not as conditionals in application code.

---

## 🔒 Security & Compliance

- **Zero Secrets in Source**: Never commit API keys, JWT secrets, passwords, or credentials. `os.getenv()` only, with startup assertions.
- **All Tests Must Pass**: `pytest tests/ -v` → 0 failures, ≥80% coverage before any commit.
- **Input Validation Required**: All GPIS endpoints validate: max 500 chars, allowlist regex, prompt injection blocking.
- **Tier 3/4 Requires Jira CR**: Never issue a Tier 3/4 JWT without validating `jira_cr_id` via `validate-jira-approval.py`.

---

## 🚀 Development Workflow

1. Check `NEXT_RELEASE_TODO.md` for the current priority item
2. Read `LESSONS_LEARNED.md` for relevant root cause patterns
3. Implement fix → run `pytest tests/ -v` → run `ruff check .` → validate schemas
4. Mark `[x]` in `NEXT_RELEASE_TODO.md` with date
5. Log session entry in `## 📍 Session Log`
6. Commit with Conventional Commits (`fix:`, `feat:`, `sec:`, `compliance:`)
7. Push → wait for green CI → done

---

## 🧪 Testing Rules

- Unit tests: `pytest tests/unit/ -v --cov=app`
- Integration tests: `pytest tests/integration/ -v`
- Schema validation: `pytest tests/compliance/ -v`
- SIEM validation: `./scripts/test-siem-emitter.sh` (10/10 must pass)
- Every new GPIS rule requires BOTH an allow-path AND deny-path test

---

## 📋 Commit Message Format

```
<type>: <short description>

Types: fix | feat | sec | chore | docs | test | ci | compliance | perf
Examples:
  sec: remove hardcoded JWT secret from app/main.py
  feat: add /api/v1/verify endpoint to GPIS
  compliance: implement NIST AC-6 namespace validation
  fix: resolve CVE evaluate_security() logic ambiguity
```
