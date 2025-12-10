from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

class PolicyCategory(str, Enum):
    SECURITY = "SECURITY"
    DEPLOYMENT = "DEPLOYMENT"
    OPERATIONS = "OPERATIONS"

class PolicyRequest(BaseModel):
    agent_id: str
    category: PolicyCategory
    payload: Dict[str, Any]

class PolicyResponse(BaseModel):
    allowed: bool
    reason: str
    token: Optional[str] = None

def evaluate_security(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Evaluates SECURITY policies.
    Rule: APPROVED if CVE score > 9.0 (Simulating a specific high-severity checking logic, 
    or arguably this might be 'DENIED if > 9.0' normally, but following user prompt: 'If Score > 9.0, APPROVED').
    Wait, user prompt said: "Checks CVE scores. (Rule: If Score > 9.0, APPROVED)."
    This is unusual (usually high score = bad = block), but I must follow instructions.
    """
    cve_score = payload.get("cve_score", 0.0)
    if cve_score > 9.0:
        return True, "Approved: Critical security patch required (Score > 9.0)."
    return False, f"Denied: Security score {cve_score} does not meet threshold > 9.0."

def evaluate_deployment(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Evaluates DEPLOYMENT policies.
    Rule: DENIED if commit_signed is False.
    """
    commit_signed = payload.get("commit_signed", False)
    if not commit_signed:
        return False, "Denied: Deployment blocked: Commit signature missing."
    return True, "Approved: Deployment authorized with signed commit."

def evaluate_operations(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Evaluates OPERATIONS policies.
    Rule: DENIED if time is between 9am-5pm.
    """
    # Assuming 'time' is passed in payload (e.g., "09:30") or we check current system time if not provided?
    # User requirement: "Checks maintenance windows. (Rule: If time is between 9am-5pm, DENIED)."
    # I will check payload first, then fallback to current time or just assume payload for deterministic behavior.
    # Let's use datetime.now() for the real check as it's more realistic for an "Engine", 
    # but for testability, accepting a time string in payload is better.
    # Let's look for a timestamp or hour in payload, else use current server time.
    
    current_hour = datetime.now().hour
    
    # Allow payload override for testing/simulation
    if "hour" in payload:
        try:
            current_hour = int(payload["hour"])
        except ValueError:
            pass # Fallback to real time
            
    # Window: 9:00 (9) to 17:00 (17)
    # If 9 <= hour < 17, it is within the window => DENIED.
    if 9 <= current_hour < 17:
        return False, f"Denied: Operations blocked during maintenance window (9am-5pm). Current hour: {current_hour}."
    
    return True, f"Approved: Operation allowed outside maintenance window. Current hour: {current_hour}."

def evaluate_request(request: PolicyRequest) -> tuple[bool, str]:
    if request.category == PolicyCategory.SECURITY:
        return evaluate_security(request.payload)
    elif request.category == PolicyCategory.DEPLOYMENT:
        return evaluate_deployment(request.payload)
    elif request.category == PolicyCategory.OPERATIONS:
        return evaluate_operations(request.payload)
    else:
        return False, f"Denied: Unknown policy category {request.category}"
