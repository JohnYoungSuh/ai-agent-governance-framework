# AI Agent Governance — Critical Gaps Analysis & Fix Status

**Analysis Date:** 2025-10-24
**Documents Analyzed:**
- `GOVERNANCE_GUARDRAILS.md`
- `frameworks/agent-guardrail.yaml`
- `scripts/validate_agent_guardrail.py`

**Framework References:** NIST AI RMF, ISO/IEC 42001, MITRE ATLAS, IEEE 7009

---

## Executive Summary

**5 Critical Gaps Identified** — Each enables AI agents to operate outside intended scope, cause unintended damage, or evade oversight.

**Status:**
- ✅ **1 Fixed** (Gap #1: Pre-execution validation)
- ⏳ **4 Pending** (Estimated 1.5 hours total to fix remaining)

---

## Critical Gap Details

### ✅ Gap #1: Post-Hoc Validation, Not Runtime Enforcement [FIXED]

**Severity:** 🔴 Critical
**Risk:** Agent can damage resources BEFORE validation catches it

**Problem:**
- Original validator ran AFTER action completed (`validate_agent_guardrail.py:33-56`)
- By then, files deleted, containers modified, data lost
- Audit log would show violation, but damage already done

**Fix Implemented:**
- **File Modified:** `scripts/validate_agent_guardrail.py`
- **Added:** `pre_validate_action()` function (line 33-80)
- **Validates BEFORE execution:**
  - Action allowed for agent
  - Target resources within namespace boundary
  - Destructive actions flagged for confirmation
- **CLI Updated:** Added `--namespace`, `--resources`, `--pre-validate-only` flags
- **Documentation:** `docs/PRE-EXECUTION-VALIDATION-USAGE.md`

**Usage Example:**
```bash
python scripts/validate_agent_guardrail.py \
  --agent cleanup-agent \
  --action delete \
  --namespace my-project \
  --resources ~/projects/my-project/temp/file.txt \
  --output /tmp/result.txt \
  --pre-validate-only
# Exit 0 = approved, Exit 1 = blocked
```

**Impact:** Prevents cross-namespace contamination and unauthorized resource modification

---

### ⏳ Gap #2: Namespace Validation = Empty Promise [PENDING]

**Severity:** 🔴 Critical
**Estimated Fix Time:** 1 hour
**Risk:** Agent can claim any namespace without verification

**Problem:**
- Policy requires "namespace validated via JWT/signed metadata" (`GOVERNANCE_GUARDRAILS.md:11`)
- **NO CODE implements this** — agents can claim any namespace
- No signature verification = no trust boundary

**What Could Go Wrong:**
- Agent claims to be in `project-a` namespace
- Actually operates on `project-b` resources
- No detection mechanism

**Proposed Fix:**
```python
import jwt

def validate_namespace_claim(agent_metadata, expected_namespace):
    """Verify agent JWT claim matches expected namespace"""
    token = agent_metadata.get('namespace_token')
    claims = jwt.decode(token, PUBLIC_KEY, algorithms=['RS256'])

    if claims['namespace'] != expected_namespace:
        raise NamespaceViolation(f"Agent claimed {claims['namespace']}, expected {expected_namespace}")
```

**Where to Add:** `scripts/validate_agent_guardrail.py:27` — call in `validate_action()` and `pre_validate_action()`

**Requirements:**
- Generate/distribute public key for JWT verification
- Define JWT payload schema (namespace, agent_id, issued_at, expires_at)
- Update agent startup to request signed namespace token

---

### ⏳ Gap #3: Audit Logs Are Mutable (Can Be Tampered) [PENDING]

**Severity:** 🔴 Critical
**Estimated Fix Time:** 15 minutes
**Risk:** Evidence can be deleted, compliance violated

**Problem:**
- Policy requires "immutable, append-only storage" (`GOVERNANCE_GUARDRAILS.md:74`)
- Current code OVERWRITES JSON file (`validate_agent_guardrail.py:82-83`)
- Malicious agent or insider can delete log entries

**What Could Go Wrong:**
- Agent performs unauthorized action → logs it
- Later, agent or attacker deletes the log entry
- Compliance audit finds no evidence of violation

**Proposed Fix:**
```python
# JSON Lines format (one entry per line, append-only)
audit_file = Path(f"audit/{datetime.date.today()}.jsonl")
audit_file.parent.mkdir(exist_ok=True)

with open(audit_file, "a") as f:  # APPEND mode, not overwrite
    f.write(json.dumps(entry) + "\n")
```

**Where to Fix:** `scripts/validate_agent_guardrail.py:82-83`

**Better Long-Term Solution:**
- Stream logs to S3 with Object Lock enabled
- Or send to centralized SIEM (Splunk, ELK, CloudWatch)
- Or use `logger` with syslog backend

---

### ⏳ Gap #4: Policy Hash Verification = Not Implemented [PENDING]

**Severity:** 🔴 Critical
**Estimated Fix Time:** 20 minutes
**Risk:** Agent can run with tampered policy, no restrictions

**Problem:**
- Policy header says "Policy hash must match registry" (`GOVERNANCE_GUARDRAILS.md:5`)
- **NO CODE verifies this** — agents never check policy integrity
- Attacker can modify `agent-guardrail.yaml` to allow forbidden actions

**What Could Go Wrong:**
- Attacker edits `frameworks/agent-guardrail.yaml`:
  ```yaml
  allowed_actions: [scan, deploy, delete_everything]  # Added forbidden action
  ```
- Agent loads modified policy
- Operates without restrictions
- No detection because hash never checked

**Proposed Fix:**
```python
import hashlib

EXPECTED_POLICY_HASH = "sha256:abc123..."  # From governance registry

def verify_policy_integrity(config_path):
    """Verify policy file hasn't been tampered with"""
    with open(config_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()

    if actual_hash != EXPECTED_POLICY_HASH:
        raise PolicyTamperDetected(f"Policy hash mismatch: {actual_hash}")
```

**Where to Add:** `scripts/validate_agent_guardrail.py:88` — call before `load_guardrails()`

**Requirements:**
- Establish policy registry (can be Git commit hash initially)
- Generate and store expected policy hash
- Update hash when policy is legitimately changed

---

### ⏳ Gap #5: No Emergency Kill Switch [PENDING]

**Severity:** 🔴 Critical
**Estimated Fix Time:** 30 minutes
**Risk:** Runaway agent with no way to halt

**Problem:**
- No mechanism to emergency-stop rogue or malfunctioning agent
- If agent enters loop or operates incorrectly, damage accumulates
- Human operator has no interrupt capability

**What Could Go Wrong:**
- Agent starts deleting files in infinite loop
- Operator notices immediately
- No way to halt agent mid-execution
- Must wait for timeout or process kill (may be too late)

**Proposed Fix:**
```python
KILL_SWITCH_FILE = Path("/tmp/agent_kill_switch")

def check_kill_switch():
    """Check if emergency stop has been activated"""
    if KILL_SWITCH_FILE.exists():
        raise AgentHalted("Emergency kill switch activated")

# In validate_action() and pre_validate_action():
# Call check_kill_switch() at start of function
```

**Usage:**
```bash
# To emergency-stop all agents:
touch /tmp/agent_kill_switch

# All agents will halt at next validation check
# To resume:
rm /tmp/agent_kill_switch
```

**Where to Add:**
- `scripts/validate_agent_guardrail.py:33` (in `pre_validate_action`)
- `scripts/validate_agent_guardrail.py:83` (in `validate_action`)

**Enhancement:** Per-agent kill switches
```bash
/tmp/agent_kill_switch_<agent_name>  # Kill specific agent
/tmp/agent_kill_switch_all           # Kill all agents
```

---

## Summary Table

| Gap | Severity | Status | Fix Time | Impact if Exploited |
|-----|----------|--------|----------|---------------------|
| #1: Post-hoc validation | 🔴 Critical | ✅ FIXED | 30 min | Data loss, wrong namespace modification |
| #2: No namespace validation | 🔴 Critical | ⏳ Pending | 1 hour | Cross-project contamination |
| #3: Mutable audit logs | 🔴 Critical | ⏳ Pending | 15 min | Evidence tampering, compliance failure |
| #4: No policy hash check | 🔴 Critical | ⏳ Pending | 20 min | Policy tampering, unrestricted agent |
| #5: No kill switch | 🔴 Critical | ⏳ Pending | 30 min | Runaway agent damage |

**Total Remaining Work:** ~2 hours to close all critical gaps

---

## Files Modified This Session

**Modified:**
- `scripts/validate_agent_guardrail.py` — Added pre-execution validation

**Created:**
- `docs/PRE-EXECUTION-VALIDATION-USAGE.md` — Usage guide for Gap #1 fix
- `docs/GOVERNANCE-GAP-ANALYSIS-STATUS.md` — This status document

---

## Next Session Action Plan

**Priority Order (by impact and ease):**

1. **Gap #3** (15 min) — Quick win, immediate compliance benefit
   - Change audit log from overwrite to append-only
   - Low complexity, high value

2. **Gap #5** (30 min) — Safety net for all agents
   - Implement emergency kill switch
   - Simple file-based flag check

3. **Gap #4** (20 min) — Prevent policy tampering
   - Add hash verification at startup
   - Requires establishing policy registry

4. **Gap #2** (1 hour) — Strongest security improvement
   - JWT namespace validation
   - Requires key generation and distribution

**Recommended:** Start with Gap #3, then Gap #5 — both are quick and significantly improve safety.

---

## Integration Testing Required

After fixing remaining gaps, test:

1. **Cross-namespace protection:**
   ```bash
   # Should BLOCK
   python scripts/validate_agent_guardrail.py \
     --agent test-agent \
     --action modify \
     --namespace project-a \
     --resources ~/projects/project-b/file.txt \
     --output /tmp/test.txt
   ```

2. **Audit log immutability:**
   ```bash
   # Run multiple validations
   # Verify audit/YYYY-MM-DD.jsonl contains all entries
   # Verify no overwrites occurred
   ```

3. **Kill switch:**
   ```bash
   touch /tmp/agent_kill_switch
   # Any agent validation should halt immediately
   ```

4. **Policy hash verification:**
   ```bash
   # Modify frameworks/agent-guardrail.yaml
   # Agent should refuse to start due to hash mismatch
   ```

---

## Compliance Mapping

| Framework | Control Area | Current State | After All Fixes |
|-----------|--------------|---------------|-----------------|
| NIST AI RMF | Govern-1.1 (Accountability) | Partial | ✅ Complete |
| NIST AI RMF | Map-1.2 (Scope Definition) | ⚠️ Weak | ✅ Enforced |
| ISO/IEC 42001 | 6.1.4 (Risk Assessment) | Partial | ✅ Complete |
| MITRE ATLAS | AML.T0051 (Scope Escape) | ❌ Vulnerable | ✅ Mitigated |
| IEEE 7009 | Fail-Safe Design | ❌ Missing | ✅ Implemented |

---

## References

**Original Gap Analysis Prompt:**
- Evaluated policies against NIST AI RMF, ISO/IEC 42001, MITRE ATLAS, IEEE 7009
- Identified gaps enabling agents to operate outside scope
- Prioritized by severity and exploitability

**Policy Documents:**
- `GOVERNANCE_GUARDRAILS.md` — 16 governance rules
- `frameworks/agent-guardrail.yaml` — YAML configuration
- `scripts/validate_agent_guardrail.py` — Validation implementation

---

**End of Status Document**
**Last Updated:** 2025-10-24
**Next Review:** After Gap #2-5 implementation
