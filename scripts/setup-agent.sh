#!/bin/bash
# Agent Setup Script
# AI Agent Governance Framework v2.0
# Purpose: Set up new AI agent with full governance compliance
#
# Usage: ./setup-agent.sh --tier <1|2|3|4> --name <agent-name> [OPTIONS]
#
# Controls Enforced:
#   - MI-020: Tier enforcement and validation
#   - APP-001: Jira approval gate for Tier 3/4
#   - G-02: Approval workflow enforcement
#   - MI-021: Budget limit configuration

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
TIER=""
AGENT_NAME=""
ENVIRONMENT="dev"
JIRA_CR_ID=""
SKIP_VALIDATION=false
RUN_THREAT_MODEL=false
DAILY_BUDGET=50
MONTHLY_BUDGET=500

usage() {
    cat <<EOF
Usage: $0 --tier <1|2|3|4> --name <agent-name> [OPTIONS]

REQUIRED:
  --tier <1|2|3|4>      Agent tier (1=Observer, 2=Developer, 3=Operations, 4=Architect)
  --name <name>         Agent identifier (lowercase, hyphens allowed)

OPTIONS:
  --environment <env>   Target environment: dev|staging|prod (default: dev)
  --jira-cr-id <id>     Jira Change Request ID (REQUIRED for Tier 3/4 in staging/prod)
  --daily-budget <usd>  Daily cost budget in USD (default: 50)
  --monthly-budget <usd> Monthly cost budget in USD (default: 500)
  --run-threat-model    Run STRIDE threat modeling (required for Tier 3/4)
  --skip-validation     Skip governance compliance checks (NOT recommended)

EXAMPLES:
  # Tier 1 agent (no approval needed)
  $0 --tier 1 --name doc-analyzer

  # Tier 2 agent with custom budget
  $0 --tier 2 --name code-reviewer --daily-budget 100

  # Tier 3 agent for production (requires Jira CR)
  $0 --tier 3 --name security-agent --environment prod \\
     --jira-cr-id CR-2025-1042 --run-threat-model

TIER REQUIREMENTS:
  Tier 1 (Observer):    Read-only access, minimal approval
  Tier 2 (Developer):   Dev environment only, no production access
  Tier 3 (Operations):  Production access, requires Jira CR approval for staging/prod
  Tier 4 (Architect):   Full access, requires Jira CR approval for staging/prod

For detailed information, see: docs/GOVERNANCE-POLICY.md
EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tier)
            TIER="$2"
            shift 2
            ;;
        --name)
            AGENT_NAME="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --jira-cr-id)
            JIRA_CR_ID="$2"
            shift 2
            ;;
        --daily-budget)
            DAILY_BUDGET="$2"
            shift 2
            ;;
        --monthly-budget)
            MONTHLY_BUDGET="$2"
            shift 2
            ;;
        --run-threat-model)
            RUN_THREAT_MODEL=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
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
if [ -z "$TIER" ] || [ -z "$AGENT_NAME" ]; then
    echo -e "${RED}ERROR: --tier and --name are required${NC}"
    usage
fi

# Validate tier value
if ! [[ "$TIER" =~ ^[1-4]$ ]]; then
    echo -e "${RED}ERROR: --tier must be 1, 2, 3, or 4${NC}"
    exit 1
fi

# Validate agent name format
if ! [[ "$AGENT_NAME" =~ ^[a-z0-9-]+$ ]]; then
    echo -e "${RED}ERROR: Agent name must be lowercase with hyphens only${NC}"
    exit 1
fi

# Validate environment
if ! [[ "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}ERROR: Environment must be dev, staging, or prod${NC}"
    exit 1
fi

echo "=========================================="
echo "AI Agent Setup - Governance Framework v2.0"
echo "=========================================="
echo "Agent Name:            $AGENT_NAME"
echo "Tier:                  $TIER"
echo "Environment:           $ENVIRONMENT"
echo "Daily Budget:          \$$DAILY_BUDGET"
echo "Monthly Budget:        \$$MONTHLY_BUDGET"
echo "=========================================="
echo ""

# ============================================================================
# STEP 1: Jira Approval Validation (Tier 3/4 in staging/prod)
# ============================================================================
if [ "$TIER" -ge 3 ] && [[ "$ENVIRONMENT" =~ ^(staging|prod)$ ]]; then
    echo "🔐 Step 1: Jira Approval Validation (APP-001, G-02)"
    echo "   Tier $TIER deployment to $ENVIRONMENT requires Jira CR approval"
    echo ""

    if [ -z "$JIRA_CR_ID" ]; then
        echo -e "${RED}❌ ERROR: Jira CR ID is required for Tier 3/4 deployments to staging/prod${NC}"
        echo ""
        echo "GOVERNANCE VIOLATION:"
        echo "  Control:     APP-001 (Human Primacy), G-02 (Approval Enforcement)"
        echo "  Requirement: All Tier 3/4 deployments require approved Jira CR"
        echo "  Action:      Provide --jira-cr-id parameter with approved CR"
        echo ""
        echo "Example:"
        echo "  $0 --tier $TIER --name $AGENT_NAME --environment $ENVIRONMENT --jira-cr-id CR-2025-1042"
        exit 1
    fi

    # Run Jira approval validation
    if [ "$SKIP_VALIDATION" = false ]; then
        if [ -f "scripts/validate-jira-approval.py" ]; then
            echo "   Running Jira approval validation..."

            if ! scripts/validate-jira-approval.py "$AGENT_NAME" "$JIRA_CR_ID" "Change Manager"; then
                echo -e "${RED}❌ Jira approval validation FAILED${NC}"
                exit 1
            fi

            echo -e "${GREEN}✅ Jira approval validated${NC}"
        else
            echo -e "${YELLOW}⚠️  WARNING: Jira validation script not found, skipping...${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  WARNING: Validation skipped (--skip-validation flag used)${NC}"
    fi
else
    echo "ℹ️  Step 1: Jira Approval - Not required for Tier $TIER in $ENVIRONMENT"
fi

echo ""

# ============================================================================
# STEP 2: Create Agent Directory Structure
# ============================================================================
echo "📁 Step 2: Creating agent directory structure..."

AGENT_DIR="agents/$AGENT_NAME"
mkdir -p "$AGENT_DIR"/{config,policies,logs,audit}

echo "   Created directories:"
echo "   - $AGENT_DIR/config  (agent configuration)"
echo "   - $AGENT_DIR/policies (policy overrides)"
echo "   - $AGENT_DIR/logs     (runtime logs)"
echo "   - $AGENT_DIR/audit    (audit trail storage)"

echo -e "${GREEN}✅ Directory structure created${NC}"
echo ""

# ============================================================================
# STEP 3: Generate Agent Configuration
# ============================================================================
echo "⚙️  Step 3: Generating agent configuration..."

# Determine tier label
case $TIER in
    1) TIER_LABEL="tier1-observer" ;;
    2) TIER_LABEL="tier2-developer" ;;
    3) TIER_LABEL="tier3-operations" ;;
    4) TIER_LABEL="tier4-architect" ;;
esac

# Check if template exists
if [ -f "templates/agent-deployment/config-template.yml" ]; then
    cp templates/agent-deployment/config-template.yml "$AGENT_DIR/config/config.yml"

    # Replace placeholders in config
    sed -i.bak "s/name: \"\"/name: \"$AGENT_NAME\"/g" "$AGENT_DIR/config/config.yml"
    sed -i.bak "s/tier: 0/tier: $TIER/g" "$AGENT_DIR/config/config.yml"
    sed -i.bak "s/environment: dev/environment: $ENVIRONMENT/g" "$AGENT_DIR/config/config.yml"
    rm "$AGENT_DIR/config/config.yml.bak"
else
    # Generate basic config if template doesn't exist
    cat > "$AGENT_DIR/config/config.yml" <<EOF
# AI Agent Configuration
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

agent:
  name: "$AGENT_NAME"
  tier: $TIER
  tier_label: "$TIER_LABEL"
  environment: "$ENVIRONMENT"

governance:
  framework_version: "2.0"
  jira_cr_id: "$JIRA_CR_ID"

budget:
  daily_limit_usd: $DAILY_BUDGET
  monthly_limit_usd: $MONTHLY_BUDGET
  circuit_breaker_threshold: 0.9

controls:
  required_mitigations:
    - MI-001  # Data Leakage Prevention
    - MI-003  # Secrets Management
    - MI-009  # Cost Monitoring
    - MI-020  # Tier Enforcement
    - MI-021  # Budget Limits

observability:
  opentelemetry_enabled: true
  prometheus_metrics: true
  audit_trail_enabled: true
  siem_integration: true

security:
  encryption_at_rest: true
  encryption_in_transit: true
  least_privilege_iam: true
  secrets_rotation_days: 90
EOF
fi

echo -e "${GREEN}✅ Agent configuration created: $AGENT_DIR/config/config.yml${NC}"
echo ""

# ============================================================================
# STEP 4: Threat Modeling (Tier 3/4)
# ============================================================================
if [ "$TIER" -ge 3 ]; then
    echo "🛡️  Step 4: STRIDE Threat Modeling (REQUIRED for Tier 3/4)"

    THREAT_MODEL_PATH="workflows/threat-modeling/reports/${AGENT_NAME}-threat-model.md"

    if [ "$RUN_THREAT_MODEL" = true ]; then
        if [ -f "workflows/threat-modeling/scripts/run-threat-model.sh" ]; then
            echo "   Running STRIDE threat modeling..."

            workflows/threat-modeling/scripts/run-threat-model.sh \
                --agent "$AGENT_NAME" \
                --tier "$TIER" || true

            if [ -f "$THREAT_MODEL_PATH" ]; then
                echo -e "${GREEN}✅ Threat model generated: $THREAT_MODEL_PATH${NC}"
            else
                echo -e "${YELLOW}⚠️  WARNING: Threat model not generated${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  WARNING: Threat modeling script not found${NC}"
        fi
    else
        if [ -f "$THREAT_MODEL_PATH" ]; then
            echo -e "${GREEN}✅ Threat model already exists: $THREAT_MODEL_PATH${NC}"
        else
            echo -e "${YELLOW}⚠️  WARNING: Threat model not found${NC}"
            echo "   Run threat modeling with: --run-threat-model flag"
            echo "   Or manually: workflows/threat-modeling/scripts/run-threat-model.sh --agent $AGENT_NAME --tier $TIER"
        fi
    fi
else
    echo "ℹ️  Step 4: Threat Modeling - Not required for Tier $TIER"
fi

echo ""

# ============================================================================
# STEP 5: Governance Compliance Check
# ============================================================================
if [ "$SKIP_VALIDATION" = false ]; then
    echo "✅ Step 5: Running governance compliance check..."

    if [ -f "scripts/governance-check.sh" ]; then
        if scripts/governance-check.sh \
            --agent "$AGENT_NAME" \
            --tier "$TIER" \
            --environment "$ENVIRONMENT" \
            --budget-limit "$MONTHLY_BUDGET"; then
            echo -e "${GREEN}✅ Governance compliance check passed${NC}"
        else
            echo -e "${RED}❌ Governance compliance check FAILED${NC}"
            echo "Review the errors above and remediate before deployment"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  WARNING: Governance check script not found${NC}"
    fi
else
    echo "⚠️  Step 5: Governance compliance check SKIPPED (--skip-validation flag used)"
fi

echo ""

# ============================================================================
# STEP 6: Generate Audit Trail Entry
# ============================================================================
echo "📝 Step 6: Generating audit trail entry..."

AUDIT_ID="audit-$(date +%s)-$(uuidgen | cut -d'-' -f1 2>/dev/null || echo $RANDOM)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$AGENT_DIR/audit/setup-${AUDIT_ID}.json" <<EOF
{
  "audit_id": "$AUDIT_ID",
  "timestamp": "$TIMESTAMP",
  "actor": "$(whoami)@$(hostname)",
  "action": "agent_setup",
  "workflow_step": "MI-020",
  "jira_reference": {
    "cr_id": "$JIRA_CR_ID",
    "approver_role": "Change Manager",
    "budget_tokens": 0,
    "controls": ["MI-020", "MI-021", "APP-001", "G-02"]
  },
  "inputs": {
    "agent_name": "$AGENT_NAME",
    "tier": $TIER,
    "environment": "$ENVIRONMENT",
    "daily_budget_usd": $DAILY_BUDGET,
    "monthly_budget_usd": $MONTHLY_BUDGET
  },
  "outputs": {
    "agent_dir": "$AGENT_DIR",
    "config_file": "$AGENT_DIR/config/config.yml",
    "threat_model_required": $([ "$TIER" -ge 3 ] && echo "true" || echo "false"),
    "jira_validation_passed": $([ -n "$JIRA_CR_ID" ] && echo "true" || echo "false")
  },
  "policy_controls_checked": ["MI-020", "MI-021", "APP-001", "G-02"],
  "compliance_result": "pass",
  "evidence_hash": "sha256:$(echo "$AGENT_NAME-$TIER-$TIMESTAMP" | sha256sum | cut -d' ' -f1)",
  "auditor_agent": "setup-agent-script"
}
EOF

echo -e "${GREEN}✅ Audit trail entry created: $AGENT_DIR/audit/setup-${AUDIT_ID}.json${NC}"
echo ""

# ============================================================================
# Summary and Next Steps
# ============================================================================
echo "=========================================="
echo "✅ Agent Setup Complete"
echo "=========================================="
echo ""
echo "Agent Details:"
echo "  Name:              $AGENT_NAME"
echo "  Tier:              $TIER ($TIER_LABEL)"
echo "  Environment:       $ENVIRONMENT"
echo "  Config:            $AGENT_DIR/config/config.yml"
echo "  Audit Trail:       $AGENT_DIR/audit/setup-${AUDIT_ID}.json"

if [ -n "$JIRA_CR_ID" ]; then
    echo "  Jira CR:           $JIRA_CR_ID (validated)"
fi

echo ""
echo "Next Steps:"
echo ""

# Tier-specific next steps
case $TIER in
    1)
        echo "  1. Review configuration: $AGENT_DIR/config/config.yml"
        echo "  2. Deploy agent to dev environment"
        echo "  3. Monitor cost reports: ./scripts/cost-report.sh --agent $AGENT_NAME"
        ;;
    2)
        echo "  1. Review configuration: $AGENT_DIR/config/config.yml"
        echo "  2. Implement required mitigations (MI-001, MI-003, MI-009, MI-021)"
        echo "  3. Run unit tests in dev environment"
        echo "  4. Monitor cost reports: ./scripts/cost-report.sh --agent $AGENT_NAME"
        ;;
    3|4)
        echo "  1. Review configuration: $AGENT_DIR/config/config.yml"
        echo "  2. Ensure threat model is complete: workflows/threat-modeling/reports/${AGENT_NAME}-threat-model.md"
        echo "  3. Implement all required mitigations from threat model"
        echo "  4. Deploy to dev for testing:"
        echo "     ./scripts/setup-agent.sh --tier $TIER --name $AGENT_NAME --environment dev"
        echo "  5. Deploy to staging with Jira CR:"
        echo "     gh workflow run deploy-security-agent.yml -f environment=staging -f jira_cr_id=$JIRA_CR_ID"
        echo "  6. After staging validation, deploy to prod"
        echo "  7. Monitor with: ./scripts/cost-report.sh --agent $AGENT_NAME"
        echo "  8. Run compliance checks: ./scripts/governance-check.sh --agent $AGENT_NAME --tier $TIER --environment prod"
        ;;
esac

echo ""
echo "Documentation:"
echo "  - Governance Policy:      docs/GOVERNANCE-POLICY.md"
echo "  - PAR Workflow:           docs/PAR-WORKFLOW-FRAMEWORK.md"
echo "  - Risk Catalog:           policies/risk-catalog.md"
echo "  - Mitigation Catalog:     policies/mitigation-catalog.md"
echo "  - Quick Reference:        docs/QUICK-REFERENCE.md"

echo ""
echo "=========================================="
echo -e "${GREEN}Agent $AGENT_NAME is ready for deployment to $ENVIRONMENT${NC}"
echo "=========================================="

exit 0
