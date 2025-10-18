#!/bin/bash
# Jira Approval Validation Script
# AI Agent Governance Framework v2.0
# Control: APP-001 (Human Primacy), G-02 (Approval Enforcement)
#
# Purpose: Validate that a Jira Change Request (CR) is approved before deployment
# Usage: ./validate-jira-approval.sh <AGENT_ID> <CR_ID> [REQUIRED_APPROVER_ROLE]
#
# Environment Variables Required:
#   JIRA_URL        - Base URL for Jira instance (e.g., https://your-company.atlassian.net)
#   JIRA_USER       - Jira username or email
#   JIRA_TOKEN      - Jira API token
#
# Exit Codes:
#   0 - CR is approved and meets requirements
#   1 - CR is not approved or validation failed
#   2 - Missing required environment variables or parameters

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
AGENT_ID="${1:-}"
CR_ID="${2:-}"
REQUIRED_APPROVER_ROLE="${3:-Change Manager}"

# Validate inputs
if [ -z "$AGENT_ID" ] || [ -z "$CR_ID" ]; then
    echo -e "${RED}❌ ERROR: Missing required arguments${NC}"
    echo "Usage: $0 <AGENT_ID> <CR_ID> [REQUIRED_APPROVER_ROLE]"
    echo ""
    echo "Example:"
    echo "  $0 security-agent CR-2025-1042 'Change Manager'"
    exit 2
fi

# Validate environment variables
if [ -z "$JIRA_URL" ] || [ -z "$JIRA_USER" ] || [ -z "$JIRA_TOKEN" ]; then
    echo -e "${RED}❌ ERROR: Missing required environment variables${NC}"
    echo "Required environment variables:"
    echo "  JIRA_URL        - Base URL for Jira instance"
    echo "  JIRA_USER       - Jira username or email"
    echo "  JIRA_TOKEN      - Jira API token"
    exit 2
fi

echo "=========================================="
echo "Jira Approval Validation (APP-001)"
echo "=========================================="
echo "Agent ID:              $AGENT_ID"
echo "Change Request:        $CR_ID"
echo "Required Approver:     $REQUIRED_APPROVER_ROLE"
echo "Jira URL:              $JIRA_URL"
echo "=========================================="
echo ""

# Fetch Jira issue details
echo "🔍 Fetching Jira CR details..."
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${JIRA_USER}:${JIRA_TOKEN}" \
    -H "Accept: application/json" \
    "${JIRA_URL}/rest/api/3/issue/${CR_ID}")

# Split response into body and status code
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

# Check HTTP response
if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}❌ FAILED: Jira API request failed with HTTP $HTTP_CODE${NC}"
    echo "Response: $BODY"
    exit 1
fi

# Parse CR status
STATUS=$(echo "$BODY" | jq -r '.fields.status.name // "Unknown"')
echo "📋 CR Status: $STATUS"

# Validate status is "Approved"
if [ "$STATUS" != "Approved" ]; then
    echo -e "${RED}❌ FAILED: CR status is '$STATUS', not 'Approved'${NC}"
    echo ""
    echo "GOVERNANCE VIOLATION:"
    echo "  Control:     APP-001 (Human Primacy)"
    echo "  Requirement: All Tier 3/4 deployments require approved Jira CR"
    echo "  Current:     CR $CR_ID has status '$STATUS'"
    echo "  Action:      Update CR to 'Approved' status before deployment"
    exit 1
fi

echo -e "${GREEN}✅ CR Status Verified: Approved${NC}"

# Parse approver information
# Note: This assumes a custom field 'customfield_10100' for approvers
# Adjust the field ID based on your Jira configuration
APPROVERS=$(echo "$BODY" | jq -r '.fields.customfield_10100 // []')

# Check if approvers field exists
if [ "$APPROVERS" == "[]" ] || [ "$APPROVERS" == "null" ]; then
    echo -e "${YELLOW}⚠️  WARNING: No approver information found in CR${NC}"
    echo "Note: This may indicate missing custom field mapping."
    echo "Proceeding based on status check only."
else
    echo "👥 Approvers found in CR"

    # Validate required approver role is present
    # This is a simplified check - adjust based on your Jira approver field structure
    if echo "$APPROVERS" | grep -qi "$REQUIRED_APPROVER_ROLE"; then
        echo -e "${GREEN}✅ Required approver role verified: $REQUIRED_APPROVER_ROLE${NC}"
    else
        echo -e "${RED}❌ FAILED: Required approver role '$REQUIRED_APPROVER_ROLE' not found${NC}"
        echo ""
        echo "GOVERNANCE VIOLATION:"
        echo "  Control:     APP-001 (Human Primacy)"
        echo "  Requirement: CR must be approved by $REQUIRED_APPROVER_ROLE"
        echo "  Current:     Approver role not found in CR $CR_ID"
        exit 1
    fi
fi

# Parse and validate agent reference in CR
AGENT_REFERENCE=$(echo "$BODY" | jq -r '.fields.summary // ""' | grep -o "$AGENT_ID" || echo "")
if [ -n "$AGENT_REFERENCE" ]; then
    echo -e "${GREEN}✅ Agent reference verified in CR summary${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: Agent ID '$AGENT_ID' not found in CR summary${NC}"
    echo "CR Summary: $(echo "$BODY" | jq -r '.fields.summary // ""')"
fi

# Check CR description for tier information
CR_DESCRIPTION=$(echo "$BODY" | jq -r '.fields.description.content[0].content[0].text // "" | .fields.description // ""' 2>/dev/null || echo "")
echo ""
echo "📝 CR Description Preview:"
echo "$CR_DESCRIPTION" | head -n 3

# Generate audit trail entry
AUDIT_ID="audit-$(date +%s)-$(uuidgen | cut -d'-' -f1)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "/tmp/${AUDIT_ID}.json" <<EOF
{
  "audit_id": "$AUDIT_ID",
  "timestamp": "$TIMESTAMP",
  "actor": "ci-cd-pipeline",
  "action": "jira_approval_validation",
  "workflow_step": "APP-001",
  "jira_reference": {
    "cr_id": "$CR_ID",
    "approver_role": "$REQUIRED_APPROVER_ROLE",
    "status": "$STATUS",
    "validated_at": "$TIMESTAMP"
  },
  "inputs": {
    "agent_id": "$AGENT_ID",
    "cr_id": "$CR_ID",
    "required_approver_role": "$REQUIRED_APPROVER_ROLE"
  },
  "outputs": {
    "validation_result": "pass",
    "cr_status": "$STATUS",
    "approval_verified": true
  },
  "policy_controls_checked": ["APP-001", "G-02"],
  "compliance_result": "pass",
  "evidence_hash": "$(echo "$BODY" | sha256sum | cut -d' ' -f1)",
  "auditor_agent": "jira-approval-validator"
}
EOF

echo ""
echo -e "${GREEN}✅ VALIDATION PASSED${NC}"
echo "=========================================="
echo "Jira CR $CR_ID is approved for deployment"
echo "Agent: $AGENT_ID"
echo "Audit ID: $AUDIT_ID"
echo "Audit Trail: /tmp/${AUDIT_ID}.json"
echo "=========================================="

# Output audit ID for CI/CD pipeline to capture
echo "$AUDIT_ID" > /tmp/jira-approval-audit-id.txt

exit 0
