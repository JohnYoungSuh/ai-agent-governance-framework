#!/bin/bash
# Setup Jira Webhook Integration (G-07)
# AI Agent Governance Framework v2.0
# Control: G-07 (Jira Webhook Integration for CR Status Monitoring)
#
# Purpose: Configure Jira webhook to monitor CR status changes and trigger CI/CD
# Usage: ./setup-jira-webhook.sh --jira-url <url> --webhook-url <url>
#
# Features:
#   - Creates Jira webhook for issue updates
#   - Filters for Change Request (CR) status changes
#   - Triggers GitHub Actions workflow on CR approval
#   - Validates webhook configuration

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
JIRA_URL=""
WEBHOOK_URL=""
WEBHOOK_NAME="AI Agent CR Status Monitor"
ISSUE_TYPES="Change Request,Quality Gate"

usage() {
    cat <<EOF
Usage: $0 --jira-url <url> --webhook-url <url> [OPTIONS]

REQUIRED:
  --jira-url <url>          Jira instance URL (e.g., https://company.atlassian.net)
  --webhook-url <url>       Webhook target URL (GitHub Actions workflow URL)

OPTIONS:
  --webhook-name <name>     Webhook name (default: "$WEBHOOK_NAME")
  --issue-types <types>     Comma-separated issue types to monitor (default: "$ISSUE_TYPES")
  --test                    Test webhook configuration only (no creation)

EXAMPLES:
  $0 --jira-url https://company.atlassian.net \\
     --webhook-url https://api.github.com/repos/user/repo/dispatches

ENVIRONMENT VARIABLES:
  JIRA_USER                 Jira username or email
  JIRA_TOKEN                Jira API token (create at: https://id.atlassian.com/manage/api-tokens)
  GITHUB_TOKEN              GitHub personal access token (for webhook target)

EOF
    exit 1
}

# Parse arguments
TEST_MODE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --jira-url)
            JIRA_URL="$2"
            shift 2
            ;;
        --webhook-url)
            WEBHOOK_URL="$2"
            shift 2
            ;;
        --webhook-name)
            WEBHOOK_NAME="$2"
            shift 2
            ;;
        --issue-types)
            ISSUE_TYPES="$2"
            shift 2
            ;;
        --test)
            TEST_MODE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Validate required arguments
if [ -z "$JIRA_URL" ] || [ -z "$WEBHOOK_URL" ]; then
    echo -e "${RED}ERROR: --jira-url and --webhook-url are required${NC}"
    usage
fi

# Validate environment variables
JIRA_USER=${JIRA_USER:-}
JIRA_TOKEN=${JIRA_TOKEN:-}

if [ -z "$JIRA_USER" ] || [ -z "$JIRA_TOKEN" ]; then
    echo -e "${RED}ERROR: JIRA_USER and JIRA_TOKEN environment variables are required${NC}"
    echo "Set them with:"
    echo "  export JIRA_USER='your-email@company.com'"
    echo "  export JIRA_TOKEN='your-api-token'"
    echo ""
    echo "Create API token at: https://id.atlassian.com/manage/api-tokens"
    exit 1
fi

# Strip trailing slash from Jira URL
JIRA_URL=${JIRA_URL%/}

echo "=========================================="
echo "Jira Webhook Setup (G-07)"
echo "=========================================="
echo "Jira URL:        $JIRA_URL"
echo "Webhook URL:     $WEBHOOK_URL"
echo "Webhook Name:    $WEBHOOK_NAME"
echo "Issue Types:     $ISSUE_TYPES"
echo "Test Mode:       $TEST_MODE"
echo "=========================================="
echo ""

# Check for required tools
command -v curl >/dev/null 2>&1 || { echo -e "${RED}ERROR: curl is required${NC}"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo -e "${RED}ERROR: jq is required${NC}"; exit 1; }

# Function to test Jira connection
test_jira_connection() {
    echo "🔍 Testing Jira connection..."

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -u "$JIRA_USER:$JIRA_TOKEN" \
        "$JIRA_URL/rest/api/3/myself")

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Jira connection successful${NC}"
        return 0
    elif [ "$HTTP_CODE" = "401" ]; then
        echo -e "${RED}❌ Jira authentication failed (401 Unauthorized)${NC}"
        echo "Check your JIRA_USER and JIRA_TOKEN"
        return 1
    else
        echo -e "${RED}❌ Jira connection failed (HTTP $HTTP_CODE)${NC}"
        return 1
    fi
}

# Function to list existing webhooks
list_webhooks() {
    echo "🔍 Listing existing webhooks..."

    WEBHOOKS=$(curl -s -X GET \
        -u "$JIRA_USER:$JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        "$JIRA_URL/rest/webhooks/1.0/webhook" | jq -r '.[] | "\(.name) - \(.url) - Enabled: \(.enabled)"')

    if [ -n "$WEBHOOKS" ]; then
        echo "$WEBHOOKS"
    else
        echo "No webhooks found"
    fi
}

# Function to create webhook
create_webhook() {
    echo "🔧 Creating Jira webhook..."

    # Build JQL filter for issue types
    IFS=',' read -ra TYPES <<< "$ISSUE_TYPES"
    JQL_FILTER="issueType IN ("
    for i in "${!TYPES[@]}"; do
        if [ $i -gt 0 ]; then
            JQL_FILTER+=","
        fi
        JQL_FILTER+="'${TYPES[$i]}'"
    done
    JQL_FILTER+=")"

    # Webhook payload
    WEBHOOK_PAYLOAD=$(cat <<EOF
{
  "name": "$WEBHOOK_NAME",
  "url": "$WEBHOOK_URL",
  "events": [
    "jira:issue_updated"
  ],
  "filters": {
    "issue-related-events-section": "$JQL_FILTER"
  },
  "excludeBody": false
}
EOF
)

    echo "Webhook configuration:"
    echo "$WEBHOOK_PAYLOAD" | jq '.'

    if [ "$TEST_MODE" = true ]; then
        echo -e "${YELLOW}⚠️  Test mode - webhook not created${NC}"
        return 0
    fi

    # Create webhook
    RESPONSE=$(curl -s -X POST \
        -u "$JIRA_USER:$JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$WEBHOOK_PAYLOAD" \
        "$JIRA_URL/rest/webhooks/1.0/webhook")

    # Check response
    WEBHOOK_ID=$(echo "$RESPONSE" | jq -r '.self // empty')

    if [ -n "$WEBHOOK_ID" ]; then
        echo -e "${GREEN}✅ Webhook created successfully${NC}"
        echo "Webhook ID: $WEBHOOK_ID"
        echo ""
        echo "Webhook details:"
        echo "$RESPONSE" | jq '.'
        return 0
    else
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.errorMessages[0] // .message // "Unknown error"')
        echo -e "${RED}❌ Failed to create webhook${NC}"
        echo "Error: $ERROR_MSG"
        echo ""
        echo "Full response:"
        echo "$RESPONSE" | jq '.'
        return 1
    fi
}

# Function to test webhook
test_webhook() {
    echo "🧪 Testing webhook delivery..."

    # Note: Jira webhooks don't have a built-in test endpoint
    # This would require creating a test issue or manually triggering
    echo -e "${YELLOW}⚠️  Manual testing required:${NC}"
    echo "1. Create or update a Change Request in Jira"
    echo "2. Change its status to 'Approved'"
    echo "3. Check webhook target URL for incoming request"
    echo ""
    echo "Webhook should send payload like:"
    cat <<'EOF'
{
  "timestamp": "2025-10-18T12:34:56.789+0000",
  "webhookEvent": "jira:issue_updated",
  "issue": {
    "id": "10042",
    "key": "CR-2025-1042",
    "fields": {
      "status": {
        "name": "Approved"
      },
      "issuetype": {
        "name": "Change Request"
      }
    }
  },
  "changelog": {
    "items": [{
      "field": "status",
      "fromString": "Pending",
      "toString": "Approved"
    }]
  }
}
EOF
}

# Function to create GitHub Actions workflow trigger
create_github_workflow_trigger() {
    echo ""
    echo "📝 GitHub Actions Workflow Configuration"
    echo "=========================================="
    echo ""
    echo "Add this to your .github/workflows/jira-cr-approved.yml:"
    echo ""
    cat <<'EOF'
name: Jira CR Approved - Deploy Agent

on:
  repository_dispatch:
    types: [jira-cr-approved]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract CR details
        id: cr
        run: |
          echo "cr_id=${{ github.event.client_payload.cr_id }}" >> $GITHUB_OUTPUT
          echo "cr_status=${{ github.event.client_payload.status }}" >> $GITHUB_OUTPUT

      - name: Trigger deployment
        run: |
          gh workflow run deploy-security-agent.yml \
            -f environment=prod \
            -f jira_cr_id=${{ steps.cr.outputs.cr_id }}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
EOF
    echo ""
}

# Function to create webhook handler example
create_webhook_handler_example() {
    echo ""
    echo "📝 Webhook Handler Example (Node.js)"
    echo "=========================================="
    echo ""
    cat <<'EOF'
// webhook-handler.js
const express = require('express');
const { Octokit } = require('@octokit/rest');

const app = express();
app.use(express.json());

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

app.post('/jira-webhook', async (req, res) => {
  const { webhookEvent, issue, changelog } = req.body;

  // Check if this is a CR status change to "Approved"
  if (webhookEvent === 'jira:issue_updated') {
    const statusChange = changelog?.items?.find(
      item => item.field === 'status' && item.toString === 'Approved'
    );

    const isCR = issue?.fields?.issuetype?.name === 'Change Request';

    if (statusChange && isCR) {
      console.log(`CR ${issue.key} approved - triggering deployment`);

      // Trigger GitHub Actions workflow
      await octokit.repos.createDispatchEvent({
        owner: 'your-org',
        repo: 'your-repo',
        event_type: 'jira-cr-approved',
        client_payload: {
          cr_id: issue.key,
          status: 'Approved',
          timestamp: new Date().toISOString()
        }
      });

      res.status(200).json({ message: 'Deployment triggered' });
    } else {
      res.status(200).json({ message: 'No action required' });
    }
  } else {
    res.status(200).json({ message: 'Event ignored' });
  }
});

app.listen(3000, () => console.log('Webhook handler running on port 3000'));
EOF
    echo ""
}

# Main execution
main() {
    # Test Jira connection
    if ! test_jira_connection; then
        exit 1
    fi

    echo ""

    # List existing webhooks
    list_webhooks

    echo ""

    # Create webhook
    if ! create_webhook; then
        exit 1
    fi

    echo ""

    # Test webhook
    test_webhook

    # Show GitHub workflow configuration
    create_github_workflow_trigger

    # Show webhook handler example
    create_webhook_handler_example

    echo ""
    echo -e "${GREEN}✅ Jira webhook setup complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy webhook handler to receive Jira events"
    echo "2. Add GitHub Actions workflow to trigger on CR approval"
    echo "3. Test by updating a CR status to 'Approved' in Jira"
    echo "4. Monitor webhook deliveries in Jira: $JIRA_URL/plugins/servlet/webhooks"
}

# Run main
main
