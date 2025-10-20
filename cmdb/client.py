#!/usr/bin/env python3
"""
CMDB MongoDB Client
AI Agent Governance Framework - Internal v2.1
Control: CM-2, CM-3, CM-6, CM-8

MongoDB client for Configuration Management Database operations
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
import hashlib
import json
from bson import ObjectId

from schemas import (
    ConfigurationItem,
    ConfigurationBaseline,
    SecurityBaseline,
    ComplianceBaseline,
    PerformanceBaseline,
    ChangeRequest,
    DriftReport,
    COLLECTIONS,
    INDEXES,
    BaselineType,
    BaselineStatus
)

from itsi_schemas import (
    ITSIService,
    ITSIKPI,
    ITSIEntity,
    ServiceHealth,
    KPIThresholdLevel,
    ITSI_COLLECTIONS,
    create_service_health_event,
    create_kpi_measurement_event,
    create_entity_discovery_event
)


class CMDBClient:
    """
    MongoDB CMDB Client

    Provides operations for:
    - Configuration Items (CIs)
    - Baselines (4 types)
    - Change Requests (Jira CR integration)
    - Drift Detection
    - Audit Trail
    """

    def __init__(self, mongodb_uri: str = "mongodb://localhost:27017",
                 database: str = "cmdb",
                 initialize_indexes: bool = True):
        """
        Initialize CMDB client

        Args:
            mongodb_uri: MongoDB connection string
            database: Database name
            initialize_indexes: Create indexes on initialization
        """
        try:
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[database]

            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {database}")

            if initialize_indexes:
                self._create_indexes()

        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    def _create_indexes(self):
        """Create MongoDB indexes for performance"""
        print("Creating indexes...")

        for collection_name, indexes in INDEXES.items():
            collection = self.db[collection_name]
            for index_spec in indexes:
                try:
                    collection.create_index(
                        index_spec["keys"],
                        unique=index_spec.get("unique", False)
                    )
                except Exception as e:
                    print(f"Warning: Could not create index on {collection_name}: {e}")

        print("✅ Indexes created")

    # ========================================================================
    # Configuration Items (CI) Operations
    # ========================================================================

    def create_ci(self, ci: ConfigurationItem) -> str:
        """
        Create a new Configuration Item

        Args:
            ci: ConfigurationItem object

        Returns:
            ci_id of created item
        """
        # Calculate hash before storing
        ci.update_hash()

        ci_dict = ci.model_dump(mode='json')
        ci_dict['_id'] = ObjectId()

        try:
            result = self.db[COLLECTIONS["configuration_items"]].insert_one(ci_dict)
            print(f"✅ Created CI: {ci.ci_id}")
            return ci.ci_id
        except DuplicateKeyError:
            raise ValueError(f"CI with id {ci.ci_id} already exists")

    def get_ci(self, ci_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Configuration Item by ID

        Args:
            ci_id: CI identifier

        Returns:
            CI document or None
        """
        ci = self.db[COLLECTIONS["configuration_items"]].find_one({"ci_id": ci_id})
        if ci:
            ci.pop('_id', None)  # Remove MongoDB ObjectId
        return ci

    def update_ci(self, ci_id: str, updates: Dict[str, Any],
                  jira_cr_id: Optional[str] = None) -> bool:
        """
        Update Configuration Item

        Args:
            ci_id: CI identifier
            updates: Fields to update
            jira_cr_id: Optional Jira CR ID for change tracking

        Returns:
            True if updated successfully
        """
        # Get current CI
        current_ci = self.get_ci(ci_id)
        if not current_ci:
            raise ValueError(f"CI {ci_id} not found")

        # Update configuration
        current_ci['configuration'].update(updates.get('configuration', {}))

        # Recalculate hash
        config_json = json.dumps(current_ci['configuration'], sort_keys=True)
        new_hash = f"sha256:{hashlib.sha256(config_json.encode()).hexdigest()}"

        update_doc = {
            "$set": {
                "configuration": current_ci['configuration'],
                "configuration_hash": new_hash,
                "updated_at": datetime.utcnow()
            }
        }

        # Add change reference if Jira CR provided
        if jira_cr_id:
            update_doc["$set"]["last_change_request"] = {
                "jira_cr_id": jira_cr_id,
                "change_date": datetime.utcnow(),
                "change_type": "configuration_update",
                "approver": updates.get('approver', 'unknown')
            }

        result = self.db[COLLECTIONS["configuration_items"]].update_one(
            {"ci_id": ci_id},
            update_doc
        )

        if result.modified_count > 0:
            print(f"✅ Updated CI: {ci_id}")
            return True
        return False

    def list_cis(self, ci_type: Optional[str] = None,
                 environment: Optional[str] = None,
                 tier: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List Configuration Items with filters

        Args:
            ci_type: Filter by CI type
            environment: Filter by environment
            tier: Filter by tier

        Returns:
            List of CIs
        """
        query = {}
        if ci_type:
            query['ci_type'] = ci_type
        if environment:
            query['environment'] = environment
        if tier:
            query['tier'] = tier

        cis = list(self.db[COLLECTIONS["configuration_items"]].find(query))

        # Remove ObjectIds
        for ci in cis:
            ci.pop('_id', None)

        return cis

    def delete_ci(self, ci_id: str) -> bool:
        """
        Delete Configuration Item

        Args:
            ci_id: CI identifier

        Returns:
            True if deleted successfully
        """
        result = self.db[COLLECTIONS["configuration_items"]].delete_one({"ci_id": ci_id})
        if result.deleted_count > 0:
            print(f"✅ Deleted CI: {ci_id}")
            return True
        return False

    # ========================================================================
    # Baseline Operations
    # ========================================================================

    def create_baseline(self, baseline: Any) -> str:
        """
        Create a new baseline (any type)

        Args:
            baseline: Baseline object (ConfigurationBaseline, SecurityBaseline, etc.)

        Returns:
            baseline_id
        """
        baseline_dict = baseline.model_dump(mode='json')
        baseline_dict['_id'] = ObjectId()

        try:
            result = self.db[COLLECTIONS["baselines"]].insert_one(baseline_dict)
            print(f"✅ Created Baseline: {baseline.baseline_id} (type: {baseline.baseline_type})")
            return baseline.baseline_id
        except DuplicateKeyError:
            raise ValueError(f"Baseline with id {baseline.baseline_id} already exists")

    def get_baseline(self, baseline_id: str) -> Optional[Dict[str, Any]]:
        """
        Get baseline by ID

        Args:
            baseline_id: Baseline identifier

        Returns:
            Baseline document or None
        """
        baseline = self.db[COLLECTIONS["baselines"]].find_one({"baseline_id": baseline_id})
        if baseline:
            baseline.pop('_id', None)
        return baseline

    def get_current_baseline(self, ci_id: str,
                            baseline_type: BaselineType = BaselineType.CONFIGURATION) -> Optional[Dict[str, Any]]:
        """
        Get current approved baseline for a CI

        Args:
            ci_id: Configuration Item ID
            baseline_type: Type of baseline

        Returns:
            Current baseline or None
        """
        baseline = self.db[COLLECTIONS["baselines"]].find_one({
            "ci_id": ci_id,
            "baseline_type": baseline_type.value,
            "status": BaselineStatus.APPROVED.value
        }, sort=[("approved_at", DESCENDING)])

        if baseline:
            baseline.pop('_id', None)
        return baseline

    def approve_baseline(self, baseline_id: str, approver: str,
                        signature: Optional[str] = None) -> bool:
        """
        Approve a baseline

        Args:
            baseline_id: Baseline identifier
            approver: Email of approver
            signature: Optional digital signature

        Returns:
            True if approved successfully
        """
        update_doc = {
            "$set": {
                "status": BaselineStatus.APPROVED.value,
                "approved_at": datetime.utcnow(),
                "approved_by": approver
            }
        }

        if signature:
            update_doc["$set"]["signature"] = signature

        result = self.db[COLLECTIONS["baselines"]].update_one(
            {"baseline_id": baseline_id},
            update_doc
        )

        if result.modified_count > 0:
            # Update CI to reference this baseline
            baseline = self.get_baseline(baseline_id)
            if baseline:
                self.db[COLLECTIONS["configuration_items"]].update_one(
                    {"ci_id": baseline['ci_id']},
                    {
                        "$set": {"current_baseline_id": baseline_id},
                        "$addToSet": {"approved_baselines": baseline_id}
                    }
                )

            print(f"✅ Approved Baseline: {baseline_id}")
            return True
        return False

    def list_baselines(self, ci_id: Optional[str] = None,
                      baseline_type: Optional[BaselineType] = None,
                      status: Optional[BaselineStatus] = None) -> List[Dict[str, Any]]:
        """
        List baselines with filters

        Args:
            ci_id: Filter by CI
            baseline_type: Filter by type
            status: Filter by status

        Returns:
            List of baselines
        """
        query = {}
        if ci_id:
            query['ci_id'] = ci_id
        if baseline_type:
            query['baseline_type'] = baseline_type.value
        if status:
            query['status'] = status.value

        baselines = list(self.db[COLLECTIONS["baselines"]].find(query).sort("created_at", DESCENDING))

        for baseline in baselines:
            baseline.pop('_id', None)

        return baselines

    # ========================================================================
    # Change Request Operations
    # ========================================================================

    def create_change_request(self, cr: ChangeRequest) -> str:
        """
        Create a change request

        Args:
            cr: ChangeRequest object

        Returns:
            cr_id
        """
        cr_dict = cr.model_dump(mode='json')
        cr_dict['_id'] = ObjectId()

        try:
            result = self.db[COLLECTIONS["change_requests"]].insert_one(cr_dict)
            print(f"✅ Created Change Request: {cr.cr_id}")
            return cr.cr_id
        except DuplicateKeyError:
            raise ValueError(f"Change Request with id {cr.cr_id} already exists")

    def get_change_request(self, cr_id: str) -> Optional[Dict[str, Any]]:
        """
        Get change request by ID

        Args:
            cr_id: Change request identifier

        Returns:
            CR document or None
        """
        cr = self.db[COLLECTIONS["change_requests"]].find_one({"cr_id": cr_id})
        if cr:
            cr.pop('_id', None)
        return cr

    def record_actual_change(self, cr_id: str, actual_change: Dict[str, Any]) -> bool:
        """
        Record actual change after implementation

        Args:
            cr_id: Change request identifier
            actual_change: Actual change details

        Returns:
            True if recorded successfully
        """
        cr = self.get_change_request(cr_id)
        if not cr:
            raise ValueError(f"Change Request {cr_id} not found")

        # Calculate variance
        planned = cr['planned_change']

        cost_variance = (
            actual_change['actual_impact'].get('cost_increase_monthly_usd', 0) -
            planned['estimated_impact'].get('cost_increase_monthly_usd', 0)
        )

        perf_variance = (
            actual_change['actual_impact'].get('performance_improvement_percent', 0) -
            planned['estimated_impact'].get('performance_improvement_percent', 0)
        )

        # Check if within tolerance (±10%)
        cost_tolerance = abs(planned['estimated_impact'].get('cost_increase_monthly_usd', 1)) * 0.10
        perf_tolerance = abs(planned['estimated_impact'].get('performance_improvement_percent', 1)) * 0.10

        within_tolerance = (
            abs(cost_variance) <= cost_tolerance and
            abs(perf_variance) <= perf_tolerance
        )

        variance = {
            "cost_variance_usd": cost_variance,
            "performance_variance_percent": perf_variance,
            "within_tolerance": within_tolerance
        }

        # Calculate tit-for-tat accuracy score
        if planned['estimated_impact'].get('cost_increase_monthly_usd', 0) != 0:
            cost_accuracy = 1.0 - min(
                abs(cost_variance) / abs(planned['estimated_impact']['cost_increase_monthly_usd']),
                1.0
            )
        else:
            cost_accuracy = 1.0

        if planned['estimated_impact'].get('performance_improvement_percent', 0) != 0:
            perf_accuracy = 1.0 - min(
                abs(perf_variance) / abs(planned['estimated_impact']['performance_improvement_percent']),
                1.0
            )
        else:
            perf_accuracy = 1.0

        accuracy_score = (cost_accuracy + perf_accuracy) / 2.0

        update_doc = {
            "$set": {
                "actual_change": actual_change,
                "variance": variance,
                "tit_for_tat_score.accuracy_score": accuracy_score
            }
        }

        result = self.db[COLLECTIONS["change_requests"]].update_one(
            {"cr_id": cr_id},
            update_doc
        )

        if result.modified_count > 0:
            print(f"✅ Recorded actual change for CR: {cr_id}")
            print(f"   Variance: Cost=${cost_variance:.2f}, Perf={perf_variance:.1f}%")
            print(f"   Accuracy Score: {accuracy_score:.2f}")
            return True
        return False

    # ========================================================================
    # Drift Detection Operations
    # ========================================================================

    def detect_drift(self, ci_id: str) -> Optional[DriftReport]:
        """
        Detect configuration drift for a CI

        Compares current configuration hash with baseline hash

        Args:
            ci_id: Configuration Item ID

        Returns:
            DriftReport if drift detected, None otherwise
        """
        # Get current CI
        ci = self.get_ci(ci_id)
        if not ci:
            raise ValueError(f"CI {ci_id} not found")

        # Get current baseline
        baseline = self.get_current_baseline(ci_id)
        if not baseline:
            print(f"⚠️  No baseline found for CI: {ci_id}")
            return None

        current_hash = ci.get('configuration_hash')
        baseline_hash = baseline.get('configuration_hash')

        if current_hash != baseline_hash:
            # Drift detected - find differences
            differences = self._compare_configurations(
                baseline['configuration_snapshot'],
                ci['configuration']
            )

            # Determine severity based on number of differences
            num_diffs = len(differences)
            if num_diffs > 10:
                severity = "critical"
            elif num_diffs > 5:
                severity = "high"
            elif num_diffs > 2:
                severity = "medium"
            else:
                severity = "low"

            drift_report = DriftReport(
                drift_id=f"DRIFT-{ci_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                ci_id=ci_id,
                detected_at=datetime.utcnow(),
                severity=severity,
                drift_type="configuration_mismatch",
                current_hash=current_hash,
                baseline_hash=baseline_hash,
                differences=differences,
                remediation_required=True
            )

            # Store drift report
            drift_dict = drift_report.model_dump(mode='json')
            drift_dict['_id'] = ObjectId()
            self.db[COLLECTIONS["drift_reports"]].insert_one(drift_dict)

            print(f"⚠️  DRIFT DETECTED: {ci_id}")
            print(f"   Severity: {severity}")
            print(f"   Differences: {num_diffs}")

            return drift_report
        else:
            print(f"✅ No drift detected: {ci_id}")
            return None

    def _compare_configurations(self, baseline_config: Dict[str, Any],
                                current_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compare two configurations and return differences

        Args:
            baseline_config: Baseline configuration
            current_config: Current configuration

        Returns:
            List of differences
        """
        differences = []

        # Check for changed fields
        all_keys = set(baseline_config.keys()) | set(current_config.keys())

        for key in all_keys:
            baseline_value = baseline_config.get(key)
            current_value = current_config.get(key)

            if baseline_value != current_value:
                differences.append({
                    "field": key,
                    "baseline_value": baseline_value,
                    "current_value": current_value,
                    "change_type": self._determine_change_type(baseline_value, current_value)
                })

        return differences

    def _determine_change_type(self, baseline_value: Any, current_value: Any) -> str:
        """Determine type of change"""
        if baseline_value is None:
            return "added"
        elif current_value is None:
            return "removed"
        else:
            return "modified"

    def get_drift_reports(self, ci_id: Optional[str] = None,
                         severity: Optional[str] = None,
                         remediation_required: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get drift reports with filters

        Args:
            ci_id: Filter by CI
            severity: Filter by severity
            remediation_required: Filter by remediation status

        Returns:
            List of drift reports
        """
        query = {}
        if ci_id:
            query['ci_id'] = ci_id
        if severity:
            query['severity'] = severity
        if remediation_required is not None:
            query['remediation_required'] = remediation_required

        reports = list(self.db[COLLECTIONS["drift_reports"]].find(query).sort("detected_at", DESCENDING))

        for report in reports:
            report.pop('_id', None)

        return reports

    # ========================================================================
    # Graph Query Operations (Neo4j-style patterns)
    # ========================================================================

    def get_ci_relationships(self, ci_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get CI relationships (graph traversal)

        Args:
            ci_id: Configuration Item ID
            relationship_type: Optional filter by relationship type

        Returns:
            List of related CIs
        """
        ci = self.get_ci(ci_id)
        if not ci:
            return []

        relationships = ci.get('relationships', [])

        if relationship_type:
            relationships = [r for r in relationships if r['type'] == relationship_type]

        # Fetch related CIs
        related_cis = []
        for rel in relationships:
            target_ci = self.get_ci(rel['target_ci_id'])
            if target_ci:
                related_cis.append({
                    "relationship": rel,
                    "ci": target_ci
                })

        return related_cis

    def find_cis_implementing_control(self, control_id: str) -> List[Dict[str, Any]]:
        """
        Find all CIs implementing a specific control

        Args:
            control_id: Control identifier (e.g., "CM-2", "SEC-001")

        Returns:
            List of CIs
        """
        cis = self.db[COLLECTIONS["configuration_items"]].find({
            "relationships": {
                "$elemMatch": {
                    "type": "IMPLEMENTS",
                    "target_ci_id": control_id
                }
            }
        })

        result = list(cis)
        for ci in result:
            ci.pop('_id', None)

        return result

    # ========================================================================
    # Utility Operations
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get CMDB statistics"""
        stats = {
            "total_cis": self.db[COLLECTIONS["configuration_items"]].count_documents({}),
            "total_baselines": self.db[COLLECTIONS["baselines"]].count_documents({}),
            "total_change_requests": self.db[COLLECTIONS["change_requests"]].count_documents({}),
            "total_drift_reports": self.db[COLLECTIONS["drift_reports"]].count_documents({}),
            "cis_by_type": {},
            "cis_by_environment": {},
            "baselines_by_status": {},
            "drift_by_severity": {}
        }

        # CIs by type
        pipeline = [{"$group": {"_id": "$ci_type", "count": {"$sum": 1}}}]
        for doc in self.db[COLLECTIONS["configuration_items"]].aggregate(pipeline):
            stats["cis_by_type"][doc['_id']] = doc['count']

        # CIs by environment
        pipeline = [{"$group": {"_id": "$environment", "count": {"$sum": 1}}}]
        for doc in self.db[COLLECTIONS["configuration_items"]].aggregate(pipeline):
            stats["cis_by_environment"][doc['_id']] = doc['count']

        # Baselines by status
        pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
        for doc in self.db[COLLECTIONS["baselines"]].aggregate(pipeline):
            stats["baselines_by_status"][doc['_id']] = doc['count']

        # Drift by severity
        pipeline = [{"$group": {"_id": "$severity", "count": {"$sum": 1}}}]
        for doc in self.db[COLLECTIONS["drift_reports"]].aggregate(pipeline):
            stats["drift_by_severity"][doc['_id']] = doc['count']

        return stats

    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("✅ MongoDB connection closed")

    # ========================================================================
    # ITSI Service Operations
    # ========================================================================

    def create_itsi_service(self, service: ITSIService) -> str:
        """
        Create ITSI service

        Args:
            service: ITSIService model

        Returns:
            Service ID
        """
        service_dict = service.model_dump(mode='json')
        service_dict['_id'] = ObjectId()

        self.db[ITSI_COLLECTIONS["services"]].insert_one(service_dict)

        # Create service health event for Splunk ingestion
        event = create_service_health_event(service)
        self._log_itsi_event(event.to_hec_format())

        print(f"✅ Created ITSI service: {service.service_id}")
        return service.service_id

    def get_itsi_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get ITSI service by ID

        Args:
            service_id: Service ID

        Returns:
            Service document or None
        """
        service = self.db[ITSI_COLLECTIONS["services"]].find_one({"service_id": service_id})
        if service:
            service.pop('_id', None)
        return service

    def update_service_health(self, service_id: str, health_score: float,
                             health_status: ServiceHealth) -> bool:
        """
        Update ITSI service health

        Args:
            service_id: Service ID
            health_score: Health score (0-100)
            health_status: ServiceHealth enum

        Returns:
            True if updated successfully
        """
        result = self.db[ITSI_COLLECTIONS["services"]].update_one(
            {"service_id": service_id},
            {
                "$set": {
                    "health_score": health_score,
                    "health_status": health_status.value,
                    "last_health_update": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if result.modified_count > 0:
            # Get updated service and log event
            service_dict = self.get_itsi_service(service_id)
            if service_dict:
                service = ITSIService(**service_dict)
                event = create_service_health_event(service)
                self._log_itsi_event(event.to_hec_format())

            print(f"✅ Updated service health: {service_id} -> {health_status.value} ({health_score})")
            return True
        return False

    def list_itsi_services(self, criticality: Optional[str] = None,
                          tier: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List ITSI services with filters

        Args:
            criticality: Filter by criticality
            tier: Filter by tier

        Returns:
            List of services
        """
        query = {}
        if criticality:
            query['criticality'] = criticality
        if tier:
            query['tier'] = tier

        services = list(self.db[ITSI_COLLECTIONS["services"]].find(query))
        for service in services:
            service.pop('_id', None)

        return services

    # ========================================================================
    # ITSI KPI Operations
    # ========================================================================

    def create_itsi_kpi(self, kpi: ITSIKPI) -> str:
        """
        Create ITSI KPI

        Args:
            kpi: ITSIKPI model

        Returns:
            KPI ID
        """
        kpi_dict = kpi.model_dump(mode='json')
        kpi_dict['_id'] = ObjectId()

        self.db[ITSI_COLLECTIONS["kpis"]].insert_one(kpi_dict)

        print(f"✅ Created ITSI KPI: {kpi.kpi_id}")
        return kpi.kpi_id

    def record_kpi_measurement(self, kpi_id: str, value: float) -> Dict[str, Any]:
        """
        Record KPI measurement and evaluate thresholds

        Args:
            kpi_id: KPI ID
            value: Measured value

        Returns:
            Measurement result with status
        """
        kpi_dict = self.db[ITSI_COLLECTIONS["kpis"]].find_one({"kpi_id": kpi_id})
        if not kpi_dict:
            raise ValueError(f"KPI not found: {kpi_id}")

        kpi_dict.pop('_id', None)
        kpi = ITSIKPI(**kpi_dict)

        # Evaluate thresholds
        status = KPIThresholdLevel.NORMAL
        breached_thresholds = []

        for threshold in sorted(kpi.thresholds, key=lambda t: t.severity, reverse=True):
            if self._evaluate_threshold(value, threshold.operator, threshold.value):
                status = threshold.level
                breached_thresholds.append(threshold.level.value)
                break

        # Update KPI
        self.db[ITSI_COLLECTIONS["kpis"]].update_one(
            {"kpi_id": kpi_id},
            {
                "$set": {
                    "current_value": value,
                    "last_measured": datetime.utcnow(),
                    "status": status.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Create KPI measurement event
        event = create_kpi_measurement_event(kpi, value, status)
        self._log_itsi_event(event.to_hec_format())

        result = {
            "kpi_id": kpi_id,
            "value": value,
            "status": status.value,
            "breached_thresholds": breached_thresholds,
            "baseline_deviation": value - kpi.baseline_value if kpi.baseline_value else None,
            "measured_at": datetime.utcnow()
        }

        print(f"✅ Recorded KPI measurement: {kpi_id} = {value} ({status.value})")
        return result

    def get_kpi_status(self, service_id: str) -> List[Dict[str, Any]]:
        """
        Get current status of all KPIs for a service

        Args:
            service_id: Service ID

        Returns:
            List of KPI statuses
        """
        kpis = list(self.db[ITSI_COLLECTIONS["kpis"]].find({"service_id": service_id}))

        statuses = []
        for kpi in kpis:
            kpi.pop('_id', None)
            statuses.append({
                "kpi_id": kpi["kpi_id"],
                "kpi_name": kpi["kpi_name"],
                "current_value": kpi.get("current_value"),
                "status": kpi.get("status", "normal"),
                "baseline_value": kpi.get("baseline_value"),
                "last_measured": kpi.get("last_measured")
            })

        return statuses

    def _evaluate_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate threshold condition"""
        if operator == "gt":
            return value > threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "lte":
            return value <= threshold
        elif operator == "eq":
            return value == threshold
        return False

    # ========================================================================
    # ITSI Entity Operations
    # ========================================================================

    def create_itsi_entity(self, entity: ITSIEntity) -> str:
        """
        Create ITSI entity

        Args:
            entity: ITSIEntity model

        Returns:
            Entity ID
        """
        entity_dict = entity.model_dump(mode='json')
        entity_dict['_id'] = ObjectId()

        self.db[ITSI_COLLECTIONS["entities"]].insert_one(entity_dict)

        # Create entity discovery event
        event = create_entity_discovery_event(entity)
        self._log_itsi_event(event.to_hec_format())

        print(f"✅ Created ITSI entity: {entity.entity_id}")
        return entity.entity_id

    def link_entity_to_service(self, entity_id: str, service_id: str) -> bool:
        """
        Link entity to service

        Args:
            entity_id: Entity ID
            service_id: Service ID

        Returns:
            True if linked successfully
        """
        # Add service to entity
        result1 = self.db[ITSI_COLLECTIONS["entities"]].update_one(
            {"entity_id": entity_id},
            {"$addToSet": {"services": service_id}}
        )

        # Add entity to service
        result2 = self.db[ITSI_COLLECTIONS["services"]].update_one(
            {"service_id": service_id},
            {"$addToSet": {"entities": entity_id}}
        )

        if result1.modified_count > 0 or result2.modified_count > 0:
            print(f"✅ Linked entity {entity_id} to service {service_id}")
            return True
        return False

    def get_service_entities(self, service_id: str) -> List[Dict[str, Any]]:
        """
        Get all entities for a service

        Args:
            service_id: Service ID

        Returns:
            List of entities
        """
        service = self.get_itsi_service(service_id)
        if not service:
            return []

        entity_ids = service.get('entities', [])
        entities = list(self.db[ITSI_COLLECTIONS["entities"]].find(
            {"entity_id": {"$in": entity_ids}}
        ))

        for entity in entities:
            entity.pop('_id', None)

        return entities

    # ========================================================================
    # ITSI Logging Operations
    # ========================================================================

    def _log_itsi_event(self, event: Dict[str, Any]) -> None:
        """
        Log ITSI event for Splunk HEC ingestion

        This method can be extended to send events to Splunk HEC endpoint
        For now, it stores events in a local collection

        Args:
            event: HEC-formatted event
        """
        # Store in local events collection for pickup by Splunk forwarder
        event['_id'] = ObjectId()
        event['ingested'] = False
        event['created_at'] = datetime.utcnow()

        # Using CMDB events collection (could be separate ITSI events collection)
        self.db['itsi_events'].insert_one(event)

    def get_pending_itsi_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get pending ITSI events for Splunk ingestion

        Args:
            limit: Maximum number of events to retrieve

        Returns:
            List of pending events
        """
        events = list(self.db['itsi_events'].find(
            {"ingested": False}
        ).limit(limit))

        for event in events:
            event.pop('_id', None)

        return events

    def mark_events_ingested(self, event_ids: List[str]) -> int:
        """
        Mark events as ingested by Splunk

        Args:
            event_ids: List of event IDs

        Returns:
            Number of events marked
        """
        result = self.db['itsi_events'].update_many(
            {"event.event_id": {"$in": event_ids}},
            {"$set": {"ingested": True, "ingested_at": datetime.utcnow()}}
        )

        return result.modified_count
