# Configuration Management Database (CMDB) Architecture

**AI Agent Governance Framework - Internal v2.1**
**Control Coverage:** CM-2, CM-3, CM-6, CM-8, AU-002, MI-019, SI-004
**Version:** 1.0
**Last Updated:** 2025-10-19

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Common Data Model (CDM)](#common-data-model-cdm)
4. [Baseline Types](#baseline-types)
5. [Graph Visualization](#graph-visualization)
6. [Change Management Integration](#change-management-integration)
7. [AI Agent Interfaces](#ai-agent-interfaces)
8. [RMF Control Mapping](#rmf-control-mapping)
9. [Security & Encryption](#security--encryption)
10. [Gap Analysis](#gap-analysis)

---

## Overview

The CMDB provides a **single source of truth** for all AI agent configurations, infrastructure state, and compliance baselines. It enables:

- ✅ **Configuration Baselines**: Approved agent configs at specific points in time
- ✅ **Security Baselines**: Required controls per tier (Tier 1-4)
- ✅ **Compliance Baselines**: NIST 800-53 RMF control states
- ✅ **Performance Baselines**: Cost, latency, quality metrics
- ✅ **Drift Detection**: Compare actual state vs. baseline
- ✅ **Change Tracking**: Planned vs. actual changes via Jira CR
- ✅ **Audit Trail**: Full history with cryptographic verification (MI-019)

### RMF Control Alignment

| Control | Description | CMDB Implementation |
|---------|-------------|---------------------|
| **CM-2** | Baseline Configuration | 4 baseline types with versioning |
| **CM-3** | Configuration Change Control | Jira CR tracking, approval gates |
| **CM-6** | Configuration Settings | Security/compliance baseline enforcement |
| **CM-8** | System Component Inventory | CI database with relationships |
| **AU-2** | Audit Events | All CMDB changes logged with hash |
| **SI-4** | System Monitoring | Drift detection, baseline comparison |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Agent Layer                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Query CMDB   │  │ Create       │  │ Detect Drift │         │
│  │ Current State│  │ Baseline     │  │ vs. Baseline │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                  │
└─────────┼─────────────────┼──────────────────┼──────────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CMDB API Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  REST API: /api/v1/cmdb/                                        │
│  - GET /ci/{ci_id}                  - Get Configuration Item    │
│  - POST /baseline                   - Create Baseline           │
│  - GET /baseline/{baseline_id}      - Get Baseline             │
│  - POST /compare                    - Compare state vs baseline │
│  - GET /drift                       - Detect drift              │
│  - POST /change-request             - Record Jira CR            │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MongoDB CMDB Core                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Collections:                                                    │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │ configuration_items│  │ baselines          │                │
│  │ - CI objects       │  │ - 4 baseline types │                │
│  │ - Relationships    │  │ - Version history  │                │
│  └────────────────────┘  └────────────────────┘                │
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │ change_requests    │  │ audit_trail        │                │
│  │ - Jira CRs         │  │ - All changes      │                │
│  │ - Planned/Actual   │  │ - Crypto hashing   │                │
│  └────────────────────┘  └────────────────────┘                │
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │ rmf_controls       │  │ drift_reports      │                │
│  │ - Control states   │  │ - Detected drifts  │                │
│  │ - Overlays         │  │ - Remediation      │                │
│  └────────────────────┘  └────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Graph Visualization Layer (Neo4j Pattern)           │
├─────────────────────────────────────────────────────────────────┤
│  Nodes: CIs, Baselines, Controls                                │
│  Edges: DEPENDS_ON, IMPLEMENTS, PART_OF, VALIDATES              │
│                                                                  │
│  Example Query:                                                  │
│  MATCH (agent:AI_Agent)-[:USES]->(config:Configuration)         │
│        -[:IMPLEMENTS]->(control:RMF_Control)                    │
│  WHERE control.id = "CM-2"                                      │
│  RETURN agent, config, control                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Data Model (CDM)

### 1. Configuration Item (CI)

**Base Model for all configuration items**

```javascript
{
  "_id": ObjectId("..."),
  "ci_id": "CI-2025-001",
  "ci_type": "ai_agent",  // ai_agent, infrastructure, service, control
  "name": "security-ops-agent",
  "description": "Tier 3 security operations agent",

  // Classification
  "tier": 3,
  "environment": "production",
  "criticality": "high",  // low, medium, high, critical

  // Metadata
  "owner": "security-team@suhlabs.com",
  "created_at": ISODate("2025-10-19T00:00:00Z"),
  "updated_at": ISODate("2025-10-19T12:00:00Z"),
  "version": "1.2.3",

  // Configuration Data (flexible schema)
  "configuration": {
    // Agent-specific config
    "model": "claude-sonnet-4-5-20250929",
    "provider": "anthropic",
    "max_tokens": 4096,
    "temperature": 0.7,
    "cost_budget_daily_usd": 100.0,
    "cost_budget_monthly_usd": 2000.0,

    // Infrastructure
    "deployment_type": "lambda",  // lambda, kubernetes, ecs
    "memory_mb": 1024,
    "timeout_seconds": 300,
    "vpc_id": "vpc-12345",
    "subnet_ids": ["subnet-abc", "subnet-def"],

    // Security
    "iam_role_arn": "arn:aws:iam::123456789012:role/security-ops-agent",
    "kms_key_id": "alias/agent-encryption",
    "secrets": {
      "llm_api_key": "arn:aws:secretsmanager:us-east-1:123:secret:llm-key",
      "github_token": "arn:aws:secretsmanager:us-east-1:123:secret:gh-token"
    },

    // Controls implemented
    "controls_implemented": [
      "SEC-001", "MI-003", "MI-009", "MI-020", "MI-021"
    ]
  },

  // Relationships (NoSQL pattern)
  "relationships": [
    {
      "type": "DEPENDS_ON",
      "target_ci_id": "CI-2025-002",
      "target_name": "kms-encryption-key",
      "description": "Depends on KMS key for encryption"
    },
    {
      "type": "IMPLEMENTS",
      "target_ci_id": "CTRL-CM-002",
      "target_name": "CM-2 Baseline Configuration",
      "description": "Implements baseline configuration control"
    },
    {
      "type": "PART_OF",
      "target_ci_id": "CI-2025-003",
      "target_name": "security-ops-service",
      "description": "Part of security operations service"
    }
  ],

  // Baseline references
  "current_baseline_id": "BL-CONFIG-2025-10-19-001",
  "approved_baselines": [
    "BL-CONFIG-2025-10-15-001",
    "BL-CONFIG-2025-10-19-001"
  ],

  // Change tracking
  "last_change_request": {
    "jira_cr_id": "CR-2025-1042",
    "change_date": ISODate("2025-10-19T10:00:00Z"),
    "change_type": "configuration_update",
    "approver": "change-manager@suhlabs.com"
  },

  // Cryptographic verification
  "configuration_hash": "sha256:a1b2c3d4...",  // SHA-256 of configuration object
  "signature": {
    "algorithm": "RSA-SHA256",
    "signed_by": "change-manager@suhlabs.com",
    "signed_at": ISODate("2025-10-19T10:00:00Z"),
    "signature_value": "base64encodedSig..."
  },

  // Audit trail
  "audit_trail_ids": [
    "audit-20251019-001",
    "audit-20251019-002"
  ]
}
```

### 2. Child Objects (Embedded or Referenced)

**Infrastructure Components**

```javascript
{
  "ci_id": "CI-2025-002",
  "ci_type": "infrastructure",
  "name": "agent-kms-key",
  "configuration": {
    "type": "kms_key",
    "key_id": "arn:aws:kms:us-east-1:123456789012:key/12345678",
    "rotation_enabled": true,
    "key_policy": { /* IAM policy */ }
  }
}
```

**Control Implementation**

```javascript
{
  "ci_id": "CTRL-CM-002",
  "ci_type": "rmf_control",
  "name": "CM-2 Baseline Configuration",
  "configuration": {
    "control_family": "CM",
    "control_number": "2",
    "control_enhancement": null,
    "implementation_status": "implemented",
    "responsible_role": "Configuration Manager",
    "implementation_description": "Automated baseline creation and versioning",
    "evidence": [
      "baseline-creation-logs",
      "version-history-db"
    ]
  }
}
```

---

## Baseline Types

### 1. Configuration Baseline

**Approved agent configuration at a specific point in time**

```javascript
{
  "_id": ObjectId("..."),
  "baseline_id": "BL-CONFIG-2025-10-19-001",
  "baseline_type": "configuration",
  "name": "Security Ops Agent v1.2.3 Production Config",
  "description": "Approved configuration for production deployment",

  // What is being baselined
  "ci_id": "CI-2025-001",
  "ci_name": "security-ops-agent",

  // Baseline metadata
  "status": "approved",  // draft, pending_approval, approved, superseded
  "created_at": ISODate("2025-10-19T10:00:00Z"),
  "approved_at": ISODate("2025-10-19T12:00:00Z"),
  "approved_by": "change-manager@suhlabs.com",

  // Jira CR linkage
  "jira_cr_id": "CR-2025-1042",
  "jira_cr_url": "https://suhlabs.atlassian.net/browse/CR-2025-1042",

  // Snapshot of configuration
  "configuration_snapshot": {
    // Full CI configuration at this point in time
    "model": "claude-sonnet-4-5-20250929",
    "memory_mb": 1024,
    "cost_budget_daily_usd": 100.0,
    // ... full config
  },

  // Cryptographic hash for integrity
  "configuration_hash": "sha256:a1b2c3d4e5f6...",
  "hash_algorithm": "SHA-256",

  // Signature for non-repudiation
  "signature": {
    "algorithm": "RSA-SHA256",
    "signed_by": "change-manager@suhlabs.com",
    "public_key_id": "key-id-12345",
    "signature_value": "base64..."
  },

  // Version control
  "version": "1.2.3",
  "previous_baseline_id": "BL-CONFIG-2025-10-15-001",
  "superseded_by": null,  // null if current

  // Audit
  "audit_trail_id": "audit-20251019-config-baseline-001"
}
```

### 2. Security Baseline

**Required controls per tier**

```javascript
{
  "baseline_id": "BL-SECURITY-TIER3-2025-10-19",
  "baseline_type": "security",
  "name": "Tier 3 Security Baseline",
  "description": "Required security controls for Tier 3 operations agents",

  "tier": 3,
  "environment": "production",

  "required_controls": [
    {
      "control_id": "SEC-001",
      "control_name": "Secrets Management",
      "status": "required",
      "implementation": {
        "type": "aws_secrets_manager",
        "rotation_enabled": true,
        "min_rotation_days": 90
      },
      "validation": {
        "method": "automated_scan",
        "frequency": "daily"
      }
    },
    {
      "control_id": "MI-003",
      "control_name": "Encryption at Rest",
      "status": "required",
      "implementation": {
        "type": "kms",
        "key_rotation": true,
        "algorithm": "AES-256"
      }
    },
    {
      "control_id": "MI-009",
      "control_name": "Cost Monitoring",
      "status": "required",
      "thresholds": {
        "daily_usd": 100.0,
        "monthly_usd": 2000.0,
        "alert_at_percent": 90
      }
    },
    {
      "control_id": "MI-020",
      "control_name": "Tier Enforcement",
      "status": "required",
      "permissions": {
        "can_modify_prod": true,
        "requires_approval": true,
        "approval_type": "jira_cr"
      }
    }
  ],

  "configuration_hash": "sha256:security-baseline-hash",
  "approved_by": "security-lead@suhlabs.com",
  "approved_at": ISODate("2025-10-19T00:00:00Z")
}
```

### 3. Compliance Baseline (NIST 800-53 RMF)

**Control implementation states**

```javascript
{
  "baseline_id": "BL-COMPLIANCE-NIST-800-53-2025-10-19",
  "baseline_type": "compliance",
  "name": "NIST 800-53 Rev 5 FedRAMP Moderate Baseline",
  "description": "RMF control implementation status",

  "framework": "NIST-800-53-Rev5",
  "overlay": "FedRAMP-Moderate",

  "control_families": {
    "CM": {
      "family_name": "Configuration Management",
      "controls": [
        {
          "control_id": "CM-2",
          "control_name": "Baseline Configuration",
          "implementation_status": "implemented",
          "responsible_role": "Configuration Manager",
          "implementation_description": "MongoDB CMDB with versioned baselines",
          "evidence": [
            "cmdb-baseline-logs",
            "version-history",
            "audit-trails"
          ],
          "assessment": {
            "last_assessed": ISODate("2025-10-15T00:00:00Z"),
            "assessor": "security-auditor@suhlabs.com",
            "result": "satisfactory",
            "findings": []
          }
        },
        {
          "control_id": "CM-3",
          "control_name": "Configuration Change Control",
          "implementation_status": "implemented",
          "responsible_role": "Change Manager",
          "implementation_description": "Jira CR with approval gates",
          "evidence": ["jira-cr-logs", "approval-trails"]
        },
        {
          "control_id": "CM-6",
          "control_name": "Configuration Settings",
          "implementation_status": "implemented"
        },
        {
          "control_id": "CM-8",
          "control_name": "System Component Inventory",
          "implementation_status": "implemented"
        }
      ]
    },
    "AU": {
      "family_name": "Audit and Accountability",
      "controls": [
        {
          "control_id": "AU-2",
          "control_name": "Event Logging",
          "implementation_status": "implemented"
        }
      ]
    }
  },

  "configuration_hash": "sha256:compliance-baseline-hash"
}
```

### 4. Performance Baseline

**Cost, latency, quality metrics**

```javascript
{
  "baseline_id": "BL-PERFORMANCE-2025-10-19-001",
  "baseline_type": "performance",
  "name": "Security Ops Agent Performance Baseline",

  "ci_id": "CI-2025-001",
  "measurement_period": {
    "start": ISODate("2025-10-01T00:00:00Z"),
    "end": ISODate("2025-10-15T23:59:59Z")
  },

  "metrics": {
    "cost": {
      "daily_avg_usd": 85.50,
      "daily_p50_usd": 82.00,
      "daily_p95_usd": 95.00,
      "monthly_total_usd": 1282.50,
      "cost_per_request_usd": 0.05
    },
    "latency": {
      "avg_ms": 450,
      "p50_ms": 400,
      "p95_ms": 750,
      "p99_ms": 1200
    },
    "quality": {
      "task_success_rate": 0.95,
      "defect_rate": 0.03,
      "human_review_approval_rate": 0.92
    },
    "availability": {
      "uptime_percent": 99.9,
      "mtbf_hours": 720,
      "mttr_minutes": 15
    }
  },

  // Thresholds for drift detection
  "thresholds": {
    "cost_increase_percent": 20,  // Alert if cost increases >20%
    "latency_increase_percent": 30,
    "quality_decrease_percent": 10
  },

  "configuration_hash": "sha256:performance-baseline-hash"
}
```

---

## Graph Visualization

### Neo4j-Style Pattern (MongoDB Implementation)

**Nodes and Relationships**

```javascript
// Node types stored in MongoDB
const nodeTypes = [
  "AI_Agent",
  "Configuration",
  "Baseline",
  "RMF_Control",
  "Infrastructure",
  "Service",
  "Change_Request"
];

// Relationship types
const relationshipTypes = [
  "DEPENDS_ON",      // CI depends on another CI
  "IMPLEMENTS",      // CI implements a control
  "PART_OF",         // CI is part of a service
  "VALIDATES",       // Baseline validates a configuration
  "REFERENCES",      // CR references a baseline
  "SUPERSEDES",      // New baseline supersedes old
  "USES",           // Agent uses configuration
  "MONITORS"        // Control monitors CI
];
```

**Graph Query Examples**

```javascript
// Find all agents implementing CM-2 control
db.configuration_items.aggregate([
  {
    $match: {
      "relationships.type": "IMPLEMENTS",
      "relationships.target_ci_id": "CTRL-CM-002"
    }
  },
  {
    $lookup: {
      from: "configuration_items",
      localField: "relationships.target_ci_id",
      foreignField: "ci_id",
      as: "controls"
    }
  }
]);

// Find drift: CIs not matching current baseline
db.configuration_items.aggregate([
  {
    $lookup: {
      from: "baselines",
      localField: "current_baseline_id",
      foreignField: "baseline_id",
      as: "baseline"
    }
  },
  {
    $addFields: {
      "config_hash_current": "$configuration_hash",
      "config_hash_baseline": { $arrayElemAt: ["$baseline.configuration_hash", 0] }
    }
  },
  {
    $match: {
      $expr: { $ne: ["$config_hash_current", "$config_hash_baseline"] }
    }
  }
]);
```

**Visualization Schema for UI**

```javascript
{
  "graph": {
    "nodes": [
      {
        "id": "CI-2025-001",
        "label": "security-ops-agent",
        "type": "AI_Agent",
        "tier": 3,
        "status": "active",
        "color": "#4CAF50",  // green for active
        "size": 30
      },
      {
        "id": "CTRL-CM-002",
        "label": "CM-2 Baseline",
        "type": "RMF_Control",
        "status": "implemented",
        "color": "#2196F3",  // blue for controls
        "size": 20
      }
    ],
    "edges": [
      {
        "source": "CI-2025-001",
        "target": "CTRL-CM-002",
        "type": "IMPLEMENTS",
        "label": "implements",
        "color": "#999",
        "width": 2
      }
    ]
  }
}
```

---

## Change Management Integration

### Jira CR Tracking

**Change Request Model**

```javascript
{
  "cr_id": "CR-2025-1042",
  "jira_url": "https://suhlabs.atlassian.net/browse/CR-2025-1042",

  "change_type": "configuration_update",  // configuration_update, baseline_creation, control_implementation
  "title": "Update security-ops-agent memory to 2GB",

  // What is being changed
  "affected_cis": ["CI-2025-001"],

  // Planned change
  "planned_change": {
    "field": "configuration.memory_mb",
    "old_value": 1024,
    "new_value": 2048,
    "justification": "Increased workload requires more memory",
    "estimated_impact": {
      "cost_increase_monthly_usd": 50.0,
      "performance_improvement_percent": 15.0
    }
  },

  // Actual change (recorded after implementation)
  "actual_change": {
    "field": "configuration.memory_mb",
    "old_value": 1024,
    "new_value": 2048,
    "implemented_at": ISODate("2025-10-19T12:00:00Z"),
    "actual_impact": {
      "cost_increase_monthly_usd": 48.0,  // Slightly better than planned
      "performance_improvement_percent": 18.0
    }
  },

  // Variance analysis (planned vs actual)
  "variance": {
    "cost_variance_usd": -2.0,  // Better than planned (negative = under budget)
    "performance_variance_percent": 3.0,  // Better than planned
    "within_tolerance": true
  },

  // Tit-for-tat scoring
  "tit_for_tat_score": {
    "accuracy_score": 0.95,  // How accurate was the estimate?
    "contributes_to_reputation": true,
    "agent_id": "security-ops-agent",
    "proposal_id": "PROP-2025-005"
  },

  // Approval workflow
  "approvals": [
    {
      "approver": "change-manager@suhlabs.com",
      "approved_at": ISODate("2025-10-19T10:00:00Z"),
      "signature": "base64..."
    }
  ],

  // Baseline linkage
  "creates_baseline": true,
  "baseline_id": "BL-CONFIG-2025-10-19-001",

  "audit_trail_id": "audit-20251019-cr-1042"
}
```

### Planned vs. Actual Comparison

```javascript
// Comparison function
function compareChange(cr_id) {
  const cr = db.change_requests.findOne({ cr_id });

  const variance = {
    field_differences: [],
    cost_variance: cr.actual_change.actual_impact.cost_increase_monthly_usd -
                   cr.planned_change.estimated_impact.cost_increase_monthly_usd,
    performance_variance: cr.actual_change.actual_impact.performance_improvement_percent -
                         cr.planned_change.estimated_impact.performance_improvement_percent
  };

  // Check if within acceptable tolerance (±10%)
  variance.within_tolerance = (
    Math.abs(variance.cost_variance) <= 0.10 * Math.abs(cr.planned_change.estimated_impact.cost_increase_monthly_usd) &&
    Math.abs(variance.performance_variance) <= 0.10 * Math.abs(cr.planned_change.estimated_impact.performance_improvement_percent)
  );

  return variance;
}
```

---

## AI Agent Interfaces

### 1. Query Current State

```python
# Example: Agent queries CMDB before proposing change
from cmdb_client import CMDBClient

cmdb = CMDBClient(mongodb_uri="mongodb://localhost:27017/cmdb")

# Get current configuration
current_config = cmdb.get_ci("CI-2025-001")
print(f"Current memory: {current_config['configuration']['memory_mb']} MB")
print(f"Current cost: ${current_config['configuration']['cost_budget_daily_usd']}/day")

# Get current baseline
baseline = cmdb.get_baseline(current_config['current_baseline_id'])
print(f"Baseline approved at: {baseline['approved_at']}")
```

### 2. Create Baseline (Automatic)

```python
# Agent automatically creates baseline after approved change
def create_baseline_after_change(ci_id, jira_cr_id):
    ci = cmdb.get_ci(ci_id)

    baseline = {
        "baseline_id": generate_baseline_id(),
        "baseline_type": "configuration",
        "ci_id": ci_id,
        "status": "draft",  # Agent creates draft, human approves
        "configuration_snapshot": ci["configuration"],
        "configuration_hash": calculate_sha256(ci["configuration"]),
        "jira_cr_id": jira_cr_id,
        "created_at": datetime.utcnow()
    }

    baseline_id = cmdb.create_baseline(baseline)
    print(f"✅ Baseline draft created: {baseline_id}")
    print(f"   Requires approval from Change Manager")

    return baseline_id
```

### 3. Detect Drift

```python
# Agent detects configuration drift
def detect_drift(ci_id):
    ci = cmdb.get_ci(ci_id)
    baseline = cmdb.get_baseline(ci["current_baseline_id"])

    current_hash = calculate_sha256(ci["configuration"])
    baseline_hash = baseline["configuration_hash"]

    if current_hash != baseline_hash:
        drift = {
            "ci_id": ci_id,
            "detected_at": datetime.utcnow(),
            "severity": "high",
            "drift_type": "configuration_mismatch",
            "current_hash": current_hash,
            "baseline_hash": baseline_hash,
            "differences": compare_configs(
                ci["configuration"],
                baseline["configuration_snapshot"]
            )
        }

        cmdb.create_drift_report(drift)
        print(f"⚠️  DRIFT DETECTED: {ci_id}")
        print(f"   Differences: {drift['differences']}")
        return drift
    else:
        print(f"✅ No drift detected: {ci_id}")
        return None
```

---

## RMF Control Mapping

### Control Overlay System

```javascript
// Base RMF controls (NIST 800-53 Rev 5)
const baseControls = {
  "CM-2": {
    "family": "CM",
    "control": "2",
    "title": "Baseline Configuration",
    "implementation_guidance": "Develop, document, and maintain baseline configurations",
    "overlays": {
      "FedRAMP-Moderate": {
        "required": true,
        "enhancements": ["CM-2(1)", "CM-2(3)", "CM-2(7)"],
        "additional_requirements": [
          "Automated baseline creation",
          "Version control with cryptographic hashing"
        ]
      },
      "AI-Specific": {
        "required": true,
        "additional_requirements": [
          "Model version tracking",
          "Prompt template versioning",
          "Cost baseline monitoring"
        ]
      }
    }
  },

  "CM-3": {
    "family": "CM",
    "control": "3",
    "title": "Configuration Change Control",
    "overlays": {
      "FedRAMP-Moderate": {
        "required": true,
        "enhancements": ["CM-3(1)", "CM-3(2)"]
      },
      "AI-Specific": {
        "additional_requirements": [
          "Jira CR for all Tier 3+ changes",
          "Tit-for-tat reputation tracking",
          "Planned vs actual variance analysis"
        ]
      }
    }
  }
};
```

### Convention for Non-Standard Controls

**AI-Specific Controls (Custom Convention)**

```javascript
{
  "control_id": "AI-CM-01",
  "control_family": "AI-Configuration Management",
  "title": "Model Version Baseline",
  "description": "Maintain baseline configurations for AI model versions, prompts, and parameters",

  "derived_from": ["CM-2", "CM-8"],
  "justification": "Standard CM controls don't address AI-specific configurations like model versions and prompt templates",

  "implementation_requirements": [
    "Track model provider and version",
    "Baseline prompt templates with version control",
    "Monitor for model drift or degradation",
    "Document model update procedures"
  ],

  "assessment_procedures": [
    "Verify model version tracking in CMDB",
    "Review prompt template version history",
    "Validate model change approval process"
  ]
}
```

---

## Security & Encryption

### Cryptographic Hashing

**SHA-256 for Version Control**

```python
import hashlib
import json

def calculate_configuration_hash(config):
    """
    Calculate SHA-256 hash of configuration
    Ensures deterministic ordering for consistent hashing
    """
    # Sort keys for deterministic hashing
    config_json = json.dumps(config, sort_keys=True, separators=(',', ':'))
    config_bytes = config_json.encode('utf-8')

    hash_obj = hashlib.sha256(config_bytes)
    hash_hex = hash_obj.hexdigest()

    return f"sha256:{hash_hex}"

# Example
config = {
    "model": "claude-sonnet-4-5-20250929",
    "memory_mb": 1024,
    "cost_budget_daily_usd": 100.0
}

config_hash = calculate_configuration_hash(config)
print(f"Configuration hash: {config_hash}")
# Output: sha256:a1b2c3d4e5f6...
```

### Digital Signatures (RSA-SHA256)

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64

def sign_baseline(baseline, private_key_pem):
    """
    Sign baseline with RSA-SHA256 for non-repudiation
    """
    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )

    # Create hash of baseline
    baseline_json = json.dumps(baseline, sort_keys=True)
    baseline_hash = hashlib.sha256(baseline_json.encode()).digest()

    # Sign hash
    signature = private_key.sign(
        baseline_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode('utf-8')

def verify_signature(baseline, signature_b64, public_key_pem):
    """
    Verify baseline signature
    """
    # Load public key
    public_key = serialization.load_pem_public_key(public_key_pem.encode())

    # Decode signature
    signature = base64.b64decode(signature_b64)

    # Verify
    baseline_json = json.dumps(baseline, sort_keys=True)
    baseline_hash = hashlib.sha256(baseline_json.encode()).digest()

    try:
        public_key.verify(
            signature,
            baseline_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False
```

### Encryption at Rest (MongoDB)

```javascript
// MongoDB client-side field-level encryption
const {
  ClientEncryption,
  MongoCryptInvalidArgumentError
} = require('mongodb-client-encryption');

// Encrypt sensitive configuration fields
const encryptedFields = {
  "configuration.secrets.llm_api_key": {
    "encrypt": true,
    "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
    "keyId": "kms-key-id-12345"
  },
  "configuration.secrets.github_token": {
    "encrypt": true,
    "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
    "keyId": "kms-key-id-12345"
  }
};
```

---

## Gap Analysis

### Current Framework Capabilities (Before CMDB)

| Capability | Status | Evidence |
|------------|--------|----------|
| Configuration tracking | ⚠️ Partial | Templates exist, no centralized DB |
| Baseline management | ❌ Missing | No baseline versioning |
| Change control | ✅ Implemented | Jira CR with PKI signatures |
| Drift detection | ❌ Missing | Manual comparison only |
| Audit trail | ✅ Implemented | MI-019 with SIEM integration |
| RMF compliance | ⚠️ Partial | 88% controls, no CM-2/CM-8 evidence |
| Performance monitoring | ⚠️ Partial | Cost monitoring, no baselines |

### Gaps Addressed by CMDB

| Gap | CMDB Solution | RMF Control |
|-----|---------------|-------------|
| **No baseline versioning** | 4 baseline types with cryptographic hashing | CM-2 |
| **No CI inventory** | MongoDB collection with relationships | CM-8 |
| **Manual drift detection** | Automated hash comparison | SI-4 |
| **Decentralized configs** | Centralized CMDB with API | CM-6 |
| **No planned vs actual tracking** | CR variance analysis | CM-3 |
| **Limited graph visualization** | Neo4j-pattern relationships | N/A (usability) |
| **No performance baselines** | Dedicated baseline type with thresholds | N/A (operations) |

### Recommendations

#### 1. Implementation Priority

**Phase 1 (Week 1-2): Core CMDB**
- ✅ MongoDB setup with collections
- ✅ Common Data Model implementation
- ✅ Configuration baseline creation
- ✅ Basic API (GET/POST)

**Phase 2 (Week 3-4): Integration**
- ✅ Jira CR integration
- ✅ Cryptographic hashing
- ✅ Drift detection
- ✅ AI agent query interface

**Phase 3 (Week 5-6): Advanced Features**
- ✅ Security/compliance baselines
- ✅ Performance baselines
- ✅ Graph visualization layer
- ✅ RMF control mapping

#### 2. Technology Recommendations

**MongoDB Configuration**
- Use **MongoDB Atlas** for managed service
- Enable **field-level encryption** for secrets
- Configure **replica sets** for high availability
- Use **change streams** for real-time drift detection

**Graph Visualization**
- **Option A**: Use MongoDB native graph queries (aggregate $graphLookup)
- **Option B**: Export to Neo4j for advanced visualization (if needed)
- **Recommended**: Start with Option A, migrate to Option B if needed

**API Framework**
- Use **FastAPI** (Python) for CMDB API
- OpenAPI/Swagger documentation
- JWT authentication
- Rate limiting

#### 3. Security Hardening

```yaml
security_measures:
  authentication:
    - JWT tokens with short expiration (1 hour)
    - Service accounts for AI agents
    - PKI certificates for critical operations

  authorization:
    - Role-based access control (RBAC)
    - Tier-based permissions (Tier 1 read-only, Tier 3+ write)
    - Approval gates for baseline modifications

  encryption:
    - TLS 1.3 for data in transit
    - MongoDB field-level encryption for secrets
    - KMS integration (AWS KMS, HashiCorp Vault)

  audit:
    - All CMDB operations logged to MI-019 audit trail
    - SIEM integration for real-time monitoring
    - Immutable audit logs
```

#### 4. Performance Optimization

```yaml
mongodb_indexes:
  configuration_items:
    - { ci_id: 1 }  # Primary key
    - { ci_type: 1, environment: 1 }  # Common queries
    - { "relationships.target_ci_id": 1 }  # Graph traversal
    - { configuration_hash: 1 }  # Drift detection

  baselines:
    - { baseline_id: 1 }
    - { ci_id: 1, baseline_type: 1 }
    - { status: 1, approved_at: -1 }

  change_requests:
    - { cr_id: 1 }
    - { "affected_cis": 1 }
    - { jira_cr_id: 1 }
```

#### 5. Integration with Tit-for-Tat

**Reputation Scoring Based on Change Accuracy**

```python
def update_tit_for_tat_from_cr(cr_id):
    """
    Update agent reputation based on CR variance
    """
    cr = cmdb.get_change_request(cr_id)
    variance = cr['variance']

    # Calculate accuracy score
    cost_accuracy = 1.0 - min(abs(variance['cost_variance_usd']) /
                              abs(cr['planned_change']['estimated_impact']['cost_increase_monthly_usd']), 1.0)
    perf_accuracy = 1.0 - min(abs(variance['performance_variance_percent']) /
                              abs(cr['planned_change']['estimated_impact']['performance_improvement_percent']), 1.0)

    accuracy_score = (cost_accuracy + perf_accuracy) / 2.0

    # Update tit-for-tat reputation
    reputation = get_agent_reputation(cr['tit_for_tat_score']['agent_id'])

    # High accuracy (>0.9) improves reputation
    # Low accuracy (<0.8) hurts reputation
    if accuracy_score >= 0.9:
        reputation.record_cooperation()
    elif accuracy_score < 0.8:
        reputation.record_defection()

    print(f"Tit-for-tat updated: Accuracy={accuracy_score:.2f}, Reputation={reputation.cooperation_score:.2f}")
```

---

## Next Steps

1. **Review this architecture** - Confirm alignment with Suhlabs requirements
2. **Implement MongoDB schema** - Create collections and indexes
3. **Build CMDB API** - FastAPI with OpenAPI documentation
4. **Integrate with existing framework** - Connect to Jira, audit trail, tit-for-tat
5. **Deploy and test** - Pilot with one agent, expand to all
6. **Documentation** - Operational runbooks, API guides

---

**Version:** 1.0
**Last Updated:** 2025-10-19
**Author:** Suhlabs AI Governance Team
**Control Coverage:** CM-2, CM-3, CM-6, CM-8, AU-002, MI-019, SI-004
