#!/usr/bin/env python3
"""
ITSI Integration Example
AI Agent Governance Framework - Internal v2.1

Demonstrates:
1. Creating ITSI services linked to CMDB CIs
2. Defining KPIs with baseline references
3. Creating entities and linking to services
4. Recording KPI measurements with threshold evaluation
5. Generating events for Splunk ingestion
"""

import sys
sys.path.append('..')

from datetime import datetime
from client import CMDBClient
from schemas import (
    ConfigurationItem,
    ConfigurationBaseline,
    CIType,
    Environment,
    Criticality,
    BaselineType,
    BaselineStatus
)
from itsi_schemas import (
    ITSIService,
    ITSIKPI,
    ITSIEntity,
    ServiceHealth,
    KPIThresholdLevel,
    KPIThreshold,
    KPIAggregation,
    EntityAlias,
    EntityType,
    KPIType
)


def main():
    """Run ITSI integration example"""
    print("=" * 70)
    print("ITSI Integration Example")
    print("=" * 70)

    # Initialize CMDB client
    cmdb = CMDBClient(
        mongodb_uri="mongodb://localhost:27017",
        database="cmdb_itsi_demo"
    )

    # ========================================================================
    # Step 1: Create CMDB Configuration Item (AI Agent)
    # ========================================================================
    print("\n[1] Creating AI Agent CI...")

    ci = ConfigurationItem(
        ci_id="CI-AGENT-SECURITY-001",
        ci_type=CIType.AI_AGENT,
        name="security-ops-agent",
        tier=3,
        environment=Environment.PRODUCTION,
        criticality=Criticality.HIGH,
        owner="security-team@suhlabs.com",
        configuration={
            "model": "claude-sonnet-4-5-20250929",
            "memory_mb": 2048,
            "max_tokens": 200000,
            "temperature": 0.7,
            "region": "us-east-1",
            "vpc_id": "vpc-12345678",
            "security_groups": ["sg-security-ops"],
            "iam_role": "arn:aws:iam::123456789012:role/SecurityOpsAgent"
        }
    )

    ci_id = cmdb.create_ci(ci)
    print(f"✅ Created CI: {ci_id}")

    # ========================================================================
    # Step 2: Create Configuration Baseline
    # ========================================================================
    print("\n[2] Creating configuration baseline...")

    ci_doc = cmdb.get_ci(ci_id)
    baseline = ConfigurationBaseline(
        baseline_id="BL-AGENT-SECURITY-001",
        baseline_type=BaselineType.CONFIGURATION,
        name="Security Ops Agent Baseline v1.0",
        ci_id=ci_doc["ci_id"],
        ci_name=ci_doc["name"],
        status=BaselineStatus.DRAFT,
        configuration_snapshot=ci_doc["configuration"],
        configuration_hash=ci_doc["configuration_hash"]
    )

    baseline_id = cmdb.create_baseline(baseline)
    cmdb.approve_baseline(baseline_id, approver="security-manager@suhlabs.com")
    print(f"✅ Created and approved baseline: {baseline_id}")

    # ========================================================================
    # Step 3: Create ITSI Service
    # ========================================================================
    print("\n[3] Creating ITSI Service...")

    service = ITSIService(
        service_id="SVC-AI-SECURITY-OPS",
        service_name="AI Security Operations Service",
        description="AI-powered security operations and threat detection",
        service_type="technical",
        tier=3,
        criticality="high",
        owner="security-team@suhlabs.com",
        team="Security Operations",
        on_call="security-oncall@suhlabs.com",
        health_score=100.0,
        health_status=ServiceHealth.NORMAL,
        cmdb_ci_ids=[ci_id]
    )

    service_id = cmdb.create_itsi_service(service)
    print(f"✅ Created ITSI service: {service_id}")

    # ========================================================================
    # Step 4: Create ITSI Entity
    # ========================================================================
    print("\n[4] Creating ITSI Entity...")

    entity = ITSIEntity(
        entity_id="ENT-AGENT-SECURITY-001",
        entity_name="security-ops-agent.suhlabs.local",
        entity_type=EntityType.AI_AGENT,
        aliases=[
            EntityAlias(alias_type="ci_id", value=ci_id),
            EntityAlias(alias_type="hostname", value="security-ops-agent.suhlabs.local"),
            EntityAlias(alias_type="fqdn", value="security-ops-agent.prod.suhlabs.com")
        ],
        environment="production",
        region="us-east-1",
        availability_zone="us-east-1a",
        cmdb_ci_id=ci_id,
        info_fields={
            "tier": "3",
            "model": "claude-sonnet-4-5-20250929",
            "owner": "security-team@suhlabs.com",
            "criticality": "high"
        },
        tags=["ai-agent", "security", "tier-3", "production"]
    )

    entity_id = cmdb.create_itsi_entity(entity)
    cmdb.link_entity_to_service(entity_id, service_id)
    print(f"✅ Created and linked entity: {entity_id}")

    # ========================================================================
    # Step 5: Create ITSI KPIs
    # ========================================================================
    print("\n[5] Creating ITSI KPIs...")

    # KPI 1: API Latency (Performance)
    kpi_latency = ITSIKPI(
        kpi_id="KPI-LATENCY-P95",
        kpi_name="API Latency P95",
        description="95th percentile API response time",
        kpi_type=KPIType.PERFORMANCE,
        service_id=service_id,
        unit="ms",
        aggregation=KPIAggregation(
            method="p95",
            field="response_time",
            time_window=300  # 5 minutes
        ),
        base_search='index=cmdb sourcetype=api_logs service_id="SVC-AI-SECURITY-OPS" | stats p95(response_time) as latency_p95',
        thresholds=[
            KPIThreshold(level=KPIThresholdLevel.NORMAL, operator="lte", value=500, severity=1),
            KPIThreshold(level=KPIThresholdLevel.MEDIUM, operator="gt", value=500, severity=5),
            KPIThreshold(level=KPIThresholdLevel.HIGH, operator="gt", value=1000, severity=7),
            KPIThreshold(level=KPIThresholdLevel.CRITICAL, operator="gt", value=2000, severity=10)
        ],
        baseline_value=400.0,
        baseline_id=baseline_id
    )

    cmdb.create_itsi_kpi(kpi_latency)
    print(f"✅ Created KPI: {kpi_latency.kpi_id} (Performance)")

    # KPI 2: Availability (Uptime)
    kpi_availability = ITSIKPI(
        kpi_id="KPI-AVAILABILITY",
        kpi_name="Service Availability",
        description="Service uptime percentage",
        kpi_type=KPIType.AVAILABILITY,
        service_id=service_id,
        unit="%",
        aggregation=KPIAggregation(
            method="avg",
            field="uptime",
            time_window=3600  # 1 hour
        ),
        base_search='index=cmdb sourcetype=health_check service_id="SVC-AI-SECURITY-OPS" | stats avg(uptime) as availability',
        thresholds=[
            KPIThreshold(level=KPIThresholdLevel.CRITICAL, operator="lt", value=95.0, severity=10),
            KPIThreshold(level=KPIThresholdLevel.HIGH, operator="lt", value=98.0, severity=7),
            KPIThreshold(level=KPIThresholdLevel.MEDIUM, operator="lt", value=99.0, severity=5),
            KPIThreshold(level=KPIThresholdLevel.NORMAL, operator="gte", value=99.0, severity=1)
        ],
        baseline_value=99.5,
        baseline_id=baseline_id
    )

    cmdb.create_itsi_kpi(kpi_availability)
    print(f"✅ Created KPI: {kpi_availability.kpi_id} (Availability)")

    # KPI 3: Cost per Request
    kpi_cost = ITSIKPI(
        kpi_id="KPI-COST-PER-REQUEST",
        kpi_name="Cost per Request",
        description="Average cost per API request",
        kpi_type=KPIType.COST,
        service_id=service_id,
        unit="USD",
        aggregation=KPIAggregation(
            method="avg",
            field="cost_usd",
            time_window=3600  # 1 hour
        ),
        base_search='index=cmdb sourcetype=billing service_id="SVC-AI-SECURITY-OPS" | stats avg(cost_usd) as avg_cost',
        thresholds=[
            KPIThreshold(level=KPIThresholdLevel.NORMAL, operator="lte", value=0.05, severity=1),
            KPIThreshold(level=KPIThresholdLevel.MEDIUM, operator="gt", value=0.05, severity=5),
            KPIThreshold(level=KPIThresholdLevel.HIGH, operator="gt", value=0.10, severity=7),
            KPIThreshold(level=KPIThresholdLevel.CRITICAL, operator="gt", value=0.15, severity=10)
        ],
        baseline_value=0.04,
        baseline_id=baseline_id
    )

    cmdb.create_itsi_kpi(kpi_cost)
    print(f"✅ Created KPI: {kpi_cost.kpi_id} (Cost)")

    # KPI 4: Error Rate
    kpi_errors = ITSIKPI(
        kpi_id="KPI-ERROR-RATE",
        kpi_name="Error Rate",
        description="Percentage of failed requests",
        kpi_type=KPIType.QUALITY,
        service_id=service_id,
        unit="%",
        aggregation=KPIAggregation(
            method="avg",
            field="error_rate",
            time_window=300  # 5 minutes
        ),
        base_search='index=cmdb sourcetype=api_logs service_id="SVC-AI-SECURITY-OPS" status>=400 | stats count as errors by service_id',
        thresholds=[
            KPIThreshold(level=KPIThresholdLevel.NORMAL, operator="lte", value=1.0, severity=1),
            KPIThreshold(level=KPIThresholdLevel.MEDIUM, operator="gt", value=1.0, severity=5),
            KPIThreshold(level=KPIThresholdLevel.HIGH, operator="gt", value=5.0, severity=7),
            KPIThreshold(level=KPIThresholdLevel.CRITICAL, operator="gt", value=10.0, severity=10)
        ],
        baseline_value=0.5,
        baseline_id=baseline_id
    )

    cmdb.create_itsi_kpi(kpi_errors)
    print(f"✅ Created KPI: {kpi_errors.kpi_id} (Quality)")

    # ========================================================================
    # Step 6: Record KPI Measurements
    # ========================================================================
    print("\n[6] Recording KPI measurements...")

    # Measurement 1: Normal latency
    result1 = cmdb.record_kpi_measurement("KPI-LATENCY-P95", 450.0)
    print(f"   Latency: {result1['value']}ms -> {result1['status']} (baseline: 400ms)")

    # Measurement 2: Normal availability
    result2 = cmdb.record_kpi_measurement("KPI-AVAILABILITY", 99.7)
    print(f"   Availability: {result2['value']}% -> {result2['status']} (baseline: 99.5%)")

    # Measurement 3: Cost within threshold
    result3 = cmdb.record_kpi_measurement("KPI-COST-PER-REQUEST", 0.045)
    print(f"   Cost: ${result3['value']} -> {result3['status']} (baseline: $0.04)")

    # Measurement 4: Low error rate
    result4 = cmdb.record_kpi_measurement("KPI-ERROR-RATE", 0.3)
    print(f"   Errors: {result4['value']}% -> {result4['status']} (baseline: 0.5%)")

    # Calculate service health based on KPIs
    kpi_statuses = cmdb.get_kpi_status(service_id)
    all_normal = all(kpi['status'] == 'normal' for kpi in kpi_statuses)

    if all_normal:
        health_score = 100.0
        health_status = ServiceHealth.NORMAL
    else:
        health_score = 85.0
        health_status = ServiceHealth.WARNING

    cmdb.update_service_health(service_id, health_score, health_status)
    print(f"\n✅ Updated service health: {health_status.value} ({health_score})")

    # ========================================================================
    # Step 7: Simulate Threshold Breach
    # ========================================================================
    print("\n[7] Simulating threshold breach...")

    # High latency
    result_breach = cmdb.record_kpi_measurement("KPI-LATENCY-P95", 1200.0)
    print(f"   Latency: {result_breach['value']}ms -> {result_breach['status']} ⚠️")
    print(f"   Breached thresholds: {result_breach['breached_thresholds']}")
    print(f"   Deviation from baseline: {result_breach['baseline_deviation']}ms")

    # Update service health to WARNING
    cmdb.update_service_health(service_id, 75.0, ServiceHealth.WARNING)
    print(f"   Service health downgraded to WARNING")

    # ========================================================================
    # Step 8: Retrieve ITSI Events for Splunk Ingestion
    # ========================================================================
    print("\n[8] Retrieving ITSI events for Splunk ingestion...")

    pending_events = cmdb.get_pending_itsi_events(limit=10)
    print(f"   Pending events: {len(pending_events)}")

    for i, event in enumerate(pending_events[:3], 1):
        event_data = event.get('event', {})
        event_type = event_data.get('event_type', 'unknown')
        print(f"   [{i}] Type: {event_type}")

        if event_type == 'kpi_measurement':
            print(f"       KPI: {event_data.get('kpi_name')}")
            print(f"       Value: {event_data.get('measurement_value')} {event_data.get('unit')}")
            print(f"       Status: {event_data.get('status')}")

    # ========================================================================
    # Step 9: Display Summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("ITSI Integration Summary")
    print("=" * 70)

    service_doc = cmdb.get_itsi_service(service_id)
    print(f"\nService: {service_doc['service_name']}")
    print(f"  ID: {service_doc['service_id']}")
    print(f"  Health: {service_doc['health_status']} ({service_doc['health_score']})")
    print(f"  Tier: {service_doc['tier']}")
    print(f"  Criticality: {service_doc['criticality']}")
    print(f"  Owner: {service_doc['owner']}")

    print(f"\nKPIs ({len(kpi_statuses)}):")
    for kpi in kpi_statuses:
        status_icon = "✅" if kpi['status'] == 'normal' else "⚠️"
        print(f"  {status_icon} {kpi['kpi_name']}: {kpi.get('current_value')} ({kpi['status']})")

    entities = cmdb.get_service_entities(service_id)
    print(f"\nEntities ({len(entities)}):")
    for ent in entities:
        print(f"  • {ent['entity_name']} ({ent['entity_type']})")
        print(f"    CMDB CI: {ent['cmdb_ci_id']}")

    print(f"\nCMDB Integration:")
    print(f"  Configuration Items: {len(service_doc['cmdb_ci_ids'])}")
    print(f"  Baselines: 1 (approved)")
    print(f"  Drift Reports: 0")

    print(f"\nSplunk Integration:")
    print(f"  Pending Events: {len(pending_events)}")
    print(f"  Event Types: service_health, kpi_measurement, entity_discovery")

    print("\n" + "=" * 70)
    print("✅ ITSI Integration Complete")
    print("=" * 70)

    # Cleanup
    cmdb.close()


if __name__ == "__main__":
    main()
