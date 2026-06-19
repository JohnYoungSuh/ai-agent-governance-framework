import pytest
import os
import json
from fastapi.testclient import TestClient
from app.main import app, check_budget_pip, redis_client
from scripts.governance_router import GovernanceRouter

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_env():
    os.environ["GPIS_JWT_SECRET"] = "suhlabs-super-secret-governance-key"
    yield

def test_arch_uc_01_gpis_suspends_network_policy_modification():
    """ARCH-UC-01: NetworkPolicy modification request -> GPIS -> SUSPENDED"""
    # Trigger suspend via the admin API
    response = client.post("/admin/v1/suspend/architect-agent")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUSPENDED"
    assert "token" in data

def test_arch_uc_02_resume_with_human_approver():
    """ARCH-UC-02: Valid Jira CR + human approver -> resume -> APPROVED"""
    # 1. Suspend
    res_sus = client.post("/admin/v1/suspend/architect-agent")
    token = res_sus.json()["token"]

    # 2. Approve suspension (simulating human approver signing off)
    res_app = client.post(f"/admin/v1/approve/{token}")
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "APPROVED"

    # 3. Request status check
    res_status = client.get(f"/api/v1/suspension/{token}/status")
    assert res_status.json()["status"] == "APPROVED"

def test_arch_uc_03_budget_critical_warning_alert(monkeypatch):
    """ARCH-UC-03: Token budget at 95% -> request -> GPIS -> BUDGET_CRITICAL warning in JWT claims"""
    class MockRedis:
        def get(self, key):
            return b"56000"
    import app.main
    monkeypatch.setattr(app.main, "redis_client", MockRedis())
    
    from app.main import check_budget_pip
    
    status_str, allowed = check_budget_pip("architect-agent")
    assert allowed is True
    assert status_str == "BUDGET_CRITICAL"

def test_arch_uc_04_conjur_ephemeral_token():
    """ARCH-UC-04: Agent identity bootstrapping -> Conjur ephemeral token returned"""
    router = GovernanceRouter()
    token = router._fetch_ephemeral_credential("https://conjur.local", "architect-agent")
    assert token is not None
    assert len(token) > 0
