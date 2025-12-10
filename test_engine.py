from app.policy_engine import evaluate_request, PolicyRequest, PolicyCategory

def run_tests():
    print("Running Governance Policy Engine Tests...\n")

    # Test 1: Security (Approved)
    req1 = PolicyRequest(
        agent_id="agent-01",
        category=PolicyCategory.SECURITY,
        payload={"cve_score": 9.5}
    )
    allowed, reason = evaluate_request(req1)
    print(f"Test 1 (Security > 9.0): Allowed={allowed}, Reason='{reason}'")
    assert allowed == True
    assert "Approved" in reason

    # Test 2: Security (Denied)
    req2 = PolicyRequest(
        agent_id="agent-02",
        category=PolicyCategory.SECURITY,
        payload={"cve_score": 8.0}
    )
    allowed, reason = evaluate_request(req2)
    print(f"Test 2 (Security <= 9.0): Allowed={allowed}, Reason='{reason}'")
    assert allowed == False

    # Test 3: Deployment (Approved)
    req3 = PolicyRequest(
        agent_id="agent-03",
        category=PolicyCategory.DEPLOYMENT,
        payload={"commit_signed": True}
    )
    allowed, reason = evaluate_request(req3)
    print(f"Test 3 (Deployment Signed): Allowed={allowed}, Reason='{reason}'")
    assert allowed == True

    # Test 4: Deployment (Denied)
    req4 = PolicyRequest(
        agent_id="agent-04",
        category=PolicyCategory.DEPLOYMENT,
        payload={"commit_signed": False}
    )
    allowed, reason = evaluate_request(req4)
    print(f"Test 4 (Deployment Unsigned): Allowed={allowed}, Reason='{reason}'")
    assert allowed == False

    # Test 5: Operations (Mocked Time)
    # Using 'hour' payload override I added for testability
    req5 = PolicyRequest(
        agent_id="agent-05",
        category=PolicyCategory.OPERATIONS,
        payload={"hour": 10} # 10 AM -> Maintenance window -> Denied
    )
    allowed, reason = evaluate_request(req5)
    print(f"Test 5 (Ops 10AM): Allowed={allowed}, Reason='{reason}'")
    assert allowed == False

    req6 = PolicyRequest(
        agent_id="agent-06",
        category=PolicyCategory.OPERATIONS,
        payload={"hour": 20} # 8 PM -> Outside window -> Approved
    )
    allowed, reason = evaluate_request(req6)
    print(f"Test 6 (Ops 8PM): Allowed={allowed}, Reason='{reason}'")
    assert allowed == True

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
