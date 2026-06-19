---
trigger: always_on
---

# Testing Rules

## Test Strategy: Three Layers

### Layer 1: Unit Tests (`tests/`)
- **Framework**: `pytest` + `pytest-cov`
- **Location**: `tests/unit/`
- **Target coverage**: ≥80% for all `app/` and `scripts/` modules
- Run: `pytest tests/unit/ -v --cov=app --cov=scripts`

### Layer 2: Integration Tests (`tests/integration/`)
- Test the full GPIS API flow: request → policy evaluation → JWT issuance
- Test GovernanceRouter with mocked LLM clients (not live API calls)
- Test audit trail schema validation on every emitted event
- Run: `pytest tests/integration/ -v`

### Layer 3: Compliance Tests (`tests/compliance/`)
- Validate that all 16 guardrail rules are enforced by the router
- Validate JSON schemas (`audit-trail.json`, `siem-event.json`, `agent-cost-record.json`)
- Validate agent manifest schema
- Run: `pytest tests/compliance/ -v`

## Required Tests Per Feature

### Every new GPIS policy rule requires:
```python
# tests/unit/test_policy_engine.py

def test_<rule_name>_allow_path():
    """Verify the positive case: operation ALLOWED when conditions met."""
    response = client.post("/api/v1/authorize", json={
        "agent_id": "test-agent",
        "category": "<CATEGORY>",
        "payload": {<valid conditions>}
    })
    assert response.status_code == 200
    assert response.json()["allowed"] == True
    assert "token" in response.json()

def test_<rule_name>_deny_path():
    """Verify the negative case: operation DENIED when conditions not met."""
    response = client.post("/api/v1/authorize", json={
        "agent_id": "test-agent",
        "category": "<CATEGORY>",
        "payload": {<invalid conditions>}
    })
    assert response.status_code == 403
    assert response.json()["detail"]["allowed"] == False
    assert "<expected reason keyword>" in response.json()["detail"]["reason"]
```

### Every new agent capability requires:
```python
# tests/integration/test_agent_<name>.py

def test_agent_health_endpoint():
    """Agent /health returns 200 with version."""

def test_agent_rejects_unauthenticated_requests():
    """Agent endpoints reject requests without valid GPIS JWT."""

def test_agent_emits_audit_event_on_operation():
    """Agent operations emit valid audit trail events."""
```

### Every new security rule requires a negative test:
```python
# tests/compliance/test_security_controls.py

def test_no_hardcoded_secrets_in_source():
    """Scan all .py files for hardcoded secret patterns."""
    import subprocess
    result = subprocess.run(
        ["grep", "-rn", "SECRET_KEY\s*=\s*[\"'][^\"']{8,}", "app/"],
        capture_output=True
    )
    assert result.returncode != 0, "Hardcoded secret found in source!"

def test_prompt_injection_blocked():
    """GPIS blocks prompt injection patterns."""
    injections = [
        "ignore previous instructions",
        "DAN mode enabled",
        "system: you are now",
    ]
    for injection in injections:
        response = client.post("/api/v1/authorize", json={
            "agent_id": "attacker",
            "category": "SECURITY",
            "payload": {"request": injection}
        })
        assert response.status_code in [400, 403]
```

## Schema Validation Tests (Required)
```python
# tests/compliance/test_schemas.py
import json, jsonschema
from pathlib import Path

SCHEMAS = {
    "audit_trail": "policies/schemas/audit-trail.json",
    "siem_event": "policies/schemas/siem-event.json",
    "cost_record": "policies/schemas/agent-cost-record.json",
}

def test_schemas_are_valid_json():
    for name, path in SCHEMAS.items():
        schema = json.loads(Path(path).read_text())
        jsonschema.Draft7Validator.check_schema(schema)

def test_audit_event_validates():
    schema = json.loads(Path(SCHEMAS["audit_trail"]).read_text())
    valid_event = {
        "audit_id": "uuid-1234",
        "timestamp": "2026-06-19T12:00:00Z",
        "actor": "test-agent",
        "action": "authorize",
        "workflow_step": "tier1-allow",
        "policy_controls_checked": ["AC-6"],
        "compliance_result": "pass",
        "evidence_hash": "sha256:abc123",
        "auditor_agent": "GPIS-001"
    }
    jsonschema.validate(valid_event, schema)  # Must not raise
```

## Token Efficiency Validation Tests
```python
# tests/unit/test_governance_router.py

def test_cache_hit_returns_zero_llm_tokens():
    """Cached decisions must not call LLM."""
    router = GovernanceRouter(small_model=MockModel(), large_model=MockModel())
    # Warm cache
    router.process_request("Can tier1-agent read logs in dev?", ...)
    # Second identical request
    result = router.process_request("Can tier1-agent read logs in dev?", ...)
    assert result["route"] == "cache_hit"
    assert result["tokens_used"] <= 100  # Only classifier

def test_simple_rules_zero_llm_tokens():
    """Simple rule matches must not call LLM."""
    result = router.process_request("ACCESS:logs:low in dev", ...)
    assert result["route"] == "simple_rules"
    assert MockModel.call_count == 0  # No LLM called
```

## Test Commands Reference
| Command | Purpose |
|---------|---------|
| `pytest tests/ -v` | All tests |
| `pytest tests/unit/ -v --cov=app` | Unit tests with coverage |
| `pytest tests/compliance/ -v` | Schema + guardrail compliance tests |
| `pytest tests/ -k "test_security"` | Security-specific tests only |
| `./scripts/test-siem-emitter.sh` | SIEM emitter validation (10/10 must pass) |
| `python3 scripts/benchmark_token_savings.py --format json` | Token efficiency benchmark |
