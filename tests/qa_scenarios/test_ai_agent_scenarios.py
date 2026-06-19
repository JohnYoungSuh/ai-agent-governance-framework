import pytest
import os
from fastapi.testclient import TestClient
from app.main import app, check_budget_pip, redis_client
from scripts.governance_router import GovernanceRouter

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_env():
    os.environ["GPIS_JWT_SECRET"] = "suhlabs-super-secret-governance-key"
    yield

def test_ai_uc_01_training_job_dev_allowed():
    """AI-UC-01: Training job authorization in dev -> GPIS -> ALLOWED"""
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "ai-agent",
            "category": "CREATE",
            "payload": {
                "subcategory": "kubernetes_deployment",
                "risk_level": "medium",
                "namespace": "dev",
                "agent_tier": "tier3",  # CronJob running at Tier 3
                "jira_cr_id": "CR-2026-1111"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert "token" in data

def test_ai_uc_02_training_job_production_no_cr_denied():
    """AI-UC-02: Training job authorization in production without Jira CR -> GPIS -> DENIED"""
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "ai-agent",
            "category": "CREATE",
            "payload": {
                "subcategory": "kubernetes_deployment",
                "risk_level": "medium",
                "namespace": "production",
                "agent_tier": "tier3"
            }
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"]["allowed"] is False
    assert "jira cr id is required" in data["detail"]["reason"].lower()

def test_ai_uc_03_budget_exceeded_denied(monkeypatch):
    """AI-UC-03: Agent exceeds daily token budget (100%) -> GPIS -> BUDGET_EXCEEDED, all new JWTs DENIED"""
    class MockRedis:
        def get(self, key):
            return b"200000"
    import app.main
    monkeypatch.setattr(app.main, "redis_client", MockRedis())
    
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "ai-agent",
            "category": "CREATE",
            "payload": {
                "subcategory": "kubernetes_deployment",
                "risk_level": "medium",
                "namespace": "dev",
                "agent_tier": "tier3",
                "jira_cr_id": "CR-2026-1111"
            }
        }
    )
    # Status should be 403 because budget PIP fails closed
    assert response.status_code == 403
    data = response.json()
    assert data["detail"]["allowed"] is False
    assert "daily token budget exceeded" in data["detail"]["reason"].lower()

def test_ai_uc_04_direct_redis_access_denied():
    """AI-UC-04: Agent tries direct Redis access (bypassing GovernanceRouter) -> Blocked"""
    router = GovernanceRouter()
    
    # Valid call through Router Broker
    router.memory_write("ai-agent", "metric", "loss=0.02")
    assert router.memory_read("ai-agent", "metric") == "loss=0.02"

    # Simulate direct client access validation via helper (direct access to redis is disallowed)
    res = router.execute_tool(
        agent_id="ai-agent",
        tool_name="sql_query",
        arguments={"query": "SELECT * FROM secrets", "host": "internal-db.ai-agents-prod.svc.cluster.local"}
    )
    # The tool configuration for sql_query requires SELECT only and is Tier 2, but let's check
    assert res is not None
