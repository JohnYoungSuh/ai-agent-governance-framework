#!/bin/bash

# AI-Driven Governed Project Creation
# Enforces governance framework from project inception
# Usage: ./create-governed-project.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AI-Driven Governed Project Creation System               ║${NC}"
echo -e "${BLUE}║  Enforcing accountability & responsible AI from Day 1      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Validation functions
validate_required() {
    local value="$1"
    local field_name="$2"
    if [ -z "$value" ]; then
        echo -e "${RED}✗ ERROR: ${field_name} is required${NC}"
        exit 1
    fi
}

validate_agent_tier() {
    local tier="$1"
    if [[ ! "$tier" =~ ^[1-4]$ ]]; then
        echo -e "${RED}✗ ERROR: Agent tier must be 1-4${NC}"
        echo "  Tier 1: Observer (read-only)"
        echo "  Tier 2: Developer (dev env)"
        echo "  Tier 3: Operations (production)"
        echo "  Tier 4: Architect (design)"
        exit 1
    fi
}

validate_email() {
    local email="$1"
    if [[ ! "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        echo -e "${RED}✗ ERROR: Invalid email format${NC}"
        exit 1
    fi
}

generate_request_id() {
    local year=$(date +%Y)
    local random_num=$(printf "%04d" $((RANDOM % 10000)))
    echo "PCR-${year}-${random_num}"
}

# Collect required project metadata
echo -e "${GREEN}Step 1: Project Metadata (Required)${NC}"
echo "─────────────────────────────────────"

read -p "Project Name (lowercase-with-dashes): " PROJECT_NAME
validate_required "$PROJECT_NAME" "Project Name"

read -p "Project Description: " PROJECT_DESC
validate_required "$PROJECT_DESC" "Project Description"

read -p "Tech Stack (e.g., Python/FastAPI, Node/Express): " TECH_STACK
validate_required "$TECH_STACK" "Tech Stack"

read -p "Infrastructure (e.g., AWS Lambda, Kubernetes, Docker): " INFRASTRUCTURE
validate_required "$INFRASTRUCTURE" "Infrastructure"

echo ""
echo -e "${GREEN}Step 2: Governance & Accountability (Required)${NC}"
echo "─────────────────────────────────────"

read -p "Project Owner (name): " OWNER_NAME
validate_required "$OWNER_NAME" "Owner Name"

read -p "Project Owner Email: " OWNER_EMAIL
validate_required "$OWNER_EMAIL" "Owner Email"
validate_email "$OWNER_EMAIL"

read -p "AI Agent Tier (1-4): " AGENT_TIER
validate_required "$AGENT_TIER" "Agent Tier"
validate_agent_tier "$AGENT_TIER"

read -p "Compliance Requirements (e.g., SOC2, HIPAA, FedRAMP, None): " COMPLIANCE
validate_required "$COMPLIANCE" "Compliance Requirements"

read -p "Budget Limit ($/month, e.g., 100): " BUDGET_LIMIT
validate_required "$BUDGET_LIMIT" "Budget Limit"

echo ""
echo -e "${GREEN}Step 3: Business Alignment & Revenue Impact (Required)${NC}"
echo "─────────────────────────────────────"

echo "Strategic Goal:"
echo "1) Increase Revenue"
echo "2) Reduce Costs"
echo "3) Improve Customer Experience"
echo "4) Enter New Market"
echo "5) Product Innovation"
echo "6) Operational Excellence"
echo "7) Compliance & Risk Management"
echo "8) Technical Debt Reduction"
echo "9) Team Productivity"
read -p "Select strategic goal (1-9): " GOAL_CHOICE

case $GOAL_CHOICE in
    1) STRATEGIC_GOAL="Increase Revenue" ;;
    2) STRATEGIC_GOAL="Reduce Costs" ;;
    3) STRATEGIC_GOAL="Improve Customer Experience" ;;
    4) STRATEGIC_GOAL="Enter New Market" ;;
    5) STRATEGIC_GOAL="Product Innovation" ;;
    6) STRATEGIC_GOAL="Operational Excellence" ;;
    7) STRATEGIC_GOAL="Compliance & Risk Management" ;;
    8) STRATEGIC_GOAL="Technical Debt Reduction" ;;
    9) STRATEGIC_GOAL="Team Productivity" ;;
    *) echo -e "${RED}✗ ERROR: Invalid choice${NC}"; exit 1 ;;
esac

read -p "Explain how this project supports the strategic goal: " GOAL_DETAILS
validate_required "$GOAL_DETAILS" "Strategic Goal Details"

echo ""
echo "Revenue Impact Type:"
echo "1) Direct Revenue Generation"
echo "2) Revenue Enablement"
echo "3) Cost Reduction (OpEx)"
echo "4) Cost Reduction (CapEx)"
echo "5) Cost Avoidance"
echo "6) Customer Retention"
echo "7) Efficiency Gain"
echo "8) Risk Mitigation"
echo "9) None"
read -p "Select revenue impact type (1-9): " REVENUE_TYPE_CHOICE

case $REVENUE_TYPE_CHOICE in
    1) REVENUE_TYPE="Direct Revenue Generation" ;;
    2) REVENUE_TYPE="Revenue Enablement" ;;
    3) REVENUE_TYPE="Cost Reduction (OpEx)" ;;
    4) REVENUE_TYPE="Cost Reduction (CapEx)" ;;
    5) REVENUE_TYPE="Cost Avoidance" ;;
    6) REVENUE_TYPE="Customer Retention" ;;
    7) REVENUE_TYPE="Efficiency Gain" ;;
    8) REVENUE_TYPE="Risk Mitigation" ;;
    9) REVENUE_TYPE="None" ;;
    *) echo -e "${RED}✗ ERROR: Invalid choice${NC}"; exit 1 ;;
esac

read -p "Estimated Annual Financial Impact (\$, e.g., 50000): " ANNUAL_VALUE
validate_required "$ANNUAL_VALUE" "Annual Financial Impact"

echo ""
echo "Confidence Level:"
echo "1) High (>80%)"
echo "2) Medium (50-80%)"
echo "3) Low (<50%)"
read -p "Select confidence level (1-3): " CONFIDENCE_CHOICE

case $CONFIDENCE_CHOICE in
    1) CONFIDENCE="High (>80%)" ;;
    2) CONFIDENCE="Medium (50-80%)" ;;
    3) CONFIDENCE="Low (<50%)" ;;
    *) echo -e "${RED}✗ ERROR: Invalid choice${NC}"; exit 1 ;;
esac

read -p "Explain the revenue impact calculation: " REVENUE_EXPLANATION
validate_required "$REVENUE_EXPLANATION" "Revenue Impact Explanation"

read -p "Priority (Critical/High/Medium/Low): " PRIORITY
validate_required "$PRIORITY" "Priority"

echo ""
echo -e "${GREEN}Step 4: Risk Assessment (Required for Tier 3+)${NC}"
echo "─────────────────────────────────────"

REQUIRE_THREAT_MODEL="no"
REQUIRE_JIRA_CR="no"
if [ "$AGENT_TIER" -ge 3 ]; then
    echo -e "${YELLOW}⚠ Tier ${AGENT_TIER} requires threat modeling and Jira CR approval${NC}"
    REQUIRE_THREAT_MODEL="yes"
    REQUIRE_JIRA_CR="yes"
    read -p "Jira CR ID (for production deployment): " JIRA_CR_ID
    validate_required "$JIRA_CR_ID" "Jira CR ID"
else
    JIRA_CR_ID="N/A"
fi

# Generate approval request
REQUEST_ID=$(generate_request_id)
echo ""
echo -e "${GREEN}Step 5: Leadership Approval${NC}"
echo "─────────────────────────────────────"

# Determine approval tier based on budget and strategic goal
if [ "$BUDGET_LIMIT" -lt 500 ]; then
    APPROVAL_TIER="Team Lead Only (<\$500/mo)"
    REQUIRE_LEADERSHIP_APPROVAL="no"
elif [ "$BUDGET_LIMIT" -lt 2000 ]; then
    APPROVAL_TIER="Manager Approval (\$500-\$2K/mo)"
    REQUIRE_LEADERSHIP_APPROVAL="yes"
elif [ "$BUDGET_LIMIT" -lt 10000 ]; then
    APPROVAL_TIER="Director Approval (\$2K-\$10K/mo)"
    REQUIRE_LEADERSHIP_APPROVAL="yes"
elif [ "$BUDGET_LIMIT" -lt 50000 ]; then
    APPROVAL_TIER="VP Approval (\$10K-\$50K/mo)"
    REQUIRE_LEADERSHIP_APPROVAL="yes"
else
    APPROVAL_TIER="Executive Approval (>\$50K/mo or Strategic)"
    REQUIRE_LEADERSHIP_APPROVAL="yes"
fi

# Strategic goals always require executive approval
if [ "$STRATEGIC_GOAL" == "Enter New Market" ] || [ "$STRATEGIC_GOAL" == "Product Innovation" ]; then
    APPROVAL_TIER="Executive Approval (Strategic Initiative)"
    REQUIRE_LEADERSHIP_APPROVAL="yes"
fi

echo "Request ID: ${REQUEST_ID}"
echo "Approval Tier: ${APPROVAL_TIER}"
echo ""

if [ "$REQUIRE_LEADERSHIP_APPROVAL" == "yes" ]; then
    echo -e "${YELLOW}⚠ This project requires leadership approval before creation${NC}"
    echo ""
    echo "Summary:"
    echo "  Strategic Goal: ${STRATEGIC_GOAL}"
    echo "  Revenue Impact: \$${ANNUAL_VALUE}/year (${REVENUE_TYPE})"
    echo "  Monthly Budget: \$${BUDGET_LIMIT}"
    echo "  Priority: ${PRIORITY}"
    echo ""
    read -p "Generate approval request for Jira? (yes/no): " CREATE_APPROVAL

    if [ "$CREATE_APPROVAL" == "yes" ]; then
        # Create approval request JSON
        APPROVAL_DIR="${HOME}/projects/project-approval-requests"
        mkdir -p "${APPROVAL_DIR}"

        cat > "${APPROVAL_DIR}/${REQUEST_ID}.json" << EOF
{
  "request_id": "${REQUEST_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "requester": {
    "name": "${OWNER_NAME}",
    "email": "${OWNER_EMAIL}",
    "role": "Project Owner",
    "department": "Engineering"
  },
  "project_metadata": {
    "name": "${PROJECT_NAME}",
    "description": "${PROJECT_DESC}",
    "tech_stack": "${TECH_STACK}",
    "infrastructure": "${INFRASTRUCTURE}",
    "owner": {
      "name": "${OWNER_NAME}",
      "email": "${OWNER_EMAIL}"
    },
    "agent_tier": ${AGENT_TIER},
    "compliance": "${COMPLIANCE}"
  },
  "business_alignment": {
    "strategic_goal": "${STRATEGIC_GOAL}",
    "strategic_goal_details": "${GOAL_DETAILS}",
    "revenue_impact": {
      "type": "${REVENUE_TYPE}",
      "estimated_annual_value": ${ANNUAL_VALUE},
      "confidence_level": "${CONFIDENCE}",
      "explanation": "${REVENUE_EXPLANATION}"
    },
    "priority": "${PRIORITY}",
    "success_metrics": []
  },
  "resource_requirements": {
    "budget_monthly": ${BUDGET_LIMIT},
    "estimated_total_cost": ${BUDGET_LIMIT},
    "human_resources": []
  },
  "approval_workflow": {
    "approval_tier": "${APPROVAL_TIER}",
    "required_approvers": [],
    "status": "Draft"
  }
}
EOF

        echo ""
        echo -e "${GREEN}✅ Approval request created: ${APPROVAL_DIR}/${REQUEST_ID}.json${NC}"
        echo ""
        echo -e "${YELLOW}Next Steps:${NC}"
        echo "1. Review the approval request: cat ${APPROVAL_DIR}/${REQUEST_ID}.json"
        echo "2. Submit for approval:"
        echo "   python3 $(dirname "$0")/submit-project-approval.py --request-file ${APPROVAL_DIR}/${REQUEST_ID}.json"
        echo ""
        echo "3. After approval, run this script again to create the project"
        echo ""
        echo -e "${RED}⛔ Project creation paused - leadership approval required${NC}"
        exit 0
    else
        echo -e "${RED}⛔ Cannot proceed without leadership approval for this budget tier${NC}"
        exit 1
    fi
fi

# Create project directory structure
PROJECT_PATH="${HOME}/projects/${PROJECT_NAME}"

if [ -d "$PROJECT_PATH" ]; then
    echo -e "${RED}✗ ERROR: Project directory already exists: ${PROJECT_PATH}${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Creating governed project structure...${NC}"

mkdir -p "${PROJECT_PATH}"/{src,tests,docs,scripts,config,.claude/{prompts,commands}}

# Create mandatory Claude Code context
cat > "${PROJECT_PATH}/.claude/prompts/project-context.md" << EOF
# ${PROJECT_NAME} - Project Context

## Project Overview
${PROJECT_DESC}

**Owner**: ${OWNER_NAME} <${OWNER_EMAIL}>
**Created**: $(date +%Y-%m-%d)
**Agent Tier**: ${AGENT_TIER}
**Compliance**: ${COMPLIANCE}

## Tech Stack
${TECH_STACK}

## Infrastructure
${INFRASTRUCTURE}

## Governance & Accountability

### Agent Tier ${AGENT_TIER} Requirements
EOF

case $AGENT_TIER in
    1)
        cat >> "${PROJECT_PATH}/.claude/prompts/project-context.md" << EOF
- **Access**: Read-only operations
- **Use Cases**: Documentation, analysis, Q&A
- **Cost Target**: \$0.10-\$0.50/task
- **Required Mitigations**: MI-001 (data leakage), MI-009 (cost monitoring)
EOF
        ;;
    2)
        cat >> "${PROJECT_PATH}/.claude/prompts/project-context.md" << EOF
- **Access**: Development environment only
- **Use Cases**: Coding, testing, refactoring
- **Cost Target**: \$0.50-\$5.00/task
- **Required Mitigations**: MI-001, MI-009, MI-021 (budget limits)
EOF
        ;;
    3)
        cat >> "${PROJECT_PATH}/.claude/prompts/project-context.md" << EOF
- **Access**: Production (with approval)
- **Use Cases**: Deployments, runbooks, operations
- **Cost Target**: \$1.00-\$10.00/task
- **Required Mitigations**: MI-001, MI-003, MI-009, MI-021
- **Approvals Required**: Jira CR (${JIRA_CR_ID})
- **Threat Modeling**: REQUIRED before production deployment
EOF
        ;;
    4)
        cat >> "${PROJECT_PATH}/.claude/prompts/project-context.md" << EOF
- **Access**: Design & research
- **Use Cases**: System design, POCs, architecture
- **Cost Target**: \$5.00-\$50.00/task
- **Required Mitigations**: MI-001, MI-003, MI-009, MI-021
- **Approvals Required**: Jira CR (${JIRA_CR_ID})
- **Threat Modeling**: REQUIRED before production deployment
EOF
        ;;
esac

cat >> "${PROJECT_PATH}/.claude/prompts/project-context.md" << EOF

### Budget & Cost Controls
- **Monthly Budget**: \$${BUDGET_LIMIT}
- **Cost Tracking**: OpenTelemetry metrics enabled
- **Budget Alerts**: Enabled at 50%, 75%, 90% thresholds
- **Cost Reporting**: Weekly reports to ${OWNER_EMAIL}

### Compliance Requirements
${COMPLIANCE}

### Audit & Accountability
- **Audit Trail**: All operations logged with correlation IDs
- **SIEM Integration**: Real-time event emission (OCSF-compliant)
- **Human Oversight**: ${OWNER_NAME} is accountable for all agent actions
- **Review Frequency**: $([ "$AGENT_TIER" -ge 3 ] && echo "Daily" || echo "Weekly")

## Project Structure
\`\`\`
/${PROJECT_NAME}
├── src/           # Application source code
├── tests/         # Test files
├── docs/          # Documentation
├── scripts/       # Automation scripts
├── config/        # Configuration files
└── .claude/       # Claude Code governance config
    ├── prompts/   # Auto-loaded context
    └── commands/  # Custom slash commands
\`\`\`

## Development Workflow
- Setup: [Add setup commands]
- Run: [Add run commands]
- Test: [Add test commands]
- Build: [Add build commands]
- Deploy: [Add deployment workflow]

## Key File Paths
- Main entry: src/
- Configuration: config/
- Tests: tests/
- Documentation: docs/

## Governance Principles (Enforced)
1. **Human Primacy** - ${OWNER_NAME} has final authority
2. **Transparency** - All actions auditable via OpenTelemetry
3. **Accountability** - Owner responsible for agent outcomes
4. **Safety** - Tier ${AGENT_TIER} controls enforced
5. **Cost Efficiency** - \$${BUDGET_LIMIT}/month budget enforced

## Common Tasks
[Customize based on your project type]

## Notes
This project was created with governance enforcement on $(date +%Y-%m-%d).
All AI agent operations are subject to the governance framework.
EOF

# Create settings.local.json with tier-appropriate permissions
cat > "${PROJECT_PATH}/.claude/settings.local.json" << EOF
{
  "permissions": {
    "allow": [
      "Read(//${PROJECT_PATH}/**)"
    ],
    "deny": [],
    "ask": []
  },
  "metadata": {
    "project_name": "${PROJECT_NAME}",
    "owner": "${OWNER_NAME}",
    "owner_email": "${OWNER_EMAIL}",
    "agent_tier": ${AGENT_TIER},
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "compliance": "${COMPLIANCE}",
    "budget_limit_monthly": ${BUDGET_LIMIT},
    "jira_cr_id": "${JIRA_CR_ID}",
    "governance_framework_version": "2.1"
  }
}
EOF

# Create mandatory governance files
cat > "${PROJECT_PATH}/GOVERNANCE.md" << EOF
# Governance & Accountability

**Project**: ${PROJECT_NAME}
**Owner**: ${OWNER_NAME} <${OWNER_EMAIL}>
**Agent Tier**: ${AGENT_TIER}
**Budget**: \$${BUDGET_LIMIT}/month

## Human Accountability
${OWNER_NAME} is the accountable human for all AI agent actions in this project.

## Required Controls
$([ "$AGENT_TIER" -ge 1 ] && echo "- MI-001: Data leakage prevention")
$([ "$AGENT_TIER" -ge 1 ] && echo "- MI-009: Cost monitoring")
$([ "$AGENT_TIER" -ge 2 ] && echo "- MI-021: Budget limits")
$([ "$AGENT_TIER" -ge 3 ] && echo "- MI-003: Input validation")
$([ "$AGENT_TIER" -ge 3 ] && echo "- Threat modeling (STRIDE-based)")
$([ "$AGENT_TIER" -ge 3 ] && echo "- Jira CR approval: ${JIRA_CR_ID}")

## Compliance
${COMPLIANCE}

## Audit Trail
All operations are logged and correlated for audit purposes.

## Framework
This project follows the AI Agent Governance Framework v2.1.
See: ~/projects/ai-agent-governance-framework/
EOF

cat > "${PROJECT_PATH}/README.md" << EOF
# ${PROJECT_NAME}

${PROJECT_DESC}

## Quick Start
[Add setup and usage instructions]

## Governance
This project enforces AI governance from inception. See [GOVERNANCE.md](GOVERNANCE.md) for details.

**Owner**: ${OWNER_NAME} <${OWNER_EMAIL}>
**Agent Tier**: ${AGENT_TIER}
**Budget**: \$${BUDGET_LIMIT}/month

## Project Structure
- \`src/\` - Application code
- \`tests/\` - Test files
- \`docs/\` - Documentation
- \`scripts/\` - Automation
- \`.claude/\` - AI governance config

## Development
\`\`\`bash
# Setup
[Add commands]

# Run
[Add commands]

# Test
[Add commands]
\`\`\`

## Compliance
${COMPLIANCE}

## Framework
Built with [AI Agent Governance Framework v2.1](${HOME}/projects/ai-agent-governance-framework/)
EOF

# Create .gitignore
cat > "${PROJECT_PATH}/.gitignore" << EOF
# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# Environment
.env
.env.local
*.key
*.pem

# Build
dist/
build/
*.log

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Keep Claude settings (contains governance metadata)
# .claude/settings.local.json is tracked for accountability
EOF

# Initialize git with governance commit
cd "${PROJECT_PATH}"
git init
git add .
git commit -m "Initial commit: Governed project creation

Project: ${PROJECT_NAME}
Owner: ${OWNER_NAME} <${OWNER_EMAIL}>
Agent Tier: ${AGENT_TIER}
Compliance: ${COMPLIANCE}
Budget: \$${BUDGET_LIMIT}/month
Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)

🤖 Created with AI Agent Governance Framework v2.1
Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Governed Project Created Successfully!                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Project Path:${NC} ${PROJECT_PATH}"
echo -e "${BLUE}Owner:${NC} ${OWNER_NAME} <${OWNER_EMAIL}>"
echo -e "${BLUE}Agent Tier:${NC} ${AGENT_TIER}"
echo -e "${BLUE}Budget:${NC} \$${BUDGET_LIMIT}/month"
echo -e "${BLUE}Compliance:${NC} ${COMPLIANCE}"
echo ""

if [ "$REQUIRE_THREAT_MODEL" == "yes" ]; then
    echo -e "${YELLOW}⚠ REQUIRED NEXT STEPS (Tier ${AGENT_TIER}):${NC}"
    echo "1. Run threat model: ~/projects/ai-agent-governance-framework/workflows/threat-modeling/scripts/run-threat-model.sh"
    echo "2. Implement required mitigations"
    echo "3. Validate Jira CR approval: ${JIRA_CR_ID}"
    echo ""
fi

echo -e "${GREEN}Next Steps:${NC}"
echo "1. cd ${PROJECT_PATH}"
echo "2. Customize project-context.md with your specific details"
echo "3. Add your source code to src/"
echo "4. Open in Claude Code - governance context loads automatically!"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "- Project governance: ${PROJECT_PATH}/GOVERNANCE.md"
echo "- Claude context: ${PROJECT_PATH}/.claude/prompts/project-context.md"
echo "- Framework docs: ~/projects/ai-agent-governance-framework/docs/"
echo ""
echo -e "${GREEN}🎉 Your AI-driven project is ready with built-in accountability!${NC}"
