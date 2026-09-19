import os
import jwt
import datetime
import uuid
from typing import Dict, Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status, Request

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.audit import emit_audit_event
from app.policy_engine import (
    PolicyRequest,
    PolicyResponse,
    RULES_PATH,
    SIMPLE_RULES,
    evaluate_request,
)

SUSPENSIONS: Dict[str, Dict[str, Any]] = {}

FORBIDDEN_JWT_DEFAULTS = {
    "dev-gpis-jwt-secret-key-change-in-prod",
    "suhlabs-super-secret-governance-key",
}

ALGORITHM = "HS256"

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Governance Policy Inquiry Service (GPIS)", version="3.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

redis_client = None
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
try:
    import redis

    redis_client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=1)
    redis_client.ping()
except Exception:
    redis_client = None


def get_jwt_secret() -> str:
    """Fail-closed: no default signing key (SEC-001)."""
    secret = os.getenv("GPIS_JWT_SECRET")
    if not secret:
        raise RuntimeError("GPIS_JWT_SECRET environment variable is required and not set.")
    if secret in FORBIDDEN_JWT_DEFAULTS:
        raise RuntimeError("GPIS_JWT_SECRET must not use a published default value.")
    return secret


def get_admin_api_key() -> str:
    key = os.getenv("GPIS_ADMIN_API_KEY")
    if not key:
        raise RuntimeError("GPIS_ADMIN_API_KEY environment variable is required and not set.")
    return key


@app.on_event("startup")
def _require_runtime_secrets() -> None:
    get_jwt_secret()
    get_admin_api_key()


def require_admin_key(x_gpis_admin_key: Optional[str] = Header(default=None, alias="X-GPIS-Admin-Key")) -> None:
    try:
        expected = get_admin_api_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    if not x_gpis_admin_key or x_gpis_admin_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
        )


def check_budget_pip(agent_id: str) -> tuple[str, bool]:
    budgets = {
        "security-agent": 25000,
        "it-ops-agent": 50000,
        "ai-agent": 133000,
        "architect-agent": 58000,
    }
    limit = budgets.get(agent_id, 25000)

    redis_key = f"agent_budget:{agent_id}:tokens:rolling_24h"
    current_tokens = 0
    if redis_client:
        try:
            val = redis_client.get(redis_key)
            if val:
                current_tokens = int(val)
        except Exception:
            pass

    pct = (current_tokens / limit) * 100 if limit > 0 else 0
    if pct >= 100:
        return "BUDGET_EXCEEDED", False
    if pct >= 95:
        return "BUDGET_CRITICAL", True
    if pct >= 80:
        return "BUDGET_WARNING", True
    return "BUDGET_OK", True


def get_tier_ttl(tier: str) -> datetime.timedelta:
    if tier == "tier3":
        return datetime.timedelta(minutes=5)
    if tier == "tier4":
        return datetime.timedelta(minutes=2)
    return datetime.timedelta(minutes=15)


def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, get_jwt_secret(), algorithm=ALGORITHM)


def validate_jira_approval(jira_cr_id: str) -> bool:
    if not jira_cr_id:
        return False
    if "denied" in jira_cr_id.lower() or "expired" in jira_cr_id.lower():
        return False
    return True


def _audit_or_raise(
    policy_req: PolicyRequest,
    *,
    action: str,
    workflow_step: str,
    compliance_result: str,
    reason: str,
    outputs: Optional[Dict[str, Any]] = None,
) -> str:
    try:
        return emit_audit_event(
            actor=policy_req.agent_id,
            action=action,
            workflow_step=workflow_step,
            compliance_result=compliance_result,
            reason=reason,
            inputs={
                "category": policy_req.category.value,
                "payload": policy_req.payload,
            },
            outputs=outputs or {},
            policy_controls_checked=["AC-6", "AU-2"],
            jira_cr_id=policy_req.payload.get("jira_cr_id"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "allowed": False,
                "reason": f"Denied: audit-trail emit failed ({exc}).",
                "agent_id": policy_req.agent_id,
            },
        ) from exc


def _deny(policy_req: PolicyRequest, reason: str, workflow_step: str = "authorize-deny") -> None:
    audit_id = _audit_or_raise(
        policy_req,
        action="authorize",
        workflow_step=workflow_step,
        compliance_result="fail",
        reason=reason,
        outputs={"allowed": False},
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "allowed": False,
            "reason": reason,
            "agent_id": policy_req.agent_id,
            "audit_id": audit_id,
        },
    )


@app.post("/api/v1/authorize", response_model=PolicyResponse)
@limiter.limit("100/minute")
async def authorize(policy_req: PolicyRequest, request: Request):
    budget_status, budget_allowed = check_budget_pip(policy_req.agent_id)
    if not budget_allowed:
        _deny(
            policy_req,
            "Denied: Daily token budget exceeded (100% boundary breach).",
            "budget-pip",
        )

    for _susp_token, susp_data in SUSPENSIONS.items():
        if susp_data.get("agent_id") == policy_req.agent_id and susp_data.get("status") == "SUSPENDED":
            _deny(
                policy_req,
                f"Denied: Agent '{policy_req.agent_id}' is currently SUSPENDED pending human PA review.",
                "kill-switch",
            )

    agent_tier = str(policy_req.payload.get("agent_tier", "tier1"))
    if agent_tier in ["tier3", "tier4", "3", "4"]:
        jira_cr_id = policy_req.payload.get("jira_cr_id")
        if not jira_cr_id:
            _deny(policy_req, "Denied: Jira CR ID is required for Tier 3/4 operations.", "jira-cr")
        if not validate_jira_approval(str(jira_cr_id)):
            _deny(
                policy_req,
                f"Denied: Jira CR '{jira_cr_id}' is not approved or is expired.",
                "jira-cr",
            )

    is_allowed, reason = evaluate_request(policy_req)
    if not is_allowed:
        _deny(policy_req, reason, "policy-evaluate")

    expires_delta = get_tier_ttl(agent_tier if agent_tier.startswith("tier") else f"tier{agent_tier}")
    token_payload = {
        "sub": policy_req.agent_id,
        "category": policy_req.category.value,
        "authorized": True,
        "tier": agent_tier,
        "namespace": policy_req.payload.get("namespace", "dev"),
        "jira_cr_id": policy_req.payload.get("jira_cr_id"),
        "budget_status": budget_status,
        "guardrails_enforced": True,
    }
    access_token = create_access_token(token_payload, expires_delta)

    final_reason = reason
    if budget_status != "BUDGET_OK":
        final_reason = f"{reason} [Warning: {budget_status} limit threshold crossed]"

    compliance = "warning" if budget_status != "BUDGET_OK" else "pass"
    audit_id = _audit_or_raise(
        policy_req,
        action="authorize",
        workflow_step="authorize-allow",
        compliance_result=compliance,
        reason=final_reason,
        outputs={"allowed": True},
    )

    return PolicyResponse(
        allowed=True,
        reason=final_reason,
        token=access_token,
        audit_id=audit_id,
    )


@app.get("/api/v1/verify")
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[ALGORITHM])
        return {"valid": True, "payload": payload}
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


def _health_body() -> dict:
    return {"status": "healthy", "version": "3.0.0"}


def _ready_body() -> dict:
    if not RULES_PATH.exists() or not SIMPLE_RULES:
        raise HTTPException(status_code=503, detail="Policy rules not loaded")
    try:
        get_jwt_secret()
        get_admin_api_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ready"}


@app.get("/health")
async def health():
    return _health_body()


@app.get("/health/live")
async def health_live():
    return _health_body()


@app.get("/ready")
async def ready():
    return _ready_body()


@app.get("/health/ready")
async def health_ready():
    return _ready_body()


@app.get("/health/startup")
async def health_startup():
    return {"status": "started"}


@app.get("/api/v1/suspension/{token}/status")
async def get_suspension_status(token: str):
    if token not in SUSPENSIONS:
        raise HTTPException(status_code=404, detail="Suspension token not found")
    return SUSPENSIONS[token]


@app.post("/admin/v1/suspend/{agent_id}")
async def suspend_agent(agent_id: str, _: None = Depends(require_admin_key)):
    token = str(uuid.uuid4())
    SUSPENSIONS[token] = {
        "status": "SUSPENDED",
        "agent_id": agent_id,
        "approval_window": "4h",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    return {"token": token, "status": "SUSPENDED"}


@app.post("/admin/v1/approve/{token}")
async def approve_suspension(token: str, _: None = Depends(require_admin_key)):
    if token not in SUSPENSIONS:
        raise HTTPException(status_code=404, detail="Suspension token not found")
    SUSPENSIONS[token]["status"] = "APPROVED"
    return {"token": token, "status": "APPROVED"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
