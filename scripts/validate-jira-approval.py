#!/usr/bin/env python3
"""
Jira Approval Validation Script (Python)
AI Agent Governance Framework v2.0
Control: APP-001 (Human Primacy), G-02 (Approval Enforcement), G-07 (Jira Integration)

Purpose: Validate that a Jira Change Request (CR) is approved with proper role enforcement
Usage: python3 validate-jira-approval.py <AGENT_ID> <CR_ID> [REQUIRED_APPROVER_ROLE]

Environment Variables Required:
  JIRA_URL        - Base URL for Jira instance (e.g., https://your-company.atlassian.net)
  JIRA_USER       - Jira username or email
  JIRA_TOKEN      - Jira API token

Exit Codes:
  0 - CR is approved and meets requirements
  1 - CR is not approved or validation failed
  2 - Missing required environment variables or parameters
"""

import os
import sys
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, Optional, List
from uuid import uuid4

# ANSI color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class JiraApprovalValidator:
    """Validates Jira CR approval status with role enforcement"""

    def __init__(self, jira_url: str, jira_user: str, jira_token: str):
        self.jira_url = jira_url.rstrip('/')
        self.auth = (jira_user, jira_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def fetch_cr(self, cr_id: str) -> Dict:
        """Fetch CR details from Jira API"""
        url = f"{self.jira_url}/rest/api/3/issue/{cr_id}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Jira CR {cr_id} not found")
            elif e.response.status_code == 401:
                raise ValueError("Jira authentication failed - check JIRA_USER and JIRA_TOKEN")
            elif e.response.status_code == 403:
                raise ValueError(f"Access denied to CR {cr_id} - check permissions")
            else:
                raise ValueError(f"Jira API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to Jira: {str(e)}")

    def get_status(self, cr_data: Dict) -> str:
        """Extract status from CR data"""
        return cr_data.get('fields', {}).get('status', {}).get('name', 'Unknown')

    def get_approvers(self, cr_data: Dict) -> List[Dict]:
        """
        Extract approver information from CR data

        Note: Adjust the custom field ID based on your Jira configuration
        Common custom field IDs for approvers:
        - customfield_10100
        - customfield_10200
        - Use Jira API to list fields: GET /rest/api/3/field
        """
        approvers = []

        # Try multiple common approver field patterns
        approver_fields = [
            'customfield_10100',  # Common approval field
            'customfield_10200',
            'approvers',          # Some Jira instances use this
            'approval'
        ]

        fields = cr_data.get('fields', {})

        for field_id in approver_fields:
            field_value = fields.get(field_id)
            if field_value and field_value != []:
                # Handle different approver data structures
                if isinstance(field_value, list):
                    approvers.extend(field_value)
                elif isinstance(field_value, dict):
                    approvers.append(field_value)

        return approvers

    def validate_approver_role(self, approvers: List[Dict], required_role: str) -> bool:
        """Validate that required approver role is present"""
        if not approvers:
            return False

        for approver in approvers:
            # Handle different approver data structures
            approver_role = (
                approver.get('role') or
                approver.get('displayName') or
                approver.get('name') or
                str(approver)
            )

            if required_role.lower() in approver_role.lower():
                return True

        return False

    def get_budget_tokens(self, cr_data: Dict) -> Optional[int]:
        """Extract budget token allocation from CR"""
        # Try to find budget in description or custom field
        description = cr_data.get('fields', {}).get('description', '')

        # Look for patterns like "Budget: 1000 tokens" or "Tokens: 1000"
        if isinstance(description, dict):
            # Jira API v3 uses Atlassian Document Format
            description = self._extract_text_from_adf(description)

        import re
        budget_match = re.search(r'(?:budget|tokens):\s*(\d+)', description, re.IGNORECASE)
        if budget_match:
            return int(budget_match.group(1))

        # Try custom field (adjust field ID as needed)
        budget_field = cr_data.get('fields', {}).get('customfield_10101')
        if budget_field and isinstance(budget_field, (int, str)):
            try:
                return int(budget_field)
            except ValueError:
                pass

        return None

    def _extract_text_from_adf(self, adf: Dict) -> str:
        """Extract plain text from Atlassian Document Format"""
        text_parts = []

        def extract(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    text_parts.append(node.get('text', ''))
                if 'content' in node:
                    for child in node['content']:
                        extract(child)
            elif isinstance(node, list):
                for item in node:
                    extract(item)

        extract(adf)
        return ' '.join(text_parts)

    def generate_audit_trail(self, agent_id: str, cr_id: str, cr_data: Dict,
                           validation_result: str, required_role: str) -> Dict:
        """Generate audit trail entry conforming to audit-trail.json schema"""
        audit_id = f"audit-{int(datetime.utcnow().timestamp())}-{str(uuid4())[:8]}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        status = self.get_status(cr_data)
        approvers = self.get_approvers(cr_data)
        budget_tokens = self.get_budget_tokens(cr_data)

        # Generate evidence hash from CR data
        evidence_string = json.dumps(cr_data, sort_keys=True)
        evidence_hash = f"sha256:{hashlib.sha256(evidence_string.encode()).hexdigest()}"

        audit_entry = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "actor": "ci-cd-pipeline",
            "action": "jira_approval_validation",
            "workflow_step": "APP-001",
            "jira_reference": {
                "cr_id": cr_id,
                "approver_role": required_role,
                "budget_tokens": budget_tokens or 0,
                "controls": ["APP-001", "G-02", "G-07"],
                "status": status,
                "validated_at": timestamp
            },
            "inputs": {
                "agent_id": agent_id,
                "cr_id": cr_id,
                "required_approver_role": required_role,
                "jira_url": self.jira_url
            },
            "outputs": {
                "validation_result": validation_result,
                "cr_status": status,
                "approval_verified": validation_result == "pass",
                "approvers_found": len(approvers)
            },
            "policy_controls_checked": ["APP-001", "G-02", "G-07"],
            "compliance_result": validation_result,
            "evidence_hash": evidence_hash,
            "auditor_agent": "jira-approval-validator-py"
        }

        return audit_entry


def print_header(agent_id: str, cr_id: str, required_role: str):
    """Print validation header"""
    print("=" * 50)
    print("Jira Approval Validation (APP-001)")
    print("=" * 50)
    print(f"Agent ID:              {agent_id}")
    print(f"Change Request:        {cr_id}")
    print(f"Required Approver:     {required_role}")
    print("=" * 50)
    print()


def validate_environment() -> tuple:
    """Validate required environment variables"""
    jira_url = os.getenv('JIRA_URL')
    jira_user = os.getenv('JIRA_USER')
    jira_token = os.getenv('JIRA_TOKEN')

    missing = []
    if not jira_url:
        missing.append('JIRA_URL')
    if not jira_user:
        missing.append('JIRA_USER')
    if not jira_token:
        missing.append('JIRA_TOKEN')

    if missing:
        print(f"{Colors.RED}❌ ERROR: Missing required environment variables{Colors.NC}")
        print("Required environment variables:")
        for var in missing:
            print(f"  - {var}")
        sys.exit(2)

    return jira_url, jira_user, jira_token


def save_audit_trail(audit_entry: Dict) -> str:
    """Save audit trail to file and return path"""
    audit_id = audit_entry['audit_id']
    audit_path = f"/tmp/{audit_id}.json"

    with open(audit_path, 'w') as f:
        json.dump(audit_entry, f, indent=2)

    # Also save audit ID for CI/CD pipeline
    with open('/tmp/jira-approval-audit-id.txt', 'w') as f:
        f.write(audit_id)

    return audit_path


def main():
    """Main validation logic"""
    # Parse arguments
    if len(sys.argv) < 3:
        print(f"{Colors.RED}❌ ERROR: Missing required arguments{Colors.NC}")
        print(f"Usage: {sys.argv[0]} <AGENT_ID> <CR_ID> [REQUIRED_APPROVER_ROLE]")
        print()
        print("Example:")
        print(f"  {sys.argv[0]} security-agent CR-2025-1042 'Change Manager'")
        sys.exit(2)

    agent_id = sys.argv[1]
    cr_id = sys.argv[2]
    required_role = sys.argv[3] if len(sys.argv) > 3 else "Change Manager"

    # Validate environment
    jira_url, jira_user, jira_token = validate_environment()

    # Print header
    print_header(agent_id, cr_id, required_role)

    # Initialize validator
    validator = JiraApprovalValidator(jira_url, jira_user, jira_token)

    # Fetch CR
    print("🔍 Fetching Jira CR details...")
    try:
        cr_data = validator.fetch_cr(cr_id)
    except ValueError as e:
        print(f"{Colors.RED}❌ FAILED: {str(e)}{Colors.NC}")
        sys.exit(1)

    print(f"{Colors.GREEN}✅ CR fetched successfully{Colors.NC}")

    # Validate status
    status = validator.get_status(cr_data)
    print(f"\n📋 CR Status: {status}")

    if status != "Approved":
        print(f"{Colors.RED}❌ FAILED: CR status is '{status}', not 'Approved'{Colors.NC}")
        print()
        print("GOVERNANCE VIOLATION:")
        print("  Control:     APP-001 (Human Primacy)")
        print("  Requirement: All Tier 3/4 deployments require approved Jira CR")
        print(f"  Current:     CR {cr_id} has status '{status}'")
        print("  Action:      Update CR to 'Approved' status before deployment")

        # Generate audit trail for failure
        audit_entry = validator.generate_audit_trail(
            agent_id, cr_id, cr_data, "fail", required_role
        )
        audit_path = save_audit_trail(audit_entry)
        print(f"\n📄 Audit Trail: {audit_path}")

        sys.exit(1)

    print(f"{Colors.GREEN}✅ CR Status Verified: Approved{Colors.NC}")

    # Validate approvers
    approvers = validator.get_approvers(cr_data)

    if not approvers or approvers == []:
        print(f"{Colors.YELLOW}⚠️  WARNING: No approver information found in CR{Colors.NC}")
        print("Note: This may indicate missing custom field mapping.")
        print("Proceeding based on status check only.")
    else:
        print(f"\n👥 Approvers found: {len(approvers)}")

        # Validate required role
        if validator.validate_approver_role(approvers, required_role):
            print(f"{Colors.GREEN}✅ Required approver role verified: {required_role}{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ FAILED: Required approver role '{required_role}' not found{Colors.NC}")
            print()
            print("GOVERNANCE VIOLATION:")
            print("  Control:     APP-001 (Human Primacy)")
            print(f"  Requirement: CR must be approved by {required_role}")
            print(f"  Current:     Approver role not found in CR {cr_id}")

            # Generate audit trail for failure
            audit_entry = validator.generate_audit_trail(
                agent_id, cr_id, cr_data, "fail", required_role
            )
            audit_path = save_audit_trail(audit_entry)
            print(f"\n📄 Audit Trail: {audit_path}")

            sys.exit(1)

    # Check budget allocation
    budget_tokens = validator.get_budget_tokens(cr_data)
    if budget_tokens:
        print(f"\n💰 Budget Tokens Allocated: {budget_tokens:,}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  WARNING: No budget token allocation found in CR{Colors.NC}")

    # Generate audit trail for success
    audit_entry = validator.generate_audit_trail(
        agent_id, cr_id, cr_data, "pass", required_role
    )
    audit_path = save_audit_trail(audit_entry)

    # Success output
    print(f"\n{Colors.GREEN}✅ VALIDATION PASSED{Colors.NC}")
    print("=" * 50)
    print(f"Jira CR {cr_id} is approved for deployment")
    print(f"Agent: {agent_id}")
    print(f"Audit ID: {audit_entry['audit_id']}")
    print(f"Audit Trail: {audit_path}")
    print("=" * 50)

    sys.exit(0)


if __name__ == "__main__":
    main()
