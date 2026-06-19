import os
import jwt
import datetime
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status, Request

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.policy_engine import PolicyRequest, PolicyResponse, evaluate_request

SUSPENSIONS: Dict[str, Dict[str, Any]] = {}

# Ensure secret key is retrieved from environment (SEC-001 / LL-001)
SECRET_KEY = os.getenv("GPIS_JWT_SECRET")  # raise
if not SECRET_KEY:
    # Set a fallback only if not in production to allow tests to run
    if os.getenv("ENVIRONMENT") == "production":  # assert
        raise RuntimeError("GPIS_JWT_SECRET environment variable is not set!")
    else:
        SECRET_KEY = "suhlabs-super-secret-governance-key"

ALGORITHM = "HS256"

# Rate Limiter setup (SEC-003)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Governance Policy Inquiry Service (GPIS)", version="3.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Redis client for Budget PIP (Component 10C)
redis_client = None
redis_host = os.getenv("REDIS_HOST", "localhost")  # assert
redis_port = int(os.getenv("REDIS_PORT", 6379))  # assert
try:
    import redis
    redis_client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=1)
    redis_client.ping()
except Exception:
    redis_client = None

def check_budget_pip(agent_id: str) -> tuple[str, bool]:
    """
    Checks rolling 24h token count against agent daily limits (Component 10C)
    """
    # Budgets: Security: 25K, IT-Ops: 50K, AI: 133K, Architect: 58K
    budgets = {
        "security-agent": 25000,
        "it-ops-agent": 50000,
        "ai-agent": 133000,
        "architect-agent": 58000
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
    elif pct >= 95:
        return "BUDGET_CRITICAL", True
    elif pct >= 80:
        return "BUDGET_WARNING", True
    return "BUDGET_OK", True

def get_tier_ttl(tier: str) -> datetime.timedelta:
    """Returns signed token TTL based on agent tier (GPIS-003)"""
    if tier == "tier3":
        return datetime.timedelta(minutes=5)
    elif tier == "tier4":
        return datetime.timedelta(minutes=2)
    else:
        return datetime.timedelta(minutes=15)

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_jira_approval(jira_cr_id: str) -> bool:
    """Simulates Jira CR validation with signature verification placeholder"""
    if not jira_cr_id:
        return False
    if "denied" in jira_cr_id.lower() or "expired" in jira_cr_id.lower():
        return False
    return True

@app.post("/api/v1/authorize", response_model=PolicyResponse)
@limiter.limit("100/minute")
async def authorize(policy_req: PolicyRequest, request: Request):
    """
    Universal Policy Decision Point (PDP) Endpoint.
    Routes requests to the correct evaluation logic based on category.
    """
    
    # 1. Budget PIP Check (Component 10C)
    budget_status, budget_allowed = check_budget_pip(policy_req.agent_id)
    if not budget_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "allowed": False,
                "reason": "Denied: Daily token budget exceeded (100% boundary breach).",
                "agent_id": policy_req.agent_id
            }
        )

    # 1b. Check active suspensions (Component 9E / 10E)
    for susp_token, susp_data in SUSPENSIONS.items():
        if susp_data.get("agent_id") == policy_req.agent_id and susp_data.get("status") == "SUSPENDED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "allowed": False,
                    "reason": f"Denied: Agent '{policy_req.agent_id}' is currently SUSPENDED pending human PA review.",
                    "agent_id": policy_req.agent_id
                }
            )

    # 2. Jira CR Check for Tier 3/4 (GPIS-003)
    agent_tier = policy_req.payload.get("agent_tier", "tier1")
    if agent_tier in ["tier3", "tier4"]:
        jira_cr_id = policy_req.payload.get("jira_cr_id")
        if not jira_cr_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "allowed": False,
                    "reason": "Denied: Jira CR ID is required for Tier 3/4 operations.",
                    "agent_id": policy_req.agent_id
                }
            )
        if not validate_jira_approval(jira_cr_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "allowed": False,
                    "reason": f"Denied: Jira CR '{jira_cr_id}' is not approved or is expired.",
                    "agent_id": policy_req.agent_id
                }
            )

    # 3. Evaluate the request
    is_allowed, reason = evaluate_request(policy_req)

    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "allowed": False,
                "reason": reason,
                "agent_id": policy_req.agent_id
            }
        )
    
    # 3. If Allowed, generate Signed JWT with detailed claims
    agent_tier = policy_req.payload.get("agent_tier", "tier1")
    expires_delta = get_tier_ttl(agent_tier)
    
    token_payload = {
        "sub": policy_req.agent_id,
        "category": policy_req.category.value,
        "authorized": True,
        "tier": agent_tier,
        "namespace": policy_req.payload.get("namespace", "dev"),
        "jira_cr_id": policy_req.payload.get("jira_cr_id"),
        "budget_status": budget_status
    }
    
    access_token = create_access_token(token_payload, expires_delta)
    
    # Append budget warnings if any
    final_reason = reason
    if budget_status != "BUDGET_OK":
        final_reason = f"{reason} [Warning: {budget_status} limit threshold crossed]"

    return PolicyResponse(
        allowed=True,
        reason=final_reason,
        token=access_token
    )

@app.get("/api/v1/verify")
async def verify_token(token: str):
    """Verify signed authorization JWT tokens (GPIS-003)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "payload": payload}
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.0.0"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

@app.get("/api/v1/suspension/{token}/status")
async def get_suspension_status(token: str):
    if token not in SUSPENSIONS:
        raise HTTPException(status_code=404, detail="Suspension token not found")
    return SUSPENSIONS[token]

@app.post("/admin/v1/suspend/{agent_id}")
async def suspend_agent(agent_id: str):
    token = str(uuid.uuid4())
    SUSPENSIONS[token] = {
        "status": "SUSPENDED",
        "agent_id": agent_id,
        "approval_window": "4h",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    return {"token": token, "status": "SUSPENDED"}

@app.post("/admin/v1/approve/{token}")
async def approve_suspension(token: str):
    if token not in SUSPENSIONS:
        raise HTTPException(status_code=404, detail="Suspension token not found")
    SUSPENSIONS[token]["status"] = "APPROVED"
    return {"token": token, "status": "APPROVED"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

