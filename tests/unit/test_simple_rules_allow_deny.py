"""Allow/deny pairs for every simple_rules.yml key, plus kernel hardening."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import FORBIDDEN_JWT_DEFAULTS, app, get_jwt_secret
from app.policy_engine import SIMPLE_RULES, evaluate_condition

client = TestClient(app)
ADMIN_HEADERS = {"X-GPIS-Admin-Key": os.environ["GPIS_ADMIN_API_KEY"]}

RULES = yaml.safe_load(
    (Path(__file__).resolve().parents[2] / "policies" / "simple_rules.yml").read_text()
)


def _split_key(key: str) -> tuple[str, str, str]:
    category, subcategory, risk = key.split(":", 2)
    return category, subcategory, risk


def _base_payload(key: str, *, allow: bool) -> dict:
    category, subcategory, risk = _split_key(key)
    payload = {
        "subcategory": subcategory,
        "risk_level": risk,
        "namespace": "dev",
        "allowed_namespace": "dev",
        "agent_tier": "tier4",
        "jira_cr_id": "CR-TEST-1",
        "path": "/tmp/work",
        "backup_exists": True,
        "resource_quota_ok": True,
        "labels": ["app", "env", "owner"],
        "service_type": "ClusterIP",
        "cost_estimate": 10,
        "read_only_operation": True,
        "contains_pii": False,
        "contains_secrets": False,
    }
    if not allow:
        if "agent_tier >= tier2" in (RULES[key].get("conditions") or []) or "agent_tier >= tier3" in (
            RULES[key].get("conditions") or []
        ) or "agent_tier == tier4" in (RULES[key].get("conditions") or []):
            payload["agent_tier"] = "tier1"
            payload.pop("jira_cr_id", None)
        elif "namespace != production" in (RULES[key].get("conditions") or []) or "namespace in [" in str(
            RULES[key].get("conditions")
        ):
            payload["namespace"] = "production"
        elif "namespace == agent.allowed_namespace" in (RULES[key].get("conditions") or []):
            payload["allowed_namespace"] = "other-ns"
        elif "path contains" in str(RULES[key].get("conditions")):
            payload["path"] = "/var/data/file"
        elif "backup_exists" in str(RULES[key].get("conditions")):
            payload["backup_exists"] = False
        elif "resource_quota_ok" in str(RULES[key].get("conditions")):
            payload["resource_quota_ok"] = False
        elif "has labels" in str(RULES[key].get("conditions")):
            payload["labels"] = []
        elif "service_type" in str(RULES[key].get("conditions")):
            payload["service_type"] = "LoadBalancer"
        elif "cost_estimate" in str(RULES[key].get("conditions")):
            payload["cost_estimate"] = 500
        elif "read_only_operation" in str(RULES[key].get("conditions")):
            payload["read_only_operation"] = False
        elif "no PII" in str(RULES[key].get("conditions")):
            payload["contains_pii"] = True
        else:
            payload["namespace"] = "production"
            payload["allowed_namespace"] = "dev"
    return payload


@pytest.mark.parametrize("rule_key", list(RULES.keys()))
def test_simple_rule_allow_or_structured_deny(rule_key: str):
    category, _, _ = _split_key(rule_key)
    decision = RULES[rule_key].get("decision", "DENY")
    escalate = RULES[rule_key].get("escalate", False)
    payload = _base_payload(rule_key, allow=True)
    response = client.post(
        "/api/v1/authorize",
        json={"agent_id": "test-agent", "category": category, "payload": payload},
    )
    if decision == "ALLOW" and not escalate:
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["allowed"] is True
        assert body["token"]
        assert body["audit_id"]
    else:
        assert response.status_code == 403, response.text
        detail = response.json()["detail"]
        assert detail["allowed"] is False
        assert detail.get("audit_id")


@pytest.mark.parametrize("rule_key", list(RULES.keys()))
def test_simple_rule_negative_path(rule_key: str):
    category, _, _ = _split_key(rule_key)
    payload = _base_payload(rule_key, allow=False)
    conditions = RULES[rule_key].get("conditions") or []
    if not conditions and RULES[rule_key].get("decision") == "ALLOW":
        payload["risk_level"] = "critical"
    response = client.post(
        "/api/v1/authorize",
        json={"agent_id": "test-agent", "category": category, "payload": payload},
    )
    assert response.status_code == 403, response.text
    detail = response.json()["detail"]
    assert detail["allowed"] is False
    assert "audit_id" in detail


def test_unknown_condition_fails_closed():
    assert evaluate_condition("unknown magic flag", {"namespace": "dev"}) is False


def test_admin_suspend_requires_key():
    response = client.post("/admin/v1/suspend/kill-switch-target")
    assert response.status_code == 401


def test_admin_suspend_with_key():
    response = client.post("/admin/v1/suspend/kill-switch-target", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "SUSPENDED"


def test_jwt_secret_rejects_published_defaults(monkeypatch):
    monkeypatch.setenv("GPIS_JWT_SECRET", "dev-gpis-jwt-secret-key-change-in-prod")
    with pytest.raises(RuntimeError, match="published default"):
        get_jwt_secret()
    assert "dev-gpis-jwt-secret-key-change-in-prod" in FORBIDDEN_JWT_DEFAULTS


def test_jwt_secret_required(monkeypatch):
    monkeypatch.delenv("GPIS_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="required"):
        get_jwt_secret()


def test_audit_file_written_on_allow():
    audit_dir = Path(os.environ["GPIS_AUDIT_DIR"])
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "test-agent",
            "category": "COMPLY",
            "payload": {
                "subcategory": "policy_validation",
                "risk_level": "low",
                "namespace": "dev",
                "agent_tier": "tier1",
            },
        },
    )
    assert response.status_code == 200
    audit_id = response.json()["audit_id"]
    record = json.loads((audit_dir / f"{audit_id}.json").read_text())
    assert record["audit_id"] == audit_id
    assert record["compliance_result"] == "pass"
    assert record["actor"] == "test-agent"


def test_health_aliases():
    assert client.get("/health").status_code == 200
    assert client.get("/health/live").status_code == 200
    assert client.get("/ready").status_code == 200
    assert client.get("/health/ready").status_code == 200


def test_oversized_payload_rejected():
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "test-agent",
            "category": "ACCESS",
            "payload": {"blob": "x" * 3000, "subcategory": "logs", "risk_level": "low"},
        },
    )
    assert response.status_code == 422


def test_simple_rules_loaded():
    assert SIMPLE_RULES
    assert len(SIMPLE_RULES) >= 19
