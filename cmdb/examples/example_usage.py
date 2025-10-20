#!/usr/bin/env python3
"""
CMDB Example Usage
AI Agent Governance Framework - Internal v2.1

Demonstrates CMDB operations for AI agents:
1. Create Configuration Item (AI Agent)
2. Create Configuration Baseline
3. Update Configuration
4. Detect Drift
5. Create Change Request with variance analysis
6. Query relationships (graph)
"""

import sys
sys.path.append('..')

from datetime import datetime
from client import CMDBClient
from schemas import (
    ConfigurationItem,
    ConfigurationBaseline,
    ChangeRequest,
    PlannedChange,
    ActualChange,
    Approval,
    CIType,
    Environment,
    Criticality,
    BaselineType,
    BaselineStatus,
    RelationshipType,
    Relationship
)


def main():
    print("=" * 70)
    print("CMDB Example Usage - AI Agent Configuration Management")
    print("=" * 70)

    # Initialize CMDB client
    cmdb = CMDBClient(
        mongodb_uri="mongodb://localhost:27017",
        database="cmdb_demo"
    )

    # ========================================================================
    # Step 1: Create AI Agent Configuration Item
    # ========================================================================

    print("\n[Step 1] Creating AI Agent CI...")

    agent_ci = ConfigurationItem(
        ci_id="CI-2025-001",
        ci_type=CIType.AI_AGENT,
        name="security-ops-agent",
        description="Tier 3 security operations agent for automated incident response",
        tier=3,
        environment=Environment.PRODUCTION,
        criticality=Criticality.HIGH,
        owner="security-team@suhlabs.com",
        version="1.0.0",
        configuration={
            # AI Model configuration
            "model": "claude-sonnet-4-5-20250929",
            "provider": "anthropic",
            "max_tokens": 4096,
            "temperature": 0.7,

            # Resource configuration
            "deployment_type": "lambda",
            "memory_mb": 1024,
            "timeout_seconds": 300,

            # Cost configuration
            "cost_budget_daily_usd": 100.0,
            "cost_budget_monthly_usd": 2000.0,

            # Security configuration
            "iam_role_arn": "arn:aws:iam::123456789012:role/security-ops-agent",
            "kms_key_id": "alias/agent-encryption",

            # Controls implemented
            "controls_implemented": [
                "SEC-001",  # Secrets Management
                "MI-003",   # Encryption
                "MI-009",   # Cost Monitoring
                "MI-020",   # Tier Enforcement
                "CM-2"      # Baseline Configuration
            ]
        },
        relationships=[
            Relationship(
                type=RelationshipType.IMPLEMENTS,
                target_ci_id="CTRL-CM-002",
                target_name="CM-2 Baseline Configuration",
                description="Implements baseline configuration control"
            ),
            Relationship(
                type=RelationshipType.DEPENDS_ON,
                target_ci_id="CI-2025-KMS-001",
                target_name="agent-kms-key",
                description="Depends on KMS key for encryption"
            )
        ]
    )

    ci_id = cmdb.create_ci(agent_ci)
    print(f"✅ Created CI: {ci_id}")
    print(f"   Configuration hash: {agent_ci.configuration_hash}")

    # ========================================================================
    # Step 2: Create Configuration Baseline
    # ========================================================================

    print("\n[Step 2] Creating Configuration Baseline...")

    baseline = ConfigurationBaseline(
        baseline_id="BL-CONFIG-2025-10-19-001",
        baseline_type=BaselineType.CONFIGURATION,
        name="Security Ops Agent v1.0.0 Production Baseline",
        description="Initial approved configuration for production deployment",
        ci_id=agent_ci.ci_id,
        ci_name=agent_ci.name,
        status=BaselineStatus.DRAFT,
        jira_cr_id="CR-2025-1050",
        jira_cr_url="https://suhlabs.atlassian.net/browse/CR-2025-1050",
        configuration_snapshot=agent_ci.configuration.copy(),
        configuration_hash=agent_ci.configuration_hash,
        version="1.0.0"
    )

    baseline_id = cmdb.create_baseline(baseline)
    print(f"✅ Created Baseline: {baseline_id}")

    # Approve baseline
    cmdb.approve_baseline(
        baseline_id,
        approver="change-manager@suhlabs.com",
        signature="base64encodedSignature..."
    )
    print(f"✅ Approved Baseline: {baseline_id}")

    # ========================================================================
    # Step 3: Create Change Request (Planned Change)
    # ========================================================================

    print("\n[Step 3] Creating Change Request...")

    change_request = ChangeRequest(
        cr_id="CR-2025-1051",
        jira_url="https://suhlabs.atlassian.net/browse/CR-2025-1051",
        change_type="configuration_update",
        title="Increase security-ops-agent memory to 2GB",
        affected_cis=[ci_id],
        planned_change=PlannedChange(
            field="configuration.memory_mb",
            old_value=1024,
            new_value=2048,
            justification="Increased workload requires more memory for concurrent operations",
            estimated_impact={
                "cost_increase_monthly_usd": 50.0,
                "performance_improvement_percent": 20.0
            }
        ),
        approvals=[
            Approval(
                approver="change-manager@suhlabs.com",
                approved_at=datetime.utcnow()
            )
        ],
        creates_baseline=True
    )

    cr_id = cmdb.create_change_request(change_request)
    print(f"✅ Created Change Request: {cr_id}")
    print(f"   Planned: 1024MB → 2048MB")
    print(f"   Estimated cost increase: $50/month")
    print(f"   Estimated performance improvement: 20%")

    # ========================================================================
    # Step 4: Implement Change
    # ========================================================================

    print("\n[Step 4] Implementing Change...")

    # Update CI configuration
    updates = {
        "configuration": {
            "memory_mb": 2048
        },
        "approver": "change-manager@suhlabs.com"
    }

    cmdb.update_ci(ci_id, updates, jira_cr_id=cr_id)
    print(f"✅ Updated CI configuration")

    # Record actual change results
    actual_change = ActualChange(
        field="configuration.memory_mb",
        old_value=1024,
        new_value=2048,
        implemented_at=datetime.utcnow(),
        actual_impact={
            "cost_increase_monthly_usd": 48.0,  # Slightly better than planned!
            "performance_improvement_percent": 22.0  # Better than expected!
        }
    )

    cmdb.record_actual_change(cr_id, actual_change.model_dump(mode='json'))
    print(f"✅ Recorded actual change results")

    # Get variance analysis
    cr = cmdb.get_change_request(cr_id)
    variance = cr['variance']
    print(f"\n   Variance Analysis:")
    print(f"   - Cost variance: ${variance['cost_variance_usd']:.2f} (better than planned!)")
    print(f"   - Performance variance: {variance['performance_variance_percent']:.1f}%")
    print(f"   - Within tolerance: {variance['within_tolerance']}")
    print(f"   - Tit-for-tat accuracy score: {cr['tit_for_tat_score']['accuracy_score']:.2f}")

    # ========================================================================
    # Step 5: Create New Baseline After Change
    # ========================================================================

    print("\n[Step 5] Creating Post-Change Baseline...")

    updated_ci = cmdb.get_ci(ci_id)

    new_baseline = ConfigurationBaseline(
        baseline_id="BL-CONFIG-2025-10-19-002",
        baseline_type=BaselineType.CONFIGURATION,
        name="Security Ops Agent v1.1.0 - Increased Memory",
        description="Updated configuration with 2GB memory",
        ci_id=ci_id,
        ci_name=agent_ci.name,
        status=BaselineStatus.DRAFT,
        jira_cr_id=cr_id,
        configuration_snapshot=updated_ci['configuration'],
        configuration_hash=updated_ci['configuration_hash'],
        version="1.1.0",
        previous_baseline_id=baseline_id
    )

    new_baseline_id = cmdb.create_baseline(new_baseline)
    cmdb.approve_baseline(new_baseline_id, "change-manager@suhlabs.com")
    print(f"✅ Created and approved new baseline: {new_baseline_id}")

    # ========================================================================
    # Step 6: Simulate Drift (Unauthorized Change)
    # ========================================================================

    print("\n[Step 6] Simulating Configuration Drift...")

    # Simulate unauthorized change (someone increased memory without CR)
    unauthorized_updates = {
        "configuration": {
            "memory_mb": 4096,  # Unauthorized increase!
            "cost_budget_daily_usd": 150.0
        }
    }

    cmdb.update_ci(ci_id, unauthorized_updates)
    print(f"⚠️  Simulated unauthorized configuration change")
    print(f"   Memory: 2048MB → 4096MB (unauthorized!)")

    # Detect drift
    drift_report = cmdb.detect_drift(ci_id)
    if drift_report:
        print(f"\n   ⚠️  DRIFT DETECTED!")
        print(f"   Drift ID: {drift_report.drift_id}")
        print(f"   Severity: {drift_report.severity}")
        print(f"   Differences: {len(drift_report.differences)}")
        for diff in drift_report.differences:
            print(f"      - {diff['field']}: {diff['baseline_value']} → {diff['current_value']} ({diff['change_type']})")

    # ========================================================================
    # Step 7: Query Relationships (Graph)
    # ========================================================================

    print("\n[Step 7] Querying CI Relationships (Graph)...")

    relationships = cmdb.get_ci_relationships(ci_id)
    print(f"\n   Found {len(relationships)} relationships:")
    for rel in relationships:
        print(f"   - {rel['relationship']['type']}: {rel['relationship']['target_name']}")

    # Find all CIs implementing CM-2 control
    cm2_cis = cmdb.find_cis_implementing_control("CTRL-CM-002")
    print(f"\n   CIs implementing CM-2 control: {len(cm2_cis)}")

    # ========================================================================
    # Step 8: Get Statistics
    # ========================================================================

    print("\n[Step 8] CMDB Statistics...")

    stats = cmdb.get_statistics()
    print(f"\n   Total CIs: {stats['total_cis']}")
    print(f"   Total Baselines: {stats['total_baselines']}")
    print(f"   Total Change Requests: {stats['total_change_requests']}")
    print(f"   Total Drift Reports: {stats['total_drift_reports']}")

    print(f"\n   CIs by Type:")
    for ci_type, count in stats['cis_by_type'].items():
        print(f"      - {ci_type}: {count}")

    print(f"\n   Baselines by Status:")
    for status, count in stats['baselines_by_status'].items():
        print(f"      - {status}: {count}")

    if stats['drift_by_severity']:
        print(f"\n   Drift Reports by Severity:")
        for severity, count in stats['drift_by_severity'].items():
            print(f"      - {severity}: {count}")

    # ========================================================================
    # Summary
    # ========================================================================

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✅ Successfully demonstrated:")
    print("   1. Creating AI Agent Configuration Item")
    print("   2. Creating and approving baseline")
    print("   3. Change request with planned vs actual variance")
    print("   4. Tit-for-tat accuracy scoring")
    print("   5. Drift detection for unauthorized changes")
    print("   6. Graph relationship queries")
    print("   7. CMDB statistics")

    print("\n📊 Key Metrics:")
    print(f"   - Tit-for-tat accuracy: {cr['tit_for_tat_score']['accuracy_score']:.2f}")
    print(f"   - Cost variance: ${variance['cost_variance_usd']:.2f}")
    print(f"   - Drift detected: {'Yes' if drift_report else 'No'}")

    print("\n" + "=" * 70)

    # Close connection
    cmdb.close()


if __name__ == "__main__":
    main()
