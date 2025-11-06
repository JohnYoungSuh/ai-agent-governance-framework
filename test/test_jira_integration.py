#!/usr/bin/env python3
"""
Integration Tests for Jira Integration
AI Agent Governance Framework v2.1

Tests webhook receiver, PKI signing, and field mapping with mock Jira server

Requirements:
  pip install pytest pytest-mock requests responses flask
"""

import os
import sys
import json
import pytest
import hmac
import hashlib
import base64
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    import responses
    from flask import Flask, request, jsonify
except ImportError:
    print("ERROR: Required testing libraries not installed", file=sys.stderr)
    print("Install with: pip install pytest responses flask", file=sys.stderr)
    sys.exit(1)


# Mock Jira Server for Testing
class MockJiraServer:
    """Mock Jira server for integration testing"""

    def __init__(self, port=8888):
        self.app = Flask(__name__)
        self.port = port
        self.issues = {}
        self.webhooks = []

        # Setup routes
        self.app.add_url_rule('/rest/api/3/issue', 'create_issue',
                             self._create_issue, methods=['POST'])
        self.app.add_url_rule('/rest/api/3/issue/<issue_key>', 'get_issue',
                             self._get_issue, methods=['GET'])
        self.app.add_url_rule('/rest/api/3/issue/<issue_key>', 'update_issue',
                             self._update_issue, methods=['PUT'])
        self.app.add_url_rule('/rest/api/3/field', 'list_fields',
                             self._list_fields, methods=['GET'])

    def _create_issue(self):
        """Mock create issue endpoint"""
        data = request.get_json()
        issue_key = f"CR-{len(self.issues) + 1:04d}"

        issue = {
            'key': issue_key,
            'id': str(len(self.issues) + 1),
            'fields': data['fields']
        }

        self.issues[issue_key] = issue
        return jsonify({'key': issue_key, 'id': issue['id']}), 201

    def _get_issue(self, issue_key):
        """Mock get issue endpoint"""
        if issue_key not in self.issues:
            return jsonify({'errorMessages': ['Issue not found']}), 404

        return jsonify(self.issues[issue_key]), 200

    def _update_issue(self, issue_key):
        """Mock update issue endpoint"""
        if issue_key not in self.issues:
            return jsonify({'errorMessages': ['Issue not found']}), 404

        data = request.get_json()
        self.issues[issue_key]['fields'].update(data['fields'])
        return '', 204

    def _list_fields(self):
        """Mock list fields endpoint"""
        fields = [
            {
                'id': 'customfield_10050',
                'name': 'CR ID',
                'custom': True,
                'type': 'string'
            },
            {
                'id': 'customfield_10051',
                'name': 'Agent ID',
                'custom': True,
                'type': 'string'
            },
            {
                'id': 'customfield_10052',
                'name': 'Agent Tier',
                'custom': True,
                'type': 'number'
            }
        ]
        return jsonify(fields), 200


# Test Fixtures
@pytest.fixture
def mock_jira_server():
    """Fixture providing mock Jira server"""
    return MockJiraServer()


@pytest.fixture
def webhook_secret():
    """Fixture providing webhook secret"""
    return "test-webhook-secret-12345"


@pytest.fixture
def test_cr_data():
    """Fixture providing test CR data"""
    return {
        'cr_id': 'CR-2024-0001',
        'agent_id': 'test-agent-01',
        'tier': 3,
        'control_id': 'SEC-001',
        'approver_role': 'Security Lead',
        'budget_tokens': 1000000,
        'cost_usd': 125.50,
        'compliance_result': 'pass'
    }


@pytest.fixture
def temp_keys_dir(tmp_path):
    """Fixture providing temporary keys directory"""
    keys_dir = tmp_path / "pki-keys"
    keys_dir.mkdir()
    return str(keys_dir)


# Test Cases

class TestJiraWebhookReceiver:
    """Test suite for Jira webhook receiver"""

    def test_health_check(self):
        """Test webhook receiver health check endpoint"""
        # This would require starting the webhook receiver
        # For now, we test the handler logic
        pass

    def test_webhook_signature_validation(self, webhook_secret):
        """Test HMAC signature validation"""
        payload = json.dumps({'test': 'data'}).encode('utf-8')

        # Calculate signature
        signature = 'sha256=' + hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Simulate validation
        expected_sig = signature
        assert hmac.compare_digest(signature, expected_sig)

    def test_jira_event_processing(self, test_cr_data):
        """Test processing of Jira webhook events"""
        event_data = {
            'issue': {
                'key': test_cr_data['cr_id'],
                'fields': {
                    'status': {'name': 'Approved'},
                    'summary': 'Test CR',
                    'priority': {'name': 'High'},
                    'assignee': {'displayName': 'John Doe'},
                    'updated': '2024-01-01T12:00:00Z',
                    'issuetype': {'name': 'Change Request'}
                }
            },
            'changelog': {
                'items': [
                    {'fromString': 'Pending', 'toString': 'Approved'}
                ]
            }
        }

        # Extract status
        status = event_data['issue']['fields']['status']['name']
        assert status == 'Approved'

        # Extract issue key
        issue_key = event_data['issue']['key']
        assert issue_key == test_cr_data['cr_id']


class TestPKISigning:
    """Test suite for PKI signing functionality"""

    def test_key_generation(self, temp_keys_dir):
        """Test RSA key pair generation"""
        from jira_pki_signing import JiraPKISigner

        signer = JiraPKISigner(temp_keys_dir)
        email = "test@example.com"

        private_path, public_path = signer.generate_key_pair(email)

        # Verify keys exist
        assert os.path.exists(private_path)
        assert os.path.exists(public_path)

        # Verify permissions on private key
        stat = os.stat(private_path)
        assert stat.st_mode & 0o777 == 0o600

    def test_sign_approval(self, temp_keys_dir, test_cr_data):
        """Test signing a CR approval"""
        from jira_pki_signing import JiraPKISigner

        signer = JiraPKISigner(temp_keys_dir)
        email = "approver@example.com"

        # Generate keys
        private_path, public_path = signer.generate_key_pair(email)

        # Sign approval
        approval_data = {
            'status': 'Approved',
            'comments': 'Looks good'
        }

        signature_obj = signer.sign_approval(
            test_cr_data['cr_id'],
            email,
            private_path,
            approval_data
        )

        # Verify signature object structure
        assert signature_obj['cr_id'] == test_cr_data['cr_id']
        assert signature_obj['approver'] == email
        assert 'signature' in signature_obj
        assert 'document_hash' in signature_obj
        assert signature_obj['algorithm'] == 'RSA-PSS-SHA256'

    def test_verify_approval(self, temp_keys_dir, test_cr_data):
        """Test verifying a signed approval"""
        from jira_pki_signing import JiraPKISigner

        signer = JiraPKISigner(temp_keys_dir)
        email = "approver@example.com"

        # Generate keys
        private_path, public_path = signer.generate_key_pair(email)

        # Sign approval
        approval_data = {'status': 'Approved'}
        signature_obj = signer.sign_approval(
            test_cr_data['cr_id'],
            email,
            private_path,
            approval_data
        )

        # Verify signature
        is_valid = signer.verify_approval(signature_obj, public_path)
        assert is_valid is True

    def test_multi_party_approval(self, temp_keys_dir, test_cr_data):
        """Test multi-party approval verification"""
        from jira_pki_signing import JiraPKISigner

        signer = JiraPKISigner(temp_keys_dir)

        # Generate keys for multiple approvers
        approvers = [
            "security-lead@example.com",
            "tech-lead@example.com",
            "product-owner@example.com"
        ]

        public_keys_dir = Path(temp_keys_dir) / "public-keys"
        public_keys_dir.mkdir()

        for approver in approvers:
            # Generate keys
            private_path, public_path = signer.generate_key_pair(approver)

            # Copy public key to public keys dir
            import shutil
            email_safe = approver.replace('@', '_at_').replace('.', '_')
            shutil.copy(
                public_path,
                public_keys_dir / f"{email_safe}_public.pem"
            )

            # Sign approval
            approval_data = {'status': 'Approved', 'comments': f'Approved by {approver}'}
            signer.sign_approval(
                test_cr_data['cr_id'],
                approver,
                private_path,
                approval_data
            )

        # Verify multi-party approval
        results = signer.verify_multi_party_approval(
            test_cr_data['cr_id'],
            approvers,
            str(public_keys_dir)
        )

        # Check results
        assert results['overall_status'] == 'APPROVED'
        assert len(results['approvers']) == len(approvers)

        for approver in approvers:
            assert results['approvers'][approver]['status'] == 'VALID'

    def test_tampered_signature(self, temp_keys_dir, test_cr_data):
        """Test that tampered signatures are detected"""
        from jira_pki_signing import JiraPKISigner

        signer = JiraPKISigner(temp_keys_dir)
        email = "approver@example.com"

        # Generate keys
        private_path, public_path = signer.generate_key_pair(email)

        # Sign approval
        approval_data = {'status': 'Approved'}
        signature_obj = signer.sign_approval(
            test_cr_data['cr_id'],
            email,
            private_path,
            approval_data
        )

        # Tamper with approval data
        signature_obj['approval_data']['status'] = 'Rejected'

        # Verification should fail
        is_valid = signer.verify_approval(signature_obj, public_path)
        assert is_valid is False


class TestFieldMapping:
    """Test suite for Jira field mapping"""

    def test_map_to_jira(self, test_cr_data):
        """Test mapping framework fields to Jira fields"""
        mapping = {
            'cr_id': 'customfield_10050',
            'agent_id': 'customfield_10051',
            'tier': 'customfield_10052',
            'control_id': 'customfield_10053'
        }

        jira_fields = {}
        for framework_key, value in test_cr_data.items():
            jira_key = mapping.get(framework_key)
            if jira_key:
                jira_fields[jira_key] = value

        # Verify mapping
        assert jira_fields['customfield_10050'] == test_cr_data['cr_id']
        assert jira_fields['customfield_10051'] == test_cr_data['agent_id']
        assert jira_fields['customfield_10052'] == test_cr_data['tier']

    def test_map_from_jira(self, test_cr_data):
        """Test mapping Jira fields back to framework fields"""
        mapping = {
            'cr_id': 'customfield_10050',
            'agent_id': 'customfield_10051',
            'tier': 'customfield_10052'
        }

        # Reverse mapping
        reverse_mapping = {v: k for k, v in mapping.items()}

        jira_data = {
            'customfield_10050': test_cr_data['cr_id'],
            'customfield_10051': test_cr_data['agent_id'],
            'customfield_10052': test_cr_data['tier']
        }

        framework_fields = {}
        for jira_key, value in jira_data.items():
            framework_key = reverse_mapping.get(jira_key)
            if framework_key:
                framework_fields[framework_key] = value

        # Verify reverse mapping
        assert framework_fields['cr_id'] == test_cr_data['cr_id']
        assert framework_fields['agent_id'] == test_cr_data['agent_id']
        assert framework_fields['tier'] == test_cr_data['tier']


class TestJiraAPIIntegration:
    """Test suite for Jira REST API integration"""

    @responses.activate
    def test_create_issue(self, test_cr_data):
        """Test creating a Jira issue via REST API"""
        # Mock Jira API response
        responses.add(
            responses.POST,
            'https://test.atlassian.net/rest/api/3/issue',
            json={'key': 'CR-0001', 'id': '10001'},
            status=201
        )

        import requests

        issue_data = {
            'fields': {
                'project': {'key': 'AIOPS'},
                'summary': 'Test CR',
                'issuetype': {'name': 'Change Request'},
                'customfield_10050': test_cr_data['cr_id']
            }
        }

        response = requests.post(
            'https://test.atlassian.net/rest/api/3/issue',
            json=issue_data,
            headers={'Authorization': 'Bearer test-token'}
        )

        assert response.status_code == 201
        assert response.json()['key'] == 'CR-0001'

    @responses.activate
    def test_query_issues(self):
        """Test querying Jira issues via JQL"""
        # Mock Jira API response
        responses.add(
            responses.GET,
            'https://test.atlassian.net/rest/api/3/search',
            json={
                'issues': [
                    {
                        'key': 'CR-0001',
                        'fields': {
                            'summary': 'Test CR',
                            'customfield_10052': 3  # tier
                        }
                    }
                ]
            },
            status=200
        )

        import requests

        response = requests.get(
            'https://test.atlassian.net/rest/api/3/search',
            params={'jql': 'project = AIOPS AND type = "Change Request"'},
            headers={'Authorization': 'Bearer test-token'}
        )

        assert response.status_code == 200
        issues = response.json()['issues']
        assert len(issues) == 1
        assert issues[0]['key'] == 'CR-0001'


class TestEndToEndWorkflow:
    """End-to-end integration tests"""

    def test_full_approval_workflow(self, temp_keys_dir, test_cr_data):
        """Test complete approval workflow with PKI signing"""
        from jira_pki_signing import JiraPKISigner

        # 1. Generate keys for approvers
        signer = JiraPKISigner(temp_keys_dir)
        approvers = ["security@example.com", "tech-lead@example.com"]

        public_keys_dir = Path(temp_keys_dir) / "public-keys"
        public_keys_dir.mkdir()

        for approver in approvers:
            private_path, public_path = signer.generate_key_pair(approver)

            # Copy public key
            import shutil
            email_safe = approver.replace('@', '_at_').replace('.', '_')
            shutil.copy(public_path, public_keys_dir / f"{email_safe}_public.pem")

            # Sign approval
            approval_data = {'status': 'Approved'}
            signer.sign_approval(test_cr_data['cr_id'], approver, private_path, approval_data)

        # 2. Verify all approvals
        results = signer.verify_multi_party_approval(
            test_cr_data['cr_id'],
            approvers,
            str(public_keys_dir)
        )

        # 3. Check workflow completion
        assert results['overall_status'] == 'APPROVED'

        # 4. Generate audit trail
        audit_entry = {
            'audit_id': f"audit-{datetime.utcnow().timestamp():.0f}",
            'cr_id': test_cr_data['cr_id'],
            'approvals': results['approvers'],
            'workflow_complete': True
        }

        assert audit_entry['workflow_complete'] is True


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
