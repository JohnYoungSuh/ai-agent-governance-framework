#!/usr/bin/env python3
"""
CMDB MongoDB Schemas
AI Agent Governance Framework - Internal v2.1
Control: CM-2, CM-3, CM-6, CM-8, AU-002

Common Data Model (CDM) for Configuration Items, Baselines, and Change Requests
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import hashlib
import json


class CIType(str, Enum):
    """Configuration Item types"""
    AI_AGENT = "ai_agent"
    INFRASTRUCTURE = "infrastructure"
    SERVICE = "service"
    RMF_CONTROL = "rmf_control"
    SECURITY_CONTROL = "security_control"


class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Criticality(str, Enum):
    """Criticality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RelationshipType(str, Enum):
    """Relationship types for graph visualization"""
    DEPENDS_ON = "DEPENDS_ON"
    IMPLEMENTS = "IMPLEMENTS"
    PART_OF = "PART_OF"
    VALIDATES = "VALIDATES"
    REFERENCES = "REFERENCES"
    SUPERSEDES = "SUPERSEDES"
    USES = "USES"
    MONITORS = "MONITORS"


class BaselineType(str, Enum):
    """Baseline types"""
    CONFIGURATION = "configuration"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"


class BaselineStatus(str, Enum):
    """Baseline status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


class Relationship(BaseModel):
    """CI relationship model"""
    type: RelationshipType
    target_ci_id: str
    target_name: str
    description: Optional[str] = None


class Signature(BaseModel):
    """Digital signature model"""
    algorithm: str = "RSA-SHA256"
    signed_by: str
    public_key_id: Optional[str] = None
    signed_at: datetime
    signature_value: str  # base64 encoded


class ChangeReference(BaseModel):
    """Last change reference"""
    jira_cr_id: str
    change_date: datetime
    change_type: str
    approver: str


class ConfigurationItem(BaseModel):
    """
    Configuration Item (CI) - Base model
    Represents any managed component in the system
    """
    ci_id: str = Field(..., description="Unique CI identifier")
    ci_type: CIType
    name: str
    description: Optional[str] = None

    # Classification
    tier: Optional[int] = Field(None, ge=1, le=4)
    environment: Environment
    criticality: Criticality

    # Metadata
    owner: str  # email
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"

    # Configuration data (flexible schema)
    configuration: Dict[str, Any] = Field(default_factory=dict)

    # Relationships (NoSQL pattern for graph)
    relationships: List[Relationship] = Field(default_factory=list)

    # Baseline references
    current_baseline_id: Optional[str] = None
    approved_baselines: List[str] = Field(default_factory=list)

    # Change tracking
    last_change_request: Optional[ChangeReference] = None

    # Cryptographic verification
    configuration_hash: Optional[str] = None
    signature: Optional[Signature] = None

    # Audit trail
    audit_trail_ids: List[str] = Field(default_factory=list)

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of configuration"""
        config_json = json.dumps(self.configuration, sort_keys=True, separators=(',', ':'))
        config_bytes = config_json.encode('utf-8')
        hash_hex = hashlib.sha256(config_bytes).hexdigest()
        return f"sha256:{hash_hex}"

    def update_hash(self):
        """Update configuration hash"""
        self.configuration_hash = self.calculate_hash()
        self.updated_at = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "ci_id": "CI-2025-001",
                "ci_type": "ai_agent",
                "name": "security-ops-agent",
                "tier": 3,
                "environment": "production",
                "criticality": "high",
                "owner": "security-team@suhlabs.com",
                "configuration": {
                    "model": "claude-sonnet-4-5-20250929",
                    "memory_mb": 1024,
                    "cost_budget_daily_usd": 100.0
                }
            }
        }


class AIAgentCI(ConfigurationItem):
    """AI Agent Configuration Item"""
    ci_type: CIType = CIType.AI_AGENT

    def __init__(self, **data):
        super().__init__(**data)
        # Validate AI agent specific fields
        required_fields = ["model", "provider", "tier"]
        for field in required_fields:
            if field not in self.configuration:
                raise ValueError(f"AI Agent CI must have '{field}' in configuration")


class ConfigurationBaseline(BaseModel):
    """Configuration Baseline Model"""
    baseline_id: str
    baseline_type: BaselineType = BaselineType.CONFIGURATION
    name: str
    description: Optional[str] = None

    # What is being baselined
    ci_id: str
    ci_name: str

    # Baseline metadata
    status: BaselineStatus = BaselineStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

    # Jira CR linkage
    jira_cr_id: Optional[str] = None
    jira_cr_url: Optional[str] = None

    # Snapshot of configuration
    configuration_snapshot: Dict[str, Any]

    # Cryptographic hash
    configuration_hash: str
    hash_algorithm: str = "SHA-256"

    # Digital signature
    signature: Optional[Signature] = None

    # Version control
    version: str = "1.0.0"
    previous_baseline_id: Optional[str] = None
    superseded_by: Optional[str] = None

    # Audit
    audit_trail_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "baseline_id": "BL-CONFIG-2025-10-19-001",
                "baseline_type": "configuration",
                "name": "Security Ops Agent v1.2.3 Production Config",
                "ci_id": "CI-2025-001",
                "ci_name": "security-ops-agent",
                "status": "approved",
                "configuration_snapshot": {
                    "model": "claude-sonnet-4-5-20250929",
                    "memory_mb": 1024
                },
                "configuration_hash": "sha256:a1b2c3d4..."
            }
        }


class SecurityControl(BaseModel):
    """Security control requirement"""
    control_id: str
    control_name: str
    status: str  # required, optional, not_applicable
    implementation: Dict[str, Any]
    validation: Dict[str, Any]


class SecurityBaseline(BaseModel):
    """Security Baseline Model - Required controls per tier"""
    baseline_id: str
    baseline_type: BaselineType = BaselineType.SECURITY
    name: str
    description: Optional[str] = None

    tier: int = Field(..., ge=1, le=4)
    environment: Environment

    required_controls: List[SecurityControl]

    configuration_hash: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class RMFControlImplementation(BaseModel):
    """RMF Control implementation details"""
    control_id: str  # e.g., "CM-2"
    control_name: str
    implementation_status: str  # not_implemented, planned, implemented, inherited
    responsible_role: str
    implementation_description: str
    evidence: List[str] = Field(default_factory=list)
    assessment: Optional[Dict[str, Any]] = None


class RMFControlFamily(BaseModel):
    """RMF Control family"""
    family_name: str
    controls: List[RMFControlImplementation]


class ComplianceBaseline(BaseModel):
    """Compliance Baseline Model - NIST 800-53 RMF control states"""
    baseline_id: str
    baseline_type: BaselineType = BaselineType.COMPLIANCE
    name: str
    description: Optional[str] = None

    framework: str = "NIST-800-53-Rev5"
    overlay: str  # FedRAMP-Moderate, AI-Specific, etc.

    control_families: Dict[str, RMFControlFamily]

    configuration_hash: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    cost: Dict[str, float]
    latency: Dict[str, float]
    quality: Dict[str, float]
    availability: Dict[str, float]


class PerformanceBaseline(BaseModel):
    """Performance Baseline Model - Cost, latency, quality metrics"""
    baseline_id: str
    baseline_type: BaselineType = BaselineType.PERFORMANCE
    name: str

    ci_id: str
    measurement_period: Dict[str, datetime]

    metrics: PerformanceMetrics

    # Thresholds for drift detection
    thresholds: Dict[str, float]

    configuration_hash: str


class PlannedChange(BaseModel):
    """Planned change details"""
    field: str
    old_value: Any
    new_value: Any
    justification: str
    estimated_impact: Dict[str, float]


class ActualChange(BaseModel):
    """Actual change details"""
    field: str
    old_value: Any
    new_value: Any
    implemented_at: datetime
    actual_impact: Dict[str, float]


class ChangeVariance(BaseModel):
    """Variance between planned and actual"""
    field_differences: List[str] = Field(default_factory=list)
    cost_variance_usd: float = 0.0
    performance_variance_percent: float = 0.0
    within_tolerance: bool = True


class TitForTatScore(BaseModel):
    """Tit-for-tat reputation scoring"""
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    contributes_to_reputation: bool = True
    agent_id: str
    proposal_id: Optional[str] = None


class Approval(BaseModel):
    """Change request approval"""
    approver: str
    approved_at: datetime
    signature: Optional[str] = None


class ChangeRequest(BaseModel):
    """Change Request Model - Jira CR integration"""
    cr_id: str
    jira_url: str

    change_type: str  # configuration_update, baseline_creation, control_implementation
    title: str

    # What is being changed
    affected_cis: List[str]

    # Planned change
    planned_change: PlannedChange

    # Actual change (recorded after implementation)
    actual_change: Optional[ActualChange] = None

    # Variance analysis
    variance: Optional[ChangeVariance] = None

    # Tit-for-tat scoring
    tit_for_tat_score: Optional[TitForTatScore] = None

    # Approval workflow
    approvals: List[Approval] = Field(default_factory=list)

    # Baseline linkage
    creates_baseline: bool = False
    baseline_id: Optional[str] = None

    audit_trail_id: Optional[str] = None


class DriftReport(BaseModel):
    """Configuration drift report"""
    drift_id: str
    ci_id: str
    detected_at: datetime

    severity: str  # low, medium, high, critical
    drift_type: str  # configuration_mismatch, unauthorized_change, baseline_deviation

    current_hash: str
    baseline_hash: str

    differences: List[Dict[str, Any]]

    # Remediation
    remediation_required: bool = True
    remediation_plan: Optional[str] = None
    remediated_at: Optional[datetime] = None

    audit_trail_id: Optional[str] = None


# MongoDB Collection Names
COLLECTIONS = {
    "configuration_items": "configuration_items",
    "baselines": "baselines",
    "change_requests": "change_requests",
    "audit_trail": "audit_trail",
    "rmf_controls": "rmf_controls",
    "drift_reports": "drift_reports"
}


# MongoDB Indexes
INDEXES = {
    "configuration_items": [
        {"keys": [("ci_id", 1)], "unique": True},
        {"keys": [("ci_type", 1), ("environment", 1)]},
        {"keys": [("relationships.target_ci_id", 1)]},
        {"keys": [("configuration_hash", 1)]},
        {"keys": [("tier", 1), ("environment", 1)]},
    ],
    "baselines": [
        {"keys": [("baseline_id", 1)], "unique": True},
        {"keys": [("ci_id", 1), ("baseline_type", 1)]},
        {"keys": [("status", 1), ("approved_at", -1)]},
        {"keys": [("jira_cr_id", 1)]},
    ],
    "change_requests": [
        {"keys": [("cr_id", 1)], "unique": True},
        {"keys": [("affected_cis", 1)]},
        {"keys": [("jira_cr_id", 1)]},
    ],
    "drift_reports": [
        {"keys": [("drift_id", 1)], "unique": True},
        {"keys": [("ci_id", 1), ("detected_at", -1)]},
        {"keys": [("severity", 1), ("remediation_required", 1)]},
    ]
}
