#!/usr/bin/env python3
"""
ITSI (IT Service Intelligence) Schemas
AI Agent Governance Framework - Internal v2.1

Integrates Splunk ITSI concepts:
- Services: Business or technical services
- KPIs: Key Performance Indicators
- Entities: Infrastructure components
- Event logs for ITSI ingestion
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class ServiceHealth(str, Enum):
    """ITSI Service health status"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class KPIThresholdLevel(str, Enum):
    """KPI threshold levels"""
    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EntityType(str, Enum):
    """ITSI Entity types"""
    AI_AGENT = "ai_agent"
    SERVER = "server"
    DATABASE = "database"
    APPLICATION = "application"
    NETWORK_DEVICE = "network_device"
    CONTAINER = "container"
    LAMBDA_FUNCTION = "lambda_function"


class KPIType(str, Enum):
    """KPI measurement types"""
    AVAILABILITY = "availability"
    PERFORMANCE = "performance"
    COST = "cost"
    QUALITY = "quality"
    SECURITY = "security"


# ============================================================================
# ITSI Service Model
# ============================================================================

class ServiceDependency(BaseModel):
    """Service dependency"""
    service_id: str
    service_name: str
    dependency_type: str  # depends_on, provides_to, peer


class ITSIService(BaseModel):
    """
    ITSI Service Model

    Represents a business or technical service monitored in Splunk ITSI
    Maps to CMDB CIs and tracks health via KPIs
    """
    service_id: str = Field(..., description="Unique service identifier")
    service_name: str
    description: Optional[str] = None

    # Service classification
    service_type: str  # business, technical, infrastructure
    tier: Optional[int] = Field(None, ge=1, le=4, description="Agent tier if applicable")
    criticality: str  # low, medium, high, critical

    # Service ownership
    owner: str  # email
    team: str
    on_call: Optional[str] = None

    # Service health
    health_score: float = Field(100.0, ge=0.0, le=100.0)
    health_status: ServiceHealth = ServiceHealth.NORMAL
    last_health_update: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    depends_on: List[ServiceDependency] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list, description="Entity IDs")
    kpis: List[str] = Field(default_factory=list, description="KPI IDs")

    # CMDB Integration
    cmdb_ci_ids: List[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "service_id": "SVC-AI-SECURITY-OPS",
                "service_name": "AI Security Operations Service",
                "service_type": "technical",
                "tier": 3,
                "criticality": "high",
                "owner": "security-team@suhlabs.com",
                "team": "Security Operations",
                "health_score": 95.5,
                "health_status": "normal",
                "entities": ["ENT-AGENT-001", "ENT-LAMBDA-001"],
                "kpis": ["KPI-AVAILABILITY", "KPI-LATENCY", "KPI-COST"],
                "cmdb_ci_ids": ["CI-2025-001"]
            }
        }


# ============================================================================
# ITSI KPI Model
# ============================================================================

class KPIThreshold(BaseModel):
    """KPI threshold definition"""
    level: KPIThresholdLevel
    operator: str  # gt, gte, lt, lte, eq
    value: float
    severity: int = Field(..., ge=1, le=10)


class KPIAggregation(BaseModel):
    """KPI aggregation method"""
    method: str  # avg, sum, count, max, min, p50, p95, p99
    field: str
    time_window: int = Field(..., description="Window in seconds")


class ITSIKPI(BaseModel):
    """
    ITSI Key Performance Indicator Model

    Defines measurable metrics for services
    Integrates with Splunk searches and CMDB baselines
    """
    kpi_id: str = Field(..., description="Unique KPI identifier")
    kpi_name: str
    description: Optional[str] = None

    # KPI classification
    kpi_type: KPIType
    service_id: str

    # Measurement
    unit: str  # %, ms, USD, requests/sec, etc.
    aggregation: KPIAggregation
    base_search: str  # Splunk SPL query

    # Thresholds
    thresholds: List[KPIThreshold]

    # Current state
    current_value: Optional[float] = None
    last_measured: Optional[datetime] = None
    status: KPIThresholdLevel = KPIThresholdLevel.NORMAL

    # Baseline integration
    baseline_value: Optional[float] = None
    baseline_id: Optional[str] = None  # Links to CMDB baseline

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    enabled: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "kpi_id": "KPI-LATENCY-P95",
                "kpi_name": "API Latency P95",
                "kpi_type": "performance",
                "service_id": "SVC-AI-SECURITY-OPS",
                "unit": "ms",
                "aggregation": {
                    "method": "p95",
                    "field": "response_time",
                    "time_window": 300
                },
                "base_search": "index=cmdb sourcetype=api_logs | stats p95(response_time) as latency_p95",
                "thresholds": [
                    {"level": "normal", "operator": "lte", "value": 500, "severity": 1},
                    {"level": "medium", "operator": "gt", "value": 500, "severity": 5},
                    {"level": "high", "operator": "gt", "value": 1000, "severity": 7},
                    {"level": "critical", "operator": "gt", "value": 2000, "severity": 10}
                ],
                "current_value": 450.0,
                "baseline_value": 400.0,
                "baseline_id": "BL-PERFORMANCE-2025-10-19-001"
            }
        }


# ============================================================================
# ITSI Entity Model
# ============================================================================

class EntityAlias(BaseModel):
    """Entity alias for identification"""
    alias_type: str  # hostname, ip, fqdn, ci_id
    value: str


class ITSIEntity(BaseModel):
    """
    ITSI Entity Model

    Represents infrastructure components
    Maps to CMDB CIs and provides context for events
    """
    entity_id: str = Field(..., description="Unique entity identifier")
    entity_name: str
    entity_type: EntityType

    # Entity details
    aliases: List[EntityAlias] = Field(default_factory=list)
    description: Optional[str] = None

    # Location/Environment
    environment: str  # development, staging, production
    region: Optional[str] = None
    availability_zone: Optional[str] = None

    # CMDB Integration
    cmdb_ci_id: Optional[str] = None

    # Service association
    services: List[str] = Field(default_factory=list, description="Service IDs")

    # Entity info fields (for Splunk correlation)
    info_fields: Dict[str, str] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "ENT-AGENT-001",
                "entity_name": "security-ops-agent",
                "entity_type": "ai_agent",
                "aliases": [
                    {"alias_type": "ci_id", "value": "CI-2025-001"},
                    {"alias_type": "hostname", "value": "security-ops-agent.suhlabs.local"}
                ],
                "environment": "production",
                "region": "us-east-1",
                "cmdb_ci_id": "CI-2025-001",
                "services": ["SVC-AI-SECURITY-OPS"],
                "info_fields": {
                    "tier": "3",
                    "model": "claude-sonnet-4-5-20250929",
                    "owner": "security-team@suhlabs.com"
                }
            }
        }


# ============================================================================
# ITSI Event Log Schemas (for Splunk HEC ingestion)
# ============================================================================

class ITSIServiceEvent(BaseModel):
    """
    ITSI Service Event for Splunk HEC ingestion

    Format compatible with Splunk HTTP Event Collector
    """
    time: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    host: str
    source: str = "cmdb_api"
    sourcetype: str = "itsi:service:event"
    index: str = "itsi"

    event: Dict[str, Any] = Field(..., description="Event payload")

    def to_hec_format(self) -> Dict[str, Any]:
        """Convert to Splunk HEC format"""
        return {
            "time": self.time,
            "host": self.host,
            "source": self.source,
            "sourcetype": self.sourcetype,
            "index": self.index,
            "event": self.event
        }


class ITSIKPIEvent(BaseModel):
    """ITSI KPI measurement event"""
    time: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    host: str
    source: str = "cmdb_api"
    sourcetype: str = "itsi:kpi:measurement"
    index: str = "itsi"

    event: Dict[str, Any]

    def to_hec_format(self) -> Dict[str, Any]:
        """Convert to Splunk HEC format"""
        return {
            "time": self.time,
            "host": self.host,
            "source": self.source,
            "sourcetype": self.sourcetype,
            "index": self.index,
            "event": self.event
        }


# ============================================================================
# ITSI Logging Helper Functions
# ============================================================================

def create_service_health_event(service: ITSIService) -> ITSIServiceEvent:
    """Create service health event for ITSI ingestion"""
    return ITSIServiceEvent(
        host="cmdb-api",
        event={
            "event_type": "service_health",
            "service_id": service.service_id,
            "service_name": service.service_name,
            "health_score": service.health_score,
            "health_status": service.health_status,
            "criticality": service.criticality,
            "owner": service.owner,
            "team": service.team,
            "kpi_count": len(service.kpis),
            "entity_count": len(service.entities),
            "cmdb_ci_ids": service.cmdb_ci_ids,
            "tags": service.tags
        }
    )


def create_kpi_measurement_event(kpi: ITSIKPI, value: float, status: KPIThresholdLevel) -> ITSIKPIEvent:
    """Create KPI measurement event for ITSI ingestion"""
    return ITSIKPIEvent(
        host="cmdb-api",
        event={
            "event_type": "kpi_measurement",
            "kpi_id": kpi.kpi_id,
            "kpi_name": kpi.kpi_name,
            "kpi_type": kpi.kpi_type,
            "service_id": kpi.service_id,
            "measurement_value": value,
            "unit": kpi.unit,
            "status": status,
            "baseline_value": kpi.baseline_value,
            "baseline_deviation": value - kpi.baseline_value if kpi.baseline_value else None,
            "baseline_id": kpi.baseline_id,
            "thresholds_breached": [
                t.level for t in kpi.thresholds
                if (t.operator == "gt" and value > t.value) or
                   (t.operator == "lt" and value < t.value)
            ]
        }
    )


def create_entity_discovery_event(entity: ITSIEntity) -> ITSIServiceEvent:
    """Create entity discovery event for ITSI ingestion"""
    return ITSIServiceEvent(
        host="cmdb-api",
        event={
            "event_type": "entity_discovery",
            "entity_id": entity.entity_id,
            "entity_name": entity.entity_name,
            "entity_type": entity.entity_type,
            "environment": entity.environment,
            "region": entity.region,
            "cmdb_ci_id": entity.cmdb_ci_id,
            "services": entity.services,
            "aliases": [{"type": a.alias_type, "value": a.value} for a in entity.aliases],
            "info_fields": entity.info_fields,
            "tags": entity.tags
        }
    )


# MongoDB Collection Names for ITSI
ITSI_COLLECTIONS = {
    "services": "itsi_services",
    "kpis": "itsi_kpis",
    "entities": "itsi_entities"
}
