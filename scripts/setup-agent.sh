#!/bin/bash
# Agent Setup Script

set -e

TIER=""
AGENT_NAME=""

usage() {
    echo "Usage: $0 --tier <1|2|3|4> --name <agent-name>"
    echo "Example: $0 --tier 2 --name code-reviewer"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --tier) TIER="$2"; shift 2 ;;
        --name) AGENT_NAME="$2"; shift 2 ;;
        *) usage ;;
    esac
done

[[ -z "$TIER" || -z "$AGENT_NAME" ]] && usage

echo "Setting up agent: $AGENT_NAME (Tier $TIER)"

mkdir -p "agents/$AGENT_NAME"
cp templates/agent-deployment/config-template.yml "agents/$AGENT_NAME/config.yml"

sed -i.bak "s/name: \"\"/name: \"$AGENT_NAME\"/g" "agents/$AGENT_NAME/config.yml"
sed -i.bak "s/tier: 0/tier: $TIER/g" "agents/$AGENT_NAME/config.yml"
rm "agents/$AGENT_NAME/config.yml.bak"

echo "✅ Agent configuration created at: agents/$AGENT_NAME/config.yml"
echo "Next steps:"
echo "  1. Edit agents/$AGENT_NAME/config.yml"
echo "  2. Fill out templates/agent-deployment/deployment-request.md"
echo "  3. Get approvals"
echo "  4. Start using the agent!"
