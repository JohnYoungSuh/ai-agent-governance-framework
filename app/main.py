import jwt
import datetime
from fastapi import FastAPI, HTTPException, status
from typing import Dict, Any

from app.policy_engine import PolicyRequest, PolicyResponse, evaluate_request, PolicyCategory

app = FastAPI(title="Governance Policy Inquiry Service (GPIS)", version="3.0.0")

# SECRET KEY for signing JWTs (in production, use environment variables)
SECRET_KEY = "suhlabs-super-secret-governance-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/api/v1/authorize", response_model=PolicyResponse)
async def authorize(request: PolicyRequest):
    """
    Universal Policy Decision Point (PDP) Endpoint.
    Routes requests to the correct evaluation logic based on category.
    """
    
    # 1. Evaluate the request
    is_allowed, reason = evaluate_request(request)
    
    if not is_allowed:
        # Return 403 Forbidden with specific reason
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "allowed": False,
                "reason": reason,
                "agent_id": request.agent_id
            }
        )
    
    # 2. If Allowed, generate Signed JWT
    token_payload = {
        "sub": request.agent_id,
        "category": request.category.value,
        "authorized": True
    }
    access_token = create_access_token(token_payload)
    
    return PolicyResponse(
        allowed=True,
        reason=reason,
        token=access_token
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
