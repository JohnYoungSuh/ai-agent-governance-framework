import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from scripts.governance_router import GovernanceRouter

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_env():
    os.environ["GPIS_JWT_SECRET"] = "dev-gpis-jwt-secret-key-change-in-prod"
    yield

def test_operations_uc_01_maintenance_window_deny():
    """OPS-UC-01: Agent requests deployment during maintenance window (9am–5pm) -> GPIS -> DENIED"""
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "it-ops-agent",
            "category": "OPERATIONS",
            "payload": {
                "hour": 10,  # 10am is inside maintenance window (9am-5pm)
                "agent_tier": "tier3",
                "jira_cr_id": "CR-APPROVED"
            }
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"]["allowed"] is False
    assert "maintenance window" in data["detail"]["reason"].lower()

def test_operations_uc_01b_outside_maintenance_window_allow():
    """OPS-UC-01b: Agent requests deployment outside maintenance window -> GPIS -> ALLOWED"""
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "it-ops-agent",
            "category": "OPERATIONS",
            "payload": {
                "hour": 18,  # 6pm is outside maintenance window
                "agent_tier": "tier3",
                "jira_cr_id": "CR-APPROVED"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True

def test_deployment_uc_02_deploy_with_jira_cr_allow():
    """OPS-UC-02: Agent requests deployment with valid Jira CR (Tier 3) -> GPIS -> ALLOWED"""
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "it-ops-agent",
            "category": "DEPLOYMENT",
            "payload": {
                "commit_signed": True,
                "agent_tier": "tier3",
                "jira_cr_id": "CR-2026-1234"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert "token" in data

def test_deployment_uc_03_deploy_without_jira_cr_deny():
    """OPS-UC-03: Agent requests deployment WITHOUT Jira CR -> GPIS -> DENIED"""
    response = client.post(
        "/api/v1/authorize",
        json={
            "agent_id": "it-ops-agent",
            "category": "DEPLOYMENT",
            "payload": {
                "commit_signed": True,
                "agent_tier": "tier3"
            }
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"]["allowed"] is False
    assert "jira cr id is required" in data["detail"]["reason"].lower()

def test_ops_uc_04_hitl_suspension_lifecycle():
    """OPS-UC-04: HITL lifecycle: suspend -> approve -> status update"""
    # 1. Trigger suspend via admin API
    res_sus = client.post("/admin/v1/suspend/it-ops-agent")
    assert res_sus.status_code == 200
    sus_data = res_sus.json()
    token = sus_data["token"]
    assert sus_data["status"] == "SUSPENDED"

    # 2. Check status is suspended
    res_stat = client.get(f"/api/v1/suspension/{token}/status")
    assert res_stat.status_code == 200
    assert res_stat.json()["status"] == "SUSPENDED"

    # 3. Approve suspension
    res_app = client.post(f"/admin/v1/approve/{token}")
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "APPROVED"

    # 4. Verify approved status
    res_stat2 = client.get(f"/api/v1/suspension/{token}/status")
    assert res_stat2.json()["status"] == "APPROVED"

def test_ops_uc_05_memory_checkpoint_restore():
    """OPS-UC-05: Agent memory checkpoint survives pod restart/restore"""
    router = GovernanceRouter()
    
    # Write context
    router.memory_write("it-ops-agent", "step", "deploying_ingress")
    router.memory_write("it-ops-agent", "revision", "v2")
    
    # Checkpoint
    checkpoint_id = router.memory_checkpoint("it-ops-agent")
    assert checkpoint_id is not None
    
    # Wipe local active memory to simulate restart/eviction (preserving checkpoints)
    keys_to_delete = [k for k in router.local_memory.keys() if k.startswith("agent_memory:it-ops-agent:")]
    for k in keys_to_delete:
        del router.local_memory[k]
    if router.redis_client:
        router.redis_client.delete("agent_memory:it-ops-agent:step")
        router.redis_client.delete("agent_memory:it-ops-agent:revision")
        
    assert router.memory_read("it-ops-agent", "step") is None

    # Restore
    restored = router.memory_restore("it-ops-agent", checkpoint_id)
    assert restored is True
    
    # Verify values are restored
    assert router.memory_read("it-ops-agent", "step") == "deploying_ingress"
    assert router.memory_read("it-ops-agent", "revision") == "v2"
