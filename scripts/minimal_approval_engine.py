#!/usr/bin/env python3
"""
Minimal Approval Engine

Purpose: Auto-approve low-risk actions to achieve ≥80% autonomy

Logic:
  1. Check if action is pre-approved → auto-approve
  2. Calculate risk score (0-100)
  3. If score < 30 → auto-approve
  4. If score ≥ 30 → require human approval
"""

# Pre-approved actions (always auto-approve)
PRE_APPROVED_ACTIONS = [
    "restart_pod",
    "scale_within_limits",
    "renew_certificate",
    "rotate_logs",
    "update_configmap",
    "rolling_restart"
]

# Risk scoring weights
WEIGHTS = {
    "blast_radius": 0.5,
    "reversible": 0.3,
    "cost_impact": 0.2
}

# Auto-approve threshold
AUTO_APPROVE_THRESHOLD = 30


def calculate_risk_score(action):
    """
    Calculate risk score (0-100) using 3 factors
    
    Args:
        action: dict with keys:
            - affected_resources: int
            - has_rollback: bool
            - cost_delta: float
    
    Returns:
        float: risk score (0-100)
    """
    
    # Factor 1: Blast radius (50% weight)
    affected_resources = action.get("affected_resources", 0)
    blast_score = 90 if affected_resources >= 10 else 10
    
    # Factor 2: Reversible (30% weight)
    has_rollback = action.get("has_rollback", False)
    reversible_score = 10 if has_rollback else 90
    
    # Factor 3: Cost impact (20% weight)
    cost_delta = action.get("cost_delta", 0)
    cost_score = 90 if cost_delta >= 100 else 10
    
    # Weighted sum
    risk_score = (
        blast_score * WEIGHTS["blast_radius"] +
        reversible_score * WEIGHTS["reversible"] +
        cost_score * WEIGHTS["cost_impact"]
    )
    
    return risk_score


def should_auto_approve(action):
    """
    Decide if action should be auto-approved
    
    Args:
        action: dict with keys:
            - type: str (action type)
            - affected_resources: int
            - has_rollback: bool
            - cost_delta: float
    
    Returns:
        tuple: (bool: should_approve, str: reason)
    """
    
    action_type = action.get("type", "")
    
    # Check pre-approved list
    if action_type in PRE_APPROVED_ACTIONS:
        return True, f"Pre-approved action: {action_type}"
    
    # Calculate risk
    risk_score = calculate_risk_score(action)
    
    # Auto-approve if low risk
    if risk_score < AUTO_APPROVE_THRESHOLD:
        return True, f"Low risk score: {risk_score:.1f} < {AUTO_APPROVE_THRESHOLD}"
    
    # Require human approval
    return False, f"High risk score: {risk_score:.1f} >= {AUTO_APPROVE_THRESHOLD}"


# Example usage
if __name__ == "__main__":
    print("Minimal Approval Engine - Test Cases\n")
    
    # Test case 1: Pre-approved action
    action1 = {
        "type": "restart_pod",
        "affected_resources": 1,
        "has_rollback": True,
        "cost_delta": 0
    }
    approve, reason = should_auto_approve(action1)
    print(f"Test 1: {action1['type']}")
    print(f"  Result: {'✅ AUTO-APPROVE' if approve else '❌ REQUIRE APPROVAL'}")
    print(f"  Reason: {reason}\n")
    
    # Test case 2: Low risk action
    action2 = {
        "type": "deploy_service",
        "affected_resources": 5,
        "has_rollback": True,
        "cost_delta": 50
    }
    approve, reason = should_auto_approve(action2)
    risk = calculate_risk_score(action2)
    print(f"Test 2: {action2['type']}")
    print(f"  Risk Score: {risk:.1f}")
    print(f"  Result: {'✅ AUTO-APPROVE' if approve else '❌ REQUIRE APPROVAL'}")
    print(f"  Reason: {reason}\n")
    
    # Test case 3: High risk action
    action3 = {
        "type": "delete_database",
        "affected_resources": 50,
        "has_rollback": False,
        "cost_delta": 5000
    }
    approve, reason = should_auto_approve(action3)
    risk = calculate_risk_score(action3)
    print(f"Test 3: {action3['type']}")
    print(f"  Risk Score: {risk:.1f}")
    print(f"  Result: {'✅ AUTO-APPROVE' if approve else '❌ REQUIRE APPROVAL'}")
    print(f"  Reason: {reason}\n")
    
    # Test case 4: Medium risk action
    action4 = {
        "type": "scale_up",
        "affected_resources": 8,
        "has_rollback": True,
        "cost_delta": 80
    }
    approve, reason = should_auto_approve(action4)
    risk = calculate_risk_score(action4)
    print(f"Test 4: {action4['type']}")
    print(f"  Risk Score: {risk:.1f}")
    print(f"  Result: {'✅ AUTO-APPROVE' if approve else '❌ REQUIRE APPROVAL'}")
    print(f"  Reason: {reason}\n")
