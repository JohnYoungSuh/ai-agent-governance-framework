# Lessons Learned — AI Agent Governance Framework

> **Purpose:** Institutional memory for root causes, diagnostic playbooks, and durable fixes. Prevents the same failure from recurring across sessions. New entries go at the top.

---

## 📌 LL-004 — Agent Manifests Accept Invalid YAML Without Error

**Date Identified:** June 19, 2026  
**File:** `agents/*/config/` — no schema enforced

### Root Cause
Agent config YAML files are read directly with `yaml.safe_load()` throughout the codebase but never validated against a schema. An agent manifest with missing `agent_tier`, `namespace`, or `budget` fields will silently pass through the GPIS, potentially allowing unauthorized operations.

### Diagnostic Checklist (Future Agent)
```bash
# Find all agent config files
find agents/ -name "*.yml" -path "*/config/*"

# Check if any schema validation exists
grep -r "jsonschema" scripts/ app/ agents/

# Validate manually against the planned schema
python3 -c "import yaml, jsonschema; ..."
```

### Rule Added to Agent Knowledge
> **Agent Manifest Contract:** Every agent config YAML must be validated against `policies/schemas/agent-manifest.json` at startup. The GPIS must reject any request from an agent whose manifest fails schema validation.

---

## 📌 LL-003 — GovernanceRouter Template Never Wired to LLM Clients

**Date Identified:** June 19, 2026  
**File:** `scripts/governance_router.py`

### Root Cause
The entire `TOKEN-EFFICIENT-IMPLEMENTATION.md` document delivered a production-ready `GovernanceRouter` class template — but the LLM client imports were marked with `# TODO` comments and never integrated. The `_classify_for_cache()` and `_route_intent()` methods return hardcoded mock responses. The 90% token reduction target is entirely theoretical until this is wired.

### What "Done" Looks Like
The GovernanceRouter is fully done only when:
1. `self.small_model` is a live Gemini Flash instance.
2. `self.large_model` is a live Claude Sonnet instance.
3. The cache backend is Redis (not `{}`).
4. Prometheus metrics are emitting.
5. A benchmark run (`scripts/benchmark_token_savings.py`) shows ≥70% actual savings.

### Rule Added to Agent Knowledge
> **Template ≠ Implementation:** A code template in a documentation file is NOT the same as working code. Before declaring the token-efficient router "implemented," verify all `# TODO` blocks are replaced, all unit tests pass, and a live benchmark confirms the savings target.

---

## 📌 LL-002 — CVE Score Policy Logic Is Ambiguous (approve vs deny on score > 9.0)

**Date Identified:** June 19, 2026  
**File:** `app/policy_engine.py`, `evaluate_security()` line 30

### What Happened
```python
def evaluate_security(payload: Dict[str, Any]) -> tuple[bool, str]:
    cve_score = payload.get("cve_score", 0.0)
    if cve_score > 9.0:
        return True, "Approved: Critical security patch required (Score > 9.0)."
```

The function *approves* when CVE score is critical (> 9.0). Standard security logic blocks high-severity vulnerabilities. The developer left a comment acknowledging the confusion but did not resolve it. This creates dual risk: (1) legitimate critical CVE patches may be blocked in other environments that read this as "block if > 9.0," and (2) the ambiguous intent makes auditing impossible.

### Durable Fix Requirements
1. The function must be renamed to `evaluate_security_patch_deployment()`.
2. It must require an explicit `action: emergency_patch` field in the payload.
3. There must be two separate tests: one for "patch approved" and one for "unpatched CVE blocked."
4. The business rule must be documented in `policies/agent-safety-policies.md`.

### The Three-Question Root Cause Checklist
Before closing any policy bug as "fixed":
1. **Is the intent documented?** (Is there a plain-language business rule somewhere?)
2. **Are both positive and negative branches tested?** (Is it impossible for a misconfigured caller to exploit the ambiguity?)
3. **Is it auditable?** (Would a human auditor instantly understand the rule from reading the code + tests?)

---

## 📌 LL-001 — Hardcoded JWT Secret in Source Code

**Date Identified:** June 19, 2026  
**File:** `app/main.py`, line 11  

### What Happened
```python
SECRET_KEY = "suhlabs-super-secret-governance-key"
```

This secret has been committed to the repository in plaintext. Any JWT issued by the GPIS can be forged by anyone with read access to the repository. This is a P0 security vulnerability that invalidates the entire authentication model for Tier 3/4 agent operations.

### Diagnostic Playbook (Future Agent)

```bash
# Step 1 — Find all hardcoded secrets in app/
grep -rn "SECRET" app/ --include="*.py"
grep -rn "password\|secret\|key\|token" app/ --include="*.py" | grep -v "#"

# Step 2 — Verify env var replacement
python3 -c "import os; print(os.getenv('GPIS_JWT_SECRET', 'MISSING'))"

# Step 3 — Run TruffleHog on the repo
trufflehog filesystem . --only-verified

# Step 4 — Verify Kubernetes secret exists
kubectl get secret gpis-credentials -n ai-agents-prod -o jsonpath='{.data.jwt-secret}' | base64 -d
```

### Durable Fix (Not Just Symptom Fix)
```python
# In app/main.py
import os

SECRET_KEY = os.getenv("GPIS_JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("GPIS_JWT_SECRET environment variable is required and not set.")
ALGORITHM = "HS256"
```

### Rule Added to Agent Knowledge
> **No Secrets in Source:** NEVER commit credentials, API keys, JWT secrets, or passwords to source code. Always use `os.getenv()` with a startup assertion. Add `detect-secrets` or TruffleHog as a pre-commit hook. A secret that has ever been in Git history must be rotated — changing the code alone is insufficient.

---

*Maintained by the Antigravity engineering agent. Add new entries at the top under `## 📌 LL-NNN`. Each entry must include: date, file, root cause, diagnostic playbook, and rule added to agent knowledge.*
