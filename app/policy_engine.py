import re
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, field_validator

class PolicyCategory(str, Enum):
    # New 5-category model
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    ACCESS = "ACCESS"
    COMPLY = "COMPLY"
    # Legacy categories
    SECURITY = "SECURITY"
    DEPLOYMENT = "DEPLOYMENT"
    OPERATIONS = "OPERATIONS"

class PolicyRequest(BaseModel):
    agent_id: str = Field(..., max_length=64)
    category: PolicyCategory
    payload: Dict[str, Any]

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9\-_]+$", v):
            raise ValueError("agent_id must be alphanumeric, hyphen, or underscore only")
        return v

class PolicyResponse(BaseModel):
    allowed: bool
    reason: str
    token: Optional[str] = None


# Load simple rules from file
RULES_PATH = Path(__file__).parent.parent / "policies" / "simple_rules.yml"
SIMPLE_RULES = yaml.safe_load(RULES_PATH.read_text()) if RULES_PATH.exists() else {}

def evaluate_security_patch_deployment(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Evaluates SECURITY policies.
    Rule: APPROVED if CVE score > 9.0 AND action == 'emergency_patch' (SEC-002).
    """
    cve_score = payload.get("cve_score", 0.0)
    action = payload.get("action", "")
    if cve_score > 9.0:
        if action == "emergency_patch":
            return True, "Approved: Critical security patch required (Score > 9.0)."
        else:
            return False, f"Denied: Critical CVE detected (Score: {cve_score}), but action is '{action}' instead of 'emergency_patch'."
    return False, f"Denied: Security score {cve_score} does not meet critical emergency patch threshold > 9.0."

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
    current_hour = datetime.now().hour
    
    # Allow payload override for testing/simulation
    if "hour" in payload:
        try:
            current_hour = int(payload["hour"])
        except ValueError:
            pass
            
    # Window: 9:00 (9) to 17:00 (17)
    if 9 <= current_hour < 17:
        return False, f"Denied: Operations blocked during maintenance window (9am-5pm). Current hour: {current_hour}."
    
    return True, f"Approved: Operation allowed outside maintenance window. Current hour: {current_hour}."

def evaluate_request(request: PolicyRequest) -> tuple[bool, str]:
    # 1. Route legacy categories
    if request.category == PolicyCategory.SECURITY:
        return evaluate_security_patch_deployment(request.payload)
    elif request.category == PolicyCategory.DEPLOYMENT:
        return evaluate_deployment(request.payload)
    elif request.category == PolicyCategory.OPERATIONS:
        return evaluate_operations(request.payload)

    # 2. Route new 5 ZT categories via simple rules registry
    category = request.category.value
    subcategory = request.payload.get("subcategory", "")
    risk_level = request.payload.get("risk_level", "low")
    rule_key = f"{category}:{subcategory}:{risk_level}"

    if rule_key in SIMPLE_RULES:
        rule = SIMPLE_RULES[rule_key]
        decision = rule.get("decision", "DENY")
        reason = rule.get("reason", f"Simple rule matched: {rule_key}")
        
        # Enforce basic conditions checking
        agent_tier = request.payload.get("agent_tier", "tier1")
        namespace = request.payload.get("namespace", "dev")

        if rule.get("escalate", False):
            return False, f"Denied: Request escalates to large model: {reason}"

        # Tier validation
        if "agent_tier >= tier2" in rule.get("conditions", []) and agent_tier == "tier1":
            return False, f"Denied: Agent tier insufficient for operation. Requires tier2, got {agent_tier}."
        if "agent_tier >= tier3" in rule.get("conditions", []) and agent_tier in ["tier1", "tier2"]:
            return False, f"Denied: Agent tier insufficient for operation. Requires tier3, got {agent_tier}."
        if "agent_tier == tier4" in rule.get("conditions", []) and agent_tier != "tier4":
            return False, f"Denied: Agent tier insufficient for operation. Requires tier4, got {agent_tier}."
        
        # Namespace validation
        if "namespace != production" in rule.get("conditions", []) and namespace in ["production", "prod"]:
            return False, "Denied: Operation not allowed in production namespace."

        if decision == "ALLOW":
            return True, f"Approved: {reason}"
        else:
            return False, f"Denied: {reason}"

    # Default deny for safety (fail-closed)
    return False, f"Denied: No simple rule found matching '{rule_key}'."
