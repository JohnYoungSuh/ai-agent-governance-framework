#!/usr/bin/env python3
"""
API Integration Tests
AI Agent Governance Framework - Internal v2.1

Comprehensive integration tests for CMDB REST API
Requires running API server on localhost:8000
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key-12345"  # Update with actual API key

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def record(self, test_name, passed, details=""):
        self.tests.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        if passed:
            self.passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {test_name} - {details}")

    def summary(self):
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed}/{total} passed ({pass_rate:.1f}%)")
        print("=" * 70)
        if self.failed > 0:
            print("\nFailed tests:")
            for test in self.tests:
                if not test["passed"]:
                    print(f"  - {test['test']}: {test['details']}")


def test_health_endpoint(results):
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                results.record("Health endpoint", True)
            else:
                results.record("Health endpoint", False, f"Status: {data.get('status')}")
        else:
            results.record("Health endpoint", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("Health endpoint", False, str(e))


def test_create_ci(results):
    """Test creating a configuration item"""
    ci_data = {
        "ci_id": "TEST-API-CI-001",
        "ci_type": "ai_agent",
        "name": "test-api-agent",
        "tier": 2,
        "environment": "development",
        "criticality": "low",
        "owner": "test@suhlabs.com",
        "configuration": {
            "model": "claude-sonnet-4-5",
            "memory_mb": 512
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/ci",
            headers=HEADERS,
            json=ci_data
        )

        if response.status_code == 201:
            data = response.json()
            if data.get("ci_id") == "TEST-API-CI-001":
                results.record("Create CI", True)
                return True
            else:
                results.record("Create CI", False, f"Wrong CI ID: {data}")
                return False
        else:
            results.record("Create CI", False, f"Status code: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        results.record("Create CI", False, str(e))
        return False


def test_get_ci(results):
    """Test retrieving a configuration item"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ci/TEST-API-CI-001")

        if response.status_code == 200:
            data = response.json()
            if data.get("ci_id") == "TEST-API-CI-001" and data.get("name") == "test-api-agent":
                results.record("Get CI", True)
                return data
            else:
                results.record("Get CI", False, f"Wrong data: {data}")
                return None
        else:
            results.record("Get CI", False, f"Status code: {response.status_code}")
            return None
    except Exception as e:
        results.record("Get CI", False, str(e))
        return None


def test_list_cis(results):
    """Test listing configuration items"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ci?ci_type=ai_agent")

        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) >= 1:
                results.record("List CIs", True)
            else:
                results.record("List CIs", False, f"No items: {data}")
        else:
            results.record("List CIs", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("List CIs", False, str(e))


def test_create_baseline(results, ci_data):
    """Test creating a baseline"""
    if not ci_data:
        results.record("Create Baseline", False, "No CI data")
        return False

    baseline_data = {
        "baseline_id": "TEST-API-BL-001",
        "baseline_type": "configuration",
        "name": "Test API Baseline",
        "ci_id": ci_data["ci_id"],
        "ci_name": ci_data["name"],
        "status": "draft",
        "configuration_snapshot": ci_data["configuration"],
        "configuration_hash": ci_data["configuration_hash"]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/baseline",
            headers=HEADERS,
            json=baseline_data
        )

        if response.status_code == 201:
            results.record("Create Baseline", True)
            return True
        else:
            results.record("Create Baseline", False, f"Status code: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        results.record("Create Baseline", False, str(e))
        return False


def test_approve_baseline(results):
    """Test approving a baseline"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/baseline/TEST-API-BL-001/approve",
            headers=HEADERS,
            json={"approver": "test-manager@suhlabs.com"}
        )

        if response.status_code == 200:
            results.record("Approve Baseline", True)
        else:
            results.record("Approve Baseline", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("Approve Baseline", False, str(e))


def test_create_change_request(results):
    """Test creating a change request"""
    cr_data = {
        "cr_id": "TEST-API-CR-001",
        "jira_url": "https://suhlabs.atlassian.net/browse/TEST-API-CR-001",
        "change_type": "configuration_update",
        "title": "Test API Change",
        "affected_cis": ["TEST-API-CI-001"],
        "planned_change": {
            "field": "configuration.memory_mb",
            "old_value": 512,
            "new_value": 1024,
            "justification": "Testing",
            "estimated_impact": {
                "cost_increase_monthly_usd": 10.0
            }
        },
        "approvals": [
            {
                "approver": "test-manager@suhlabs.com",
                "approved_at": datetime.utcnow().isoformat()
            }
        ]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/change-request",
            headers=HEADERS,
            json=cr_data
        )

        if response.status_code == 201:
            results.record("Create Change Request", True)
            return True
        else:
            results.record("Create Change Request", False, f"Status code: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        results.record("Create Change Request", False, str(e))
        return False


def test_detect_drift(results):
    """Test drift detection"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/drift/detect/TEST-API-CI-001",
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            # Drift may or may not be detected depending on CI state
            results.record("Detect Drift", True)
        else:
            results.record("Detect Drift", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("Detect Drift", False, str(e))


def test_create_itsi_service(results):
    """Test creating ITSI service"""
    service_data = {
        "service_id": "TEST-API-SVC-001",
        "service_name": "Test API Service",
        "service_type": "technical",
        "tier": 2,
        "criticality": "low",
        "owner": "test@suhlabs.com",
        "team": "Test Team",
        "cmdb_ci_ids": ["TEST-API-CI-001"]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/itsi/services",
            headers=HEADERS,
            json=service_data
        )

        if response.status_code == 201:
            results.record("Create ITSI Service", True)
            return True
        else:
            results.record("Create ITSI Service", False, f"Status code: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        results.record("Create ITSI Service", False, str(e))
        return False


def test_create_itsi_kpi(results):
    """Test creating ITSI KPI"""
    kpi_data = {
        "kpi_id": "TEST-API-KPI-001",
        "kpi_name": "Test API Latency",
        "kpi_type": "performance",
        "service_id": "TEST-API-SVC-001",
        "unit": "ms",
        "aggregation": {
            "method": "avg",
            "field": "latency",
            "time_window": 300
        },
        "base_search": "index=test",
        "thresholds": [
            {"level": "normal", "operator": "lte", "value": 100, "severity": 1},
            {"level": "critical", "operator": "gt", "value": 100, "severity": 10}
        ]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/itsi/kpis",
            headers=HEADERS,
            json=kpi_data
        )

        if response.status_code == 201:
            results.record("Create ITSI KPI", True)
            return True
        else:
            results.record("Create ITSI KPI", False, f"Status code: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        results.record("Create ITSI KPI", False, str(e))
        return False


def test_record_kpi_measurement(results):
    """Test recording KPI measurement"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/itsi/kpis/TEST-API-KPI-001/measure",
            headers=HEADERS,
            json={"value": 50.0}
        )

        if response.status_code == 200:
            data = response.json()
            if "value" in data and "status" in data:
                results.record("Record KPI Measurement", True)
            else:
                results.record("Record KPI Measurement", False, f"Missing fields: {data}")
        else:
            results.record("Record KPI Measurement", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("Record KPI Measurement", False, str(e))


def test_create_itsi_entity(results):
    """Test creating ITSI entity"""
    entity_data = {
        "entity_id": "TEST-API-ENT-001",
        "entity_name": "test-api-entity",
        "entity_type": "ai_agent",
        "environment": "development",
        "cmdb_ci_id": "TEST-API-CI-001"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/itsi/entities",
            headers=HEADERS,
            json=entity_data
        )

        if response.status_code == 201:
            results.record("Create ITSI Entity", True)
            return True
        else:
            results.record("Create ITSI Entity", False, f"Status code: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        results.record("Create ITSI Entity", False, str(e))
        return False


def test_link_entity_to_service(results):
    """Test linking entity to service"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/itsi/entities/TEST-API-ENT-001/link/TEST-API-SVC-001",
            headers=HEADERS
        )

        if response.status_code == 200:
            results.record("Link Entity to Service", True)
        else:
            results.record("Link Entity to Service", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("Link Entity to Service", False, str(e))


def test_get_kpi_status(results):
    """Test getting KPI status"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/itsi/services/TEST-API-SVC-001/kpis"
        )

        if response.status_code == 200:
            data = response.json()
            if "kpis" in data and len(data["kpis"]) >= 1:
                results.record("Get KPI Status", True)
            else:
                results.record("Get KPI Status", False, f"No KPIs: {data}")
        else:
            results.record("Get KPI Status", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("Get KPI Status", False, str(e))


def test_get_statistics(results):
    """Test getting CMDB statistics"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/statistics")

        if response.status_code == 200:
            data = response.json()
            if "total_cis" in data and "total_baselines" in data:
                results.record("Get Statistics", True)
            else:
                results.record("Get Statistics", False, f"Missing fields: {data}")
        else:
            results.record("Get Statistics", False, f"Status code: {response.status_code}")
    except Exception as e:
        results.record("Get Statistics", False, str(e))


def test_authentication_required(results):
    """Test that authentication is required for write operations"""
    try:
        # Try to create CI without API key
        response = requests.post(
            f"{BASE_URL}/api/v1/ci",
            headers={"Content-Type": "application/json"},
            json={"ci_id": "UNAUTHORIZED", "ci_type": "ai_agent", "name": "test"}
        )

        if response.status_code == 403:
            results.record("Authentication Required", True)
        else:
            results.record("Authentication Required", False, f"Expected 403, got {response.status_code}")
    except Exception as e:
        results.record("Authentication Required", False, str(e))


def main():
    """Run all tests"""
    print("=" * 70)
    print("CMDB API Integration Tests")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Using API key: {API_KEY[:10]}...\n")

    results = TestResults()

    # Wait for API to be ready
    print("Checking API health...")
    time.sleep(1)

    # Run tests in order
    test_health_endpoint(results)
    test_authentication_required(results)

    # CMDB CI tests
    if test_create_ci(results):
        ci_data = test_get_ci(results)
        test_list_cis(results)

        # Baseline tests
        if test_create_baseline(results, ci_data):
            test_approve_baseline(results)

        # Change request tests
        test_create_change_request(results)

        # Drift detection
        test_detect_drift(results)

    # ITSI tests
    if test_create_itsi_service(results):
        if test_create_itsi_kpi(results):
            test_record_kpi_measurement(results)
            test_get_kpi_status(results)

        if test_create_itsi_entity(results):
            test_link_entity_to_service(results)

    # Statistics
    test_get_statistics(results)

    # Print summary
    results.summary()

    return results.failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
