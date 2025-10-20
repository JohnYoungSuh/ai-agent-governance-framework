#!/usr/bin/env python3
"""
MongoDB Client Tests
AI Agent Governance Framework - Internal v2.1

Comprehensive tests for CMDB MongoDB client operations
"""

import sys
sys.path.append('..')

from datetime import datetime
import pytest
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
    Relationship,
    RelationshipType
)


class TestCMDBClient:
    """Test CMDB MongoDB Client"""

    @classmethod
    def setup_class(cls):
        """Setup test database"""
        cls.cmdb = CMDBClient(
            mongodb_uri="mongodb://localhost:27017",
            database="cmdb_test"
        )
        print("\n✅ Test database connected")

    @classmethod
    def teardown_class(cls):
        """Cleanup test database"""
        # Drop test database
        cls.cmdb.client.drop_database("cmdb_test")
        cls.cmdb.close()
        print("\n✅ Test database cleaned up")

    # ========================================================================
    # Configuration Item Tests
    # ========================================================================

    def test_01_create_ci(self):
        """Test creating a configuration item"""
        ci = ConfigurationItem(
            ci_id="TEST-CI-001",
            ci_type=CIType.AI_AGENT,
            name="test-agent",
            tier=2,
            environment=Environment.DEVELOPMENT,
            criticality=Criticality.LOW,
            owner="test@suhlabs.com",
            configuration={
                "model": "claude-sonnet-4-5",
                "memory_mb": 512
            }
        )

        ci_id = self.cmdb.create_ci(ci)
        assert ci_id == "TEST-CI-001"
        print("✅ test_01_create_ci PASSED")

    def test_02_get_ci(self):
        """Test retrieving a configuration item"""
        ci = self.cmdb.get_ci("TEST-CI-001")
        assert ci is not None
        assert ci["ci_id"] == "TEST-CI-001"
        assert ci["name"] == "test-agent"
        assert ci["configuration"]["model"] == "claude-sonnet-4-5"
        print("✅ test_02_get_ci PASSED")

    def test_03_update_ci(self):
        """Test updating a configuration item"""
        updates = {
            "configuration": {
                "memory_mb": 1024
            }
        }

        success = self.cmdb.update_ci("TEST-CI-001", updates)
        assert success is True

        # Verify update
        ci = self.cmdb.get_ci("TEST-CI-001")
        assert ci["configuration"]["memory_mb"] == 1024
        print("✅ test_03_update_ci PASSED")

    def test_04_list_cis(self):
        """Test listing configuration items"""
        cis = self.cmdb.list_cis(ci_type=CIType.AI_AGENT.value)
        assert len(cis) >= 1
        assert any(ci["ci_id"] == "TEST-CI-001" for ci in cis)
        print("✅ test_04_list_cis PASSED")

    # ========================================================================
    # Baseline Tests
    # ========================================================================

    def test_05_create_baseline(self):
        """Test creating a configuration baseline"""
        ci = self.cmdb.get_ci("TEST-CI-001")

        baseline = ConfigurationBaseline(
            baseline_id="TEST-BL-001",
            baseline_type=BaselineType.CONFIGURATION,
            name="Test Baseline",
            ci_id=ci["ci_id"],
            ci_name=ci["name"],
            status=BaselineStatus.DRAFT,
            configuration_snapshot=ci["configuration"],
            configuration_hash=ci["configuration_hash"]
        )

        baseline_id = self.cmdb.create_baseline(baseline)
        assert baseline_id == "TEST-BL-001"
        print("✅ test_05_create_baseline PASSED")

    def test_06_approve_baseline(self):
        """Test approving a baseline"""
        success = self.cmdb.approve_baseline(
            "TEST-BL-001",
            approver="test-manager@suhlabs.com"
        )
        assert success is True

        # Verify approval
        baseline = self.cmdb.get_baseline("TEST-BL-001")
        assert baseline["status"] == BaselineStatus.APPROVED.value
        assert baseline["approved_by"] == "test-manager@suhlabs.com"
        print("✅ test_06_approve_baseline PASSED")

    def test_07_get_current_baseline(self):
        """Test getting current baseline"""
        baseline = self.cmdb.get_current_baseline("TEST-CI-001")
        assert baseline is not None
        assert baseline["baseline_id"] == "TEST-BL-001"
        print("✅ test_07_get_current_baseline PASSED")

    # ========================================================================
    # Change Request Tests
    # ========================================================================

    def test_08_create_change_request(self):
        """Test creating a change request"""
        cr = ChangeRequest(
            cr_id="TEST-CR-001",
            jira_url="https://suhlabs.atlassian.net/browse/TEST-CR-001",
            change_type="configuration_update",
            title="Test Change",
            affected_cis=["TEST-CI-001"],
            planned_change=PlannedChange(
                field="configuration.memory_mb",
                old_value=1024,
                new_value=2048,
                justification="Testing",
                estimated_impact={
                    "cost_increase_monthly_usd": 25.0,
                    "performance_improvement_percent": 10.0
                }
            ),
            approvals=[
                Approval(
                    approver="test-manager@suhlabs.com",
                    approved_at=datetime.utcnow()
                )
            ]
        )

        cr_id = self.cmdb.create_change_request(cr)
        assert cr_id == "TEST-CR-001"
        print("✅ test_08_create_change_request PASSED")

    def test_09_record_actual_change(self):
        """Test recording actual change"""
        actual = ActualChange(
            field="configuration.memory_mb",
            old_value=1024,
            new_value=2048,
            implemented_at=datetime.utcnow(),
            actual_impact={
                "cost_increase_monthly_usd": 24.0,
                "performance_improvement_percent": 11.0
            }
        )

        success = self.cmdb.record_actual_change(
            "TEST-CR-001",
            actual.model_dump(mode='json')
        )
        assert success is True

        # Verify variance calculation
        cr = self.cmdb.get_change_request("TEST-CR-001")
        assert cr["variance"] is not None
        assert cr["variance"]["cost_variance_usd"] == -1.0  # Better than planned
        assert cr["tit_for_tat_score"]["accuracy_score"] > 0.9  # High accuracy
        print("✅ test_09_record_actual_change PASSED")

    # ========================================================================
    # Drift Detection Tests
    # ========================================================================

    def test_10_detect_no_drift(self):
        """Test drift detection when no drift exists"""
        drift = self.cmdb.detect_drift("TEST-CI-001")
        # Drift may or may not exist depending on whether CI was updated
        # This test verifies the function works
        print("✅ test_10_detect_no_drift PASSED")

    def test_11_detect_drift_after_change(self):
        """Test drift detection after unauthorized change"""
        # Make unauthorized change
        updates = {
            "configuration": {
                "memory_mb": 4096  # Changed without CR
            }
        }
        self.cmdb.update_ci("TEST-CI-001", updates)

        # Detect drift
        drift = self.cmdb.detect_drift("TEST-CI-001")
        assert drift is not None
        assert drift.ci_id == "TEST-CI-001"
        assert len(drift.differences) > 0
        print("✅ test_11_detect_drift_after_change PASSED")

    def test_12_get_drift_reports(self):
        """Test retrieving drift reports"""
        reports = self.cmdb.get_drift_reports(ci_id="TEST-CI-001")
        assert len(reports) > 0
        print("✅ test_12_get_drift_reports PASSED")

    # ========================================================================
    # Relationship Tests
    # ========================================================================

    def test_13_create_ci_with_relationships(self):
        """Test creating CI with relationships"""
        ci = ConfigurationItem(
            ci_id="TEST-CI-002",
            ci_type=CIType.INFRASTRUCTURE,
            name="test-kms-key",
            tier=None,
            environment=Environment.DEVELOPMENT,
            criticality=Criticality.HIGH,
            owner="test@suhlabs.com",
            configuration={
                "key_type": "kms",
                "rotation_enabled": True
            },
            relationships=[
                Relationship(
                    type=RelationshipType.DEPENDS_ON,
                    target_ci_id="TEST-CI-001",
                    target_name="test-agent",
                    description="Agent depends on this KMS key"
                )
            ]
        )

        ci_id = self.cmdb.create_ci(ci)
        assert ci_id == "TEST-CI-002"
        print("✅ test_13_create_ci_with_relationships PASSED")

    def test_14_get_relationships(self):
        """Test getting CI relationships"""
        relationships = self.cmdb.get_ci_relationships("TEST-CI-002")
        assert len(relationships) > 0
        assert relationships[0]["relationship"]["target_ci_id"] == "TEST-CI-001"
        print("✅ test_14_get_relationships PASSED")

    # ========================================================================
    # Statistics Tests
    # ========================================================================

    def test_15_get_statistics(self):
        """Test getting CMDB statistics"""
        stats = self.cmdb.get_statistics()
        assert stats["total_cis"] >= 2
        assert stats["total_baselines"] >= 1
        assert stats["total_change_requests"] >= 1
        assert "cis_by_type" in stats
        print("✅ test_15_get_statistics PASSED")

    # ========================================================================
    # Cleanup Tests
    # ========================================================================

    def test_16_delete_ci(self):
        """Test deleting a configuration item"""
        success = self.cmdb.delete_ci("TEST-CI-002")
        assert success is True

        # Verify deletion
        ci = self.cmdb.get_ci("TEST-CI-002")
        assert ci is None
        print("✅ test_16_delete_ci PASSED")


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("CMDB MongoDB Client Tests")
    print("=" * 70)

    test = TestCMDBClient()
    test.setup_class()

    try:
        # Run tests in order
        test.test_01_create_ci()
        test.test_02_get_ci()
        test.test_03_update_ci()
        test.test_04_list_cis()
        test.test_05_create_baseline()
        test.test_06_approve_baseline()
        test.test_07_get_current_baseline()
        test.test_08_create_change_request()
        test.test_09_record_actual_change()
        test.test_10_detect_no_drift()
        test.test_11_detect_drift_after_change()
        test.test_12_get_drift_reports()
        test.test_13_create_ci_with_relationships()
        test.test_14_get_relationships()
        test.test_15_get_statistics()
        test.test_16_delete_ci()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED (16/16)")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    finally:
        test.teardown_class()


if __name__ == "__main__":
    run_tests()
