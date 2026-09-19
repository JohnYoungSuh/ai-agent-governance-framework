import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

class PolicyCategory(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    ACCESS = "ACCESS"
    COMPLY = "COMPLY"
    ANY = "ANY"
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

    @field_validator("payload")
    @classmethod
    def validate_payload_size(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        encoded = json.dumps(v, default=str)
        if len(encoded) > 2048:
            raise ValueError("payload exceeds 2KB")
        return v


class PolicyResponse(BaseModel):
    allowed: bool
    reason: str
    token: Optional[str] = None
    audit_id: Optional[str] = None


RULES_PATH = Path(__file__).parent.parent / "policies" / "simple_rules.yml"
SIMPLE_RULES = yaml.safe_load(RULES_PATH.read_text()) if RULES_PATH.exists() else {}

TIER_RANK = {
    "tier1": 1,
    "t1": 1,
    "1": 1,
    "tier2": 2,
    "t2": 2,
    "2": 2,
    "tier3": 3,
    "t3": 3,
    "3": 3,
    "tier4": 4,
    "t4": 4,
    "4": 4,
}


def _tier_rank(tier: Any) -> int:
    key = str(tier).lower().replace(" ", "")
    return TIER_RANK.get(key, 0)


def _label_names(payload: Dict[str, Any]) -> List[str]:
    labels = payload.get("labels")
    if labels is None:
        return []
    if isinstance(labels, dict):
        return [str(k) for k in labels.keys()]
    if isinstance(labels, list):
        return [str(x) for x in labels]
    return [str(labels)]


def evaluate_condition(condition: str, payload: Dict[str, Any]) -> bool:
    """Fail-closed: unknown condition strings return False."""
    c = condition.strip()
    namespace = str(payload.get("namespace", "dev"))
    allowed_ns = str(payload.get("allowed_namespace", namespace))
    tier = payload.get("agent_tier", "tier1")
    path = str(payload.get("path", ""))

    if c == "namespace == agent.allowed_namespace":
        return bool(namespace) and namespace == allowed_ns
    if c.startswith("agent_tier >= "):
        required = c.split(">=", 1)[1].strip()
        return _tier_rank(tier) >= _tier_rank(required)
    if c.startswith("agent_tier == "):
        required = c.split("==", 1)[1].strip()
        return _tier_rank(tier) == _tier_rank(required)
    if c == "no PII or secrets in config":
        return not payload.get("contains_pii") and not payload.get("contains_secrets")
    if c.startswith("namespace in ["):
        inner = c[c.index("[") + 1 : c.index("]")]
        allowed = [x.strip() for x in inner.split(",")]
        return namespace in allowed
    if "path contains /tmp/ or /temp/" in c:
        return "/tmp/" in path or "/temp/" in path or path.startswith("/tmp") or path.startswith("/temp")
    if c == "namespace != production":
        return namespace not in ("production", "prod")
    if c == "backup_exists == true":
        return bool(payload.get("backup_exists"))
    if c == "resource_quota_ok == true":
        return bool(payload.get("resource_quota_ok"))
    if c.startswith("has labels"):
        labels = _label_names(payload)
        return all(name in labels for name in ("app", "env", "owner"))
    if c == "service_type != LoadBalancer":
        return str(payload.get("service_type", "ClusterIP")) != "LoadBalancer"
    if c == "namespace == dev":
        return namespace == "dev"
    if "cost_estimate < 100" in c:
        raw = payload.get("cost_estimate", payload.get("cost_estimate_usd", None))
        try:
            return float(raw) < 100
        except (TypeError, ValueError):
            return False
    if c == "read_only_operation == true":
        return bool(payload.get("read_only_operation"))
    return False


def evaluate_conditions(conditions: List[str], payload: Dict[str, Any]) -> Tuple[bool, str]:
    for condition in conditions or []:
        if not evaluate_condition(condition, payload):
            return False, condition
    return True, ""


def evaluate_security_patch_deployment(payload: Dict[str, Any]) -> tuple[bool, str]:
    """APPROVED if CVE score > 9.0 AND action == 'emergency_patch' (SEC-002)."""
    cve_score = payload.get("cve_score", 0.0)
    action = payload.get("action", "")
    if cve_score > 9.0:
        if action == "emergency_patch":
            return True, "Approved: Critical security patch required (Score > 9.0)."
        return False, (
            f"Denied: Critical CVE detected (Score: {cve_score}), "
            f"but action is '{action}' instead of 'emergency_patch'."
        )
    return False, (
        f"Denied: Security score {cve_score} does not meet critical emergency patch threshold > 9.0."
    )


def evaluate_deployment(payload: Dict[str, Any]) -> tuple[bool, str]:
    commit_signed = payload.get("commit_signed", False)
    if not commit_signed:
        return False, "Denied: Deployment blocked: Commit signature missing."
    return True, "Approved: Deployment authorized with signed commit."


def evaluate_operations(payload: Dict[str, Any]) -> tuple[bool, str]:
    current_hour = datetime.now().hour
    if "hour" in payload:
        try:
            current_hour = int(payload["hour"])
        except (TypeError, ValueError):
            pass
    if 9 <= current_hour < 17:
        return False, (
            f"Denied: Operations blocked during maintenance window (9am-5pm). Current hour: {current_hour}."
        )
    return True, f"Approved: Operation allowed outside maintenance window. Current hour: {current_hour}."


def evaluate_request(request: PolicyRequest) -> tuple[bool, str]:
    if request.category == PolicyCategory.SECURITY:
        return evaluate_security_patch_deployment(request.payload)
    if request.category == PolicyCategory.DEPLOYMENT:
        return evaluate_deployment(request.payload)
    if request.category == PolicyCategory.OPERATIONS:
        return evaluate_operations(request.payload)

    category = request.category.value
    subcategory = request.payload.get("subcategory", "")
    risk_level = request.payload.get("risk_level", "low")
    rule_key = f"{category}:{subcategory}:{risk_level}"

    if rule_key not in SIMPLE_RULES:
        return False, f"Denied: No simple rule found matching '{rule_key}'."

    rule = SIMPLE_RULES[rule_key]
    decision = rule.get("decision", "DENY")
    reason = rule.get("reason", f"Simple rule matched: {rule_key}")
    ok, failed = evaluate_conditions(rule.get("conditions") or [], request.payload)
    if not ok:
        return False, f"Denied: Condition not met ({failed})."

    if rule.get("escalate", False):
        return False, f"Denied: Pending human/LLM escalation (fail-closed): {reason}"

    if decision == "ALLOW":
        return True, f"Approved: {reason}"
    return False, f"Denied: {reason}"
