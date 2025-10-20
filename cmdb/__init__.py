"""
CMDB Package
AI Agent Governance Framework - Internal v2.1

Configuration Management Database with MongoDB backend
"""

from .client import CMDBClient
from .schemas import (
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
    Environment,
    Criticality
)

__version__ = "1.0.0"
__all__ = [
    "CMDBClient",
    "ConfigurationItem",
    "AIAgentCI",
    "ConfigurationBaseline",
    "SecurityBaseline",
    "ComplianceBaseline",
    "PerformanceBaseline",
    "ChangeRequest",
    "DriftReport",
    "BaselineType",
    "BaselineStatus",
    "CIType",
    "Environment",
    "Criticality"
]
