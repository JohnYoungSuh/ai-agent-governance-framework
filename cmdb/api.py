#!/usr/bin/env python3
"""
CMDB REST API
AI Agent Governance Framework - Internal v2.1
Control: CM-2, CM-3, CM-6, CM-8

FastAPI REST API for Configuration Management Database
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

from schemas import (
    ConfigurationItem,
    AIAgentCI,
    ConfigurationBaseline,
    SecurityBaseline,
    ComplianceBaseline,
    PerformanceBaseline,
    ChangeRequest,
    DriftReport,
    BaselineType,
    BaselineStatus,
    CIType,
    Environment
)
from itsi_schemas import (
    ITSIService,
    ITSIKPI,
    ITSIEntity,
    ServiceHealth,
    KPIThresholdLevel
)
from client import CMDBClient

# Initialize FastAPI
app = FastAPI(
    title="CMDB API",
    description="Configuration Management Database API for AI Agent Governance Framework",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
CMDB_DATABASE = os.getenv("CMDB_DATABASE", "cmdb")


def get_cmdb_client() -> CMDBClient:
    """Dependency injection for CMDB client"""
    client = CMDBClient(mongodb_uri=MONGODB_URI, database=CMDB_DATABASE)
    try:
        yield client
    finally:
        client.close()


def verify_api_key(x_api_key: str = Header(...)) -> str:
    """
    Verify API key for authentication
    In production, validate against secure key store
    """
    expected_key = os.getenv("CMDB_API_KEY", "dev-api-key-12345")
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CMDB API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/stats")
async def get_statistics(cmdb: CMDBClient = Depends(get_cmdb_client)):
    """Get CMDB statistics"""
    try:
        stats = cmdb.get_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Configuration Items (CI) Endpoints
# ============================================================================

@app.post("/api/v1/ci", status_code=status.HTTP_201_CREATED)
async def create_ci(
    ci: ConfigurationItem,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new Configuration Item

    Requires API key authentication
    """
    try:
        ci_id = cmdb.create_ci(ci)
        return {"ci_id": ci_id, "message": "CI created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ci/{ci_id}")
async def get_ci(
    ci_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """Get Configuration Item by ID"""
    ci = cmdb.get_ci(ci_id)
    if not ci:
        raise HTTPException(status_code=404, detail=f"CI {ci_id} not found")
    return JSONResponse(content=ci)


@app.put("/api/v1/ci/{ci_id}")
async def update_ci(
    ci_id: str,
    updates: Dict[str, Any],
    jira_cr_id: Optional[str] = None,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Update Configuration Item

    Requires API key authentication
    """
    try:
        success = cmdb.update_ci(ci_id, updates, jira_cr_id)
        if success:
            return {"message": "CI updated successfully", "ci_id": ci_id}
        else:
            raise HTTPException(status_code=404, detail=f"CI {ci_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ci")
async def list_cis(
    ci_type: Optional[CIType] = None,
    environment: Optional[Environment] = None,
    tier: Optional[int] = None,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    List Configuration Items with filters

    Query Parameters:
    - ci_type: Filter by CI type (ai_agent, infrastructure, service, etc.)
    - environment: Filter by environment (development, staging, production)
    - tier: Filter by tier (1-4)
    """
    try:
        cis = cmdb.list_cis(
            ci_type=ci_type.value if ci_type else None,
            environment=environment.value if environment else None,
            tier=tier
        )
        return JSONResponse(content={"count": len(cis), "items": cis})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/ci/{ci_id}")
async def delete_ci(
    ci_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete Configuration Item

    Requires API key authentication
    """
    success = cmdb.delete_ci(ci_id)
    if success:
        return {"message": "CI deleted successfully", "ci_id": ci_id}
    else:
        raise HTTPException(status_code=404, detail=f"CI {ci_id} not found")


# ============================================================================
# Baseline Endpoints
# ============================================================================

@app.post("/api/v1/baseline", status_code=status.HTTP_201_CREATED)
async def create_baseline(
    baseline: Dict[str, Any],  # Accept generic dict, parse based on type
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new baseline

    Accepts any baseline type (configuration, security, compliance, performance)
    """
    try:
        # Parse based on baseline_type
        baseline_type = baseline.get('baseline_type')

        if baseline_type == 'configuration':
            baseline_obj = ConfigurationBaseline(**baseline)
        elif baseline_type == 'security':
            baseline_obj = SecurityBaseline(**baseline)
        elif baseline_type == 'compliance':
            baseline_obj = ComplianceBaseline(**baseline)
        elif baseline_type == 'performance':
            baseline_obj = PerformanceBaseline(**baseline)
        else:
            raise ValueError(f"Invalid baseline type: {baseline_type}")

        baseline_id = cmdb.create_baseline(baseline_obj)
        return {"baseline_id": baseline_id, "message": "Baseline created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/baseline/{baseline_id}")
async def get_baseline(
    baseline_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """Get baseline by ID"""
    baseline = cmdb.get_baseline(baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail=f"Baseline {baseline_id} not found")
    return JSONResponse(content=baseline)


@app.get("/api/v1/baseline/current/{ci_id}")
async def get_current_baseline(
    ci_id: str,
    baseline_type: BaselineType = BaselineType.CONFIGURATION,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """Get current approved baseline for a CI"""
    baseline = cmdb.get_current_baseline(ci_id, baseline_type)
    if not baseline:
        raise HTTPException(
            status_code=404,
            detail=f"No approved {baseline_type.value} baseline found for CI {ci_id}"
        )
    return JSONResponse(content=baseline)


@app.post("/api/v1/baseline/{baseline_id}/approve")
async def approve_baseline(
    baseline_id: str,
    approver: str,
    signature: Optional[str] = None,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Approve a baseline

    Requires API key authentication
    """
    success = cmdb.approve_baseline(baseline_id, approver, signature)
    if success:
        return {"message": "Baseline approved successfully", "baseline_id": baseline_id}
    else:
        raise HTTPException(status_code=404, detail=f"Baseline {baseline_id} not found")


@app.get("/api/v1/baseline")
async def list_baselines(
    ci_id: Optional[str] = None,
    baseline_type: Optional[BaselineType] = None,
    status: Optional[BaselineStatus] = None,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    List baselines with filters

    Query Parameters:
    - ci_id: Filter by CI
    - baseline_type: Filter by type
    - status: Filter by status
    """
    baselines = cmdb.list_baselines(ci_id, baseline_type, status)
    return JSONResponse(content={"count": len(baselines), "items": baselines})


# ============================================================================
# Change Request Endpoints
# ============================================================================

@app.post("/api/v1/change-request", status_code=status.HTTP_201_CREATED)
async def create_change_request(
    cr: ChangeRequest,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a change request

    Requires API key authentication
    """
    try:
        cr_id = cmdb.create_change_request(cr)
        return {"cr_id": cr_id, "message": "Change request created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/change-request/{cr_id}")
async def get_change_request(
    cr_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """Get change request by ID"""
    cr = cmdb.get_change_request(cr_id)
    if not cr:
        raise HTTPException(status_code=404, detail=f"Change request {cr_id} not found")
    return JSONResponse(content=cr)


@app.post("/api/v1/change-request/{cr_id}/actual")
async def record_actual_change(
    cr_id: str,
    actual_change: Dict[str, Any],
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Record actual change after implementation

    Calculates variance and tit-for-tat accuracy score
    """
    try:
        success = cmdb.record_actual_change(cr_id, actual_change)
        if success:
            return {"message": "Actual change recorded successfully", "cr_id": cr_id}
        else:
            raise HTTPException(status_code=404, detail=f"Change request {cr_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Drift Detection Endpoints
# ============================================================================

@app.post("/api/v1/drift/detect/{ci_id}")
async def detect_drift(
    ci_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Detect configuration drift for a CI

    Compares current configuration with baseline
    """
    try:
        drift_report = cmdb.detect_drift(ci_id)
        if drift_report:
            return JSONResponse(content={
                "drift_detected": True,
                "drift_report": drift_report.model_dump(mode='json')
            })
        else:
            return JSONResponse(content={
                "drift_detected": False,
                "message": "No drift detected"
            })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/drift")
async def get_drift_reports(
    ci_id: Optional[str] = None,
    severity: Optional[str] = None,
    remediation_required: Optional[bool] = None,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    Get drift reports with filters

    Query Parameters:
    - ci_id: Filter by CI
    - severity: Filter by severity (low, medium, high, critical)
    - remediation_required: Filter by remediation status
    """
    reports = cmdb.get_drift_reports(ci_id, severity, remediation_required)
    return JSONResponse(content={"count": len(reports), "items": reports})


# ============================================================================
# Graph Query Endpoints
# ============================================================================

@app.get("/api/v1/graph/relationships/{ci_id}")
async def get_ci_relationships(
    ci_id: str,
    relationship_type: Optional[str] = None,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    Get CI relationships (graph traversal)

    Query Parameters:
    - relationship_type: Filter by relationship type
    """
    relationships = cmdb.get_ci_relationships(ci_id, relationship_type)
    return JSONResponse(content={"count": len(relationships), "relationships": relationships})


@app.get("/api/v1/graph/control/{control_id}")
async def find_cis_implementing_control(
    control_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    Find all CIs implementing a specific control

    Example: control_id = "CM-2" or "SEC-001"
    """
    cis = cmdb.find_cis_implementing_control(control_id)
    return JSONResponse(content={"count": len(cis), "items": cis})


# ============================================================================
# Comparison Endpoints
# ============================================================================

@app.post("/api/v1/compare")
async def compare_configurations(
    ci_id: str,
    baseline_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    Compare current CI configuration with a baseline

    Returns detailed differences
    """
    try:
        ci = cmdb.get_ci(ci_id)
        if not ci:
            raise HTTPException(status_code=404, detail=f"CI {ci_id} not found")

        baseline = cmdb.get_baseline(baseline_id)
        if not baseline:
            raise HTTPException(status_code=404, detail=f"Baseline {baseline_id} not found")

        differences = cmdb._compare_configurations(
            baseline['configuration_snapshot'],
            ci['configuration']
        )

        return JSONResponse(content={
            "ci_id": ci_id,
            "baseline_id": baseline_id,
            "has_differences": len(differences) > 0,
            "difference_count": len(differences),
            "differences": differences
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ITSI Service Endpoints
# ============================================================================

@app.post("/api/v1/itsi/services", status_code=status.HTTP_201_CREATED)
async def create_itsi_service(
    service: ITSIService,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Create ITSI service

    Links to CMDB CIs via cmdb_ci_ids field
    """
    try:
        service_id = cmdb.create_itsi_service(service)
        return {"message": "Service created successfully", "service_id": service_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/itsi/services/{service_id}")
async def get_itsi_service(
    service_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """Get ITSI service by ID"""
    service = cmdb.get_itsi_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
    return JSONResponse(content=service)


@app.get("/api/v1/itsi/services")
async def list_itsi_services(
    criticality: Optional[str] = None,
    tier: Optional[int] = None,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    List ITSI services with filters

    Query Parameters:
    - criticality: Filter by criticality (low, medium, high, critical)
    - tier: Filter by agent tier (1-4)
    """
    services = cmdb.list_itsi_services(criticality, tier)
    return JSONResponse(content={"count": len(services), "items": services})


@app.patch("/api/v1/itsi/services/{service_id}/health")
async def update_service_health(
    service_id: str,
    health_score: float,
    health_status: ServiceHealth,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Update ITSI service health

    Body:
    - health_score: Health score (0-100)
    - health_status: ServiceHealth enum (normal, warning, critical, unknown)
    """
    try:
        success = cmdb.update_service_health(service_id, health_score, health_status)
        if success:
            return {"message": "Service health updated", "service_id": service_id}
        else:
            raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ITSI KPI Endpoints
# ============================================================================

@app.post("/api/v1/itsi/kpis", status_code=status.HTTP_201_CREATED)
async def create_itsi_kpi(
    kpi: ITSIKPI,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Create ITSI KPI

    Links to CMDB baselines via baseline_id field
    """
    try:
        kpi_id = cmdb.create_itsi_kpi(kpi)
        return {"message": "KPI created successfully", "kpi_id": kpi_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/itsi/kpis/{kpi_id}/measure")
async def record_kpi_measurement(
    kpi_id: str,
    value: float,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Record KPI measurement

    Evaluates thresholds and creates Splunk event
    """
    try:
        result = cmdb.record_kpi_measurement(kpi_id, value)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/itsi/services/{service_id}/kpis")
async def get_kpi_status(
    service_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    Get current status of all KPIs for a service

    Returns KPI values, status, and baseline deviations
    """
    try:
        statuses = cmdb.get_kpi_status(service_id)
        return JSONResponse(content={"count": len(statuses), "kpis": statuses})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ITSI Entity Endpoints
# ============================================================================

@app.post("/api/v1/itsi/entities", status_code=status.HTTP_201_CREATED)
async def create_itsi_entity(
    entity: ITSIEntity,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Create ITSI entity

    Links to CMDB CI via cmdb_ci_id field
    """
    try:
        entity_id = cmdb.create_itsi_entity(entity)
        return {"message": "Entity created successfully", "entity_id": entity_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/itsi/entities/{entity_id}/link/{service_id}")
async def link_entity_to_service(
    entity_id: str,
    service_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """Link entity to service"""
    try:
        success = cmdb.link_entity_to_service(entity_id, service_id)
        if success:
            return {"message": "Entity linked to service", "entity_id": entity_id, "service_id": service_id}
        else:
            return {"message": "Already linked or not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/itsi/services/{service_id}/entities")
async def get_service_entities(
    service_id: str,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """Get all entities for a service"""
    try:
        entities = cmdb.get_service_entities(service_id)
        return JSONResponse(content={"count": len(entities), "entities": entities})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ITSI Event Endpoints (for Splunk ingestion)
# ============================================================================

@app.get("/api/v1/itsi/events")
async def get_pending_itsi_events(
    limit: int = 100,
    cmdb: CMDBClient = Depends(get_cmdb_client)
):
    """
    Get pending ITSI events for Splunk HEC ingestion

    Query Parameters:
    - limit: Maximum number of events to retrieve (default 100)
    """
    try:
        events = cmdb.get_pending_itsi_events(limit)
        return JSONResponse(content={"count": len(events), "events": events})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/itsi/events/mark_ingested")
async def mark_events_ingested(
    event_ids: List[str],
    cmdb: CMDBClient = Depends(get_cmdb_client),
    api_key: str = Depends(verify_api_key)
):
    """
    Mark events as ingested by Splunk

    Body: List of event IDs that have been successfully ingested
    """
    try:
        count = cmdb.mark_events_ingested(event_ids)
        return {"message": f"Marked {count} events as ingested", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
