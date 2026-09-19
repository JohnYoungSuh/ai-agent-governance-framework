"""
IT-Ops Agent - API Server
Tier 3: IT operations automation and incident response
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import yaml

_shared = Path("/app/shared")
if _shared.is_dir():
    sys.path.insert(0, str(_shared))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from gpis_client import GpisAuthorizationError, require_gpis_token

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
incident_requests = Counter('ops_incident_requests_total', 'Total incident requests')
deployment_requests = Counter('ops_deployment_requests_total', 'Total deployment requests')
response_time = Histogram('ops_response_time_seconds', 'Incident response time')

app = FastAPI(
    title="IT-Ops Agent",
    description="AI Agent Governance Framework - IT Operations Agent API",
    version="1.0.0"
)

class IncidentRequest(BaseModel):
    severity: str  # P0, P1, P2, P3
    description: str
    auto_remediate: bool = False

class DeploymentRequest(BaseModel):
    environment: str  # dev, staging, prod
    application: str
    version: str
    commit_signed: bool = False
    jira_cr_id: Optional[str] = None


def _agent_tier() -> str:
    raw = os.getenv("AGENT_TIER", "3")
    return f"tier{raw}" if str(raw).isdigit() else str(raw)


def _authorize_or_raise(category: str, payload: dict) -> str:
    try:
        return require_gpis_token("it-ops-agent", category, payload)
    except GpisAuthorizationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.on_startup
async def startup_event():
    """Initialize agent on startup"""
    logger.info(f"Starting IT-Ops Agent v1.0.0")
    logger.info(f"Agent Tier: {os.getenv('AGENT_TIER', '3')}")
    logger.info(f"Framework Version: {os.getenv('FRAMEWORK_VERSION', '2.1.0')}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "it-ops-agent",
        "tier": os.getenv("AGENT_TIER", "3"),
        "framework_version": os.getenv("FRAMEWORK_VERSION", "2.1.0"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/live")
async def liveness_probe():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness_probe():
    return {"status": "ready"}

@app.get("/health/startup")
async def startup_probe():
    return {"status": "started"}

@app.post("/incidents")
async def handle_incident(request: IncidentRequest):
    """Handle incident response. Requires GPIS JWT."""
    payload = {
        "hour": datetime.utcnow().hour,
        "agent_tier": _agent_tier(),
        "jira_cr_id": os.getenv("JIRA_CR_ID", ""),
        "namespace": os.getenv("AGENT_NAMESPACE", "dev"),
    }
    _authorize_or_raise("OPERATIONS", payload)
    incident_requests.inc()

    logger.info(f"Handling {request.severity} incident: {request.description}")

    # Placeholder: actual incident handling logic
    incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    return {
        "incident_id": incident_id,
        "status": "acknowledged",
        "severity": request.severity,
        "auto_remediation": request.auto_remediate,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/deployments")
async def trigger_deployment(request: DeploymentRequest):
    """Trigger application deployment. Requires GPIS JWT."""
    payload = {
        "commit_signed": request.commit_signed,
        "agent_tier": _agent_tier(),
        "jira_cr_id": request.jira_cr_id or os.getenv("JIRA_CR_ID", ""),
        "namespace": request.environment,
    }
    _authorize_or_raise("DEPLOYMENT", payload)
    deployment_requests.inc()

    logger.info(f"Deploying {request.application} v{request.version} to {request.environment}")

    # Placeholder: actual deployment logic
    deployment_id = f"DEP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    return {
        "deployment_id": deployment_id,
        "status": "in_progress",
        "environment": request.environment,
        "application": request.application,
        "version": request.version,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
