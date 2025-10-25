# Leadership Approval Workflow for Project Creation

## Overview
This document describes the **leadership approval and revenue alignment system** that ensures all AI-driven projects support strategic business goals and generate measurable value.

## Philosophy
**Every project must justify its existence through strategic alignment and financial impact.**

Leadership needs to know:
1. **Which strategic goal** does this project support?
2. **What revenue impact** will it have?
3. **What's the ROI** compared to cost?
4. **Is this aligned** with company OKRs?

## Approval Workflow

### Step 1: Project Creation Request
When someone creates a project using `create-governed-project.sh`, they must provide:

**Business Alignment (Required)**
- Strategic goal selection (9 options)
- Detailed explanation of alignment
- Revenue impact type
- Estimated annual financial value
- Confidence level
- Revenue calculation explanation
- Priority level

**Resource Requirements (Required)**
- Monthly AI agent budget
- Estimated total project cost
- Human resource allocation

### Step 2: Automatic Approval Tier Determination

The system automatically determines required approval tier based on:

| Budget/Month | Approval Tier | Decision Maker |
|--------------|---------------|----------------|
| < $500 | Team Lead Only | Proceeds immediately |
| $500 - $2K | Manager Approval | Engineering/Product Manager |
| $2K - $10K | Director Approval | Director of Engineering |
| $10K - $50K | VP Approval | VP of Engineering/Product |
| > $50K | Executive Approval | C-Level Executive |

**Strategic Initiative Override:**
- "Enter New Market" → Executive Approval (regardless of budget)
- "Product Innovation" → Executive Approval (regardless of budget)

### Step 3: Leadership Review in Jira

If approval is required (budget >= $500 or strategic initiative):

1. **Approval request JSON is generated**
   - Location: `~/projects/project-approval-requests/PCR-YYYY-NNNN.json`
   - Contains complete project details, business case, ROI

2. **Jira issue is created** (via `submit-project-approval.py`)
   - Project: PROJAPPR (Project Approvals)
   - Rich formatted description with:
     - Project overview
     - Business alignment and strategic goal
     - Revenue impact analysis
     - Financial analysis (ROI, payback period)
     - Resource requirements
     - Risk assessment
     - Required approvers

3. **Slack notification sent** (optional)
   - Posted to leadership channel
   - Includes key metrics and Jira link
   - Action button to review

4. **Leadership reviews and decides**
   - Approve → Project can be created
   - Reject → Project blocked with reason
   - Request More Info → Requester provides additional details

### Step 4: Project Creation
Once approved:
- Requester runs `create-governed-project.sh` again
- For budgets < $500, proceeds immediately
- For budgets >= $500, must provide approved Jira issue key

## Revenue Impact Types

Leadership sees one of these revenue impact types:

| Type | Description | Examples |
|------|-------------|----------|
| **Direct Revenue Generation** | Project directly generates new revenue | Sales automation bot, lead generation |
| **Revenue Enablement** | Enables sales/growth teams | CRM integration, proposal generator |
| **Cost Reduction (OpEx)** | Reduces operating expenses | Support automation, process efficiency |
| **Cost Reduction (CapEx)** | Reduces capital expenditures | Cloud optimization, infrastructure automation |
| **Cost Avoidance** | Prevents future costs | Compliance automation, security improvements |
| **Customer Retention** | Improves retention/reduces churn | Customer success bot, proactive support |
| **Efficiency Gain** | Increases team productivity | Development tools, automation |
| **Risk Mitigation** | Reduces business/technical risk | Security scanning, compliance monitoring |
| **None** | No direct financial impact | Exploratory projects, R&D |

## Strategic Goals Alignment

Every project must map to one of these company strategic goals:

1. **Increase Revenue** - New revenue streams, upsell/cross-sell
2. **Reduce Costs** - Operating efficiency, automation
3. **Improve Customer Experience** - Satisfaction, NPS, support quality
4. **Enter New Market** - Geographic, vertical, or product expansion
5. **Product Innovation** - New capabilities, competitive differentiation
6. **Operational Excellence** - Process improvement, quality
7. **Compliance & Risk Management** - Regulatory, security, audit
8. **Technical Debt Reduction** - Code quality, maintainability
9. **Team Productivity** - Developer/ops efficiency, tooling

## Financial Analysis (Auto-Calculated)

Leadership sees automatic ROI calculations:

```
Monthly AI Budget:        $2,000
Monthly Infrastructure:   $500
Total Monthly Cost:       $2,500
Annual Cost:             $30,000

Estimated Annual Value:  $150,000
ROI Ratio:               5.0:1
Payback Period:          2.4 months
Net Annual Impact:       +$120,000
```

**Decision Criteria:**
- ROI < 2:1 → Requires strong justification
- ROI 2:1 to 5:1 → Standard approval
- ROI > 5:1 → Fast-track approval
- Payback < 6 months → Positive signal
- Payback > 12 months → Requires long-term strategic rationale

## Jira Integration

### Issue Format

**Summary:**
```
Project Approval: customer-support-bot - $2000/mo - Reduce Costs
```

**Description:**
- Rich Jira formatting with sections:
  - 🚀 Project Overview
  - 🎯 Business Alignment
  - 💰 Financial Analysis (with ROI)
  - ⚠️ Risk Assessment
  - ✅ Approval Required
  - 📝 Next Steps for Approvers

**Labels:**
- `agent-tier-3`
- `budget-$2000`
- `reduce-costs`
- `cost-reduction-opex`
- `engineering`

**Custom Fields:**
- Request ID: PCR-2025-0123

### Approval Process in Jira

1. **Leadership reviews** the business case in Jira
2. **Comments** for questions or more information
3. **Transitions** issue:
   - "Approve" → Sets status to "Approved"
   - "Reject" → Sets status to "Rejected" with reason
   - "More Info Needed" → Back to requester

4. **Automated notification** to requester
5. **Requester proceeds** with project creation (if approved)

## Usage Examples

### Example 1: Small Project (No Approval Required)

```bash
$ ./create-governed-project.sh

# User fills in:
Project Name: log-analyzer
Budget: $300/month
Strategic Goal: Team Productivity
Revenue Impact: Efficiency Gain, $10,000/year

# Result:
✅ Approval Tier: Team Lead Only (<$500/mo)
✅ Project created immediately (no approval gate)
```

### Example 2: Medium Project (Manager Approval)

```bash
$ ./create-governed-project.sh

# User fills in:
Project Name: customer-support-bot
Budget: $1,500/month
Strategic Goal: Reduce Costs
Revenue Impact: Cost Reduction (OpEx), $80,000/year

# Result:
⚠ This project requires leadership approval
✅ Approval request created: ~/projects/project-approval-requests/PCR-2025-0234.json

Next Steps:
1. Review request
2. Submit to Jira: python3 submit-project-approval.py --request-file PCR-2025-0234.json
3. Wait for manager approval
4. Re-run script with approved Jira issue
```

### Example 3: Strategic Initiative (Executive Approval)

```bash
$ ./create-governed-project.sh

# User fills in:
Project Name: ai-product-recommendations
Budget: $5,000/month
Strategic Goal: Product Innovation
Revenue Impact: Direct Revenue Generation, $500,000/year

# Result:
⚠ This project requires leadership approval
✅ Approval Tier: Executive Approval (Strategic Initiative)
✅ Jira issue PROJAPPR-456 created
✅ Slack notification sent to #leadership

Next Steps:
1. Executive reviews in Jira
2. Business case discussion
3. Approval or request for more info
4. Re-run script after approval
```

## Integration with Existing Governance

This approval workflow integrates with the existing agent tier system:

| Agent Tier | Existing Controls | New Approval Requirement |
|------------|-------------------|--------------------------|
| **Tier 1** (Observer) | Read-only, MI-001, MI-009 | Leadership approval if budget >= $500 |
| **Tier 2** (Developer) | Dev env, MI-001/009/021 | Leadership approval if budget >= $500 |
| **Tier 3** (Operations) | Production, threat model, Jira CR | Leadership approval if budget >= $500 + production CR |
| **Tier 4** (Architect) | Design, threat model, Jira CR | Leadership approval if budget >= $500 + architecture review |

**Key Point:** Budget-based approval is a **separate gate** from tier-based controls. Both must be satisfied.

## Slack Notifications

Optional Slack integration notifies leadership channel:

```
🚀 New Project Approval Request: customer-support-bot

Requester: Jane Smith | Engineering
Strategic Goal: Reduce Costs | Priority: High
Monthly Budget: $1,500 | Est. Annual Value: $80,000
ROI: 5.3:1 | Agent Tier: 3

Revenue Impact: Cost Reduction (OpEx)
Automates tier-1 support inquiries, reducing support team load...

[Review in Jira] (button)
```

## Audit Trail

All approval requests include complete audit trail:

```json
{
  "audit_trail": {
    "created_at": "2025-10-23T14:30:00Z",
    "created_by": "jane.smith@example.com",
    "last_updated": "2025-10-23T15:45:00Z",
    "updated_by": "manager@example.com",
    "approval_history": [
      {
        "timestamp": "2025-10-23T14:30:00Z",
        "actor": "jane.smith@example.com",
        "action": "Created",
        "details": "Initial request submission"
      },
      {
        "timestamp": "2025-10-23T15:45:00Z",
        "actor": "manager@example.com",
        "action": "Approved",
        "details": "Strong business case, clear ROI"
      }
    ]
  }
}
```

## Scripts & Tools

### 1. Create Governed Project (with Approval Gate)
```bash
~/projects/ai-agent-governance-framework/scripts/create-governed-project.sh
```
- Collects business alignment data
- Determines approval tier
- Generates approval request if needed
- Blocks project creation until approved

### 2. Submit Project Approval
```bash
python3 ~/projects/ai-agent-governance-framework/scripts/submit-project-approval.py \
  --request-file ~/projects/project-approval-requests/PCR-2025-0001.json
```
- Creates Jira issue with rich formatting
- Calculates ROI and financial metrics
- Sends Slack notification
- Returns Jira issue key

### 3. Check Approval Status
```bash
# Query Jira API to check status
curl -u $JIRA_USERNAME:$JIRA_API_TOKEN \
  https://your-company.atlassian.net/rest/api/3/issue/PROJAPPR-123
```

## Environment Variables

Configure these for Jira/Slack integration:

```bash
# Jira Configuration
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_USERNAME="automation@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT_APPROVAL_KEY="PROJAPPR"

# Slack Configuration (optional)
export SLACK_LEADERSHIP_WEBHOOK="https://hooks.slack.com/services/..."
```

## Schema

Complete JSON schema: `policies/schemas/project-creation-request.json`

Key fields:
- `request_id` - Unique identifier (PCR-YYYY-NNNN)
- `requester` - Person creating project
- `project_metadata` - Technical details
- `business_alignment` - Strategic goal, revenue impact, success metrics
- `resource_requirements` - Budget, human resources
- `approval_workflow` - Approval tier, required approvers, status
- `risk_assessment` - Risk factors and mitigations
- `audit_trail` - Complete history

## Benefits

### For Leadership
✅ **Visibility** - Know about all projects before they start
✅ **Strategic Alignment** - Ensure projects support company goals
✅ **ROI Awareness** - Understand expected financial impact
✅ **Budget Control** - Approve spending before commitments
✅ **Risk Management** - Review risks before projects begin
✅ **Audit Trail** - Complete record of decisions

### For Teams
✅ **Clear Process** - Know what's required upfront
✅ **Fast Approval** - Small projects (<$500) proceed immediately
✅ **Structured Justification** - Framework for building business case
✅ **Automatic Routing** - System determines right approver
✅ **Transparency** - Status visible in Jira

### For the Company
✅ **Resource Optimization** - Best use of AI agent budgets
✅ **Goal Alignment** - Projects ladder up to OKRs
✅ **Financial Discipline** - Every project has ROI justification
✅ **Governance from Day 1** - No "rogue" projects
✅ **Measurable Outcomes** - Success metrics defined upfront

## Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| Project Creation | Ad-hoc, no approval | Structured, approval-based |
| Strategic Alignment | Optional, often missing | Mandatory declaration |
| Revenue Impact | Unknown or assumed | Quantified with confidence level |
| ROI Visibility | Calculated later (if at all) | Calculated upfront, reviewed |
| Leadership Awareness | After the fact | Before project starts |
| Budget Control | Reactive | Proactive |
| Approval Process | Email/Slack chaos | Structured Jira workflow |
| Audit Trail | Incomplete | Complete from inception |

## Future Enhancements

Potential improvements:
- **Dashboard** - Leadership view of all pending approvals
- **OKR Integration** - Automatic linking to company/team OKRs
- **Portfolio View** - See all projects by strategic goal
- **Actual vs Estimated** - Track real ROI vs projected
- **Post-Project Review** - Validate financial impact achieved
- **Budget Rollup** - Department/company-wide AI spend visibility
- **Auto-Approval Rules** - Certain patterns fast-track (e.g., proven templates)
- **ML-Based Scoring** - Predict project success based on historical data

## Summary

The leadership approval workflow ensures:
- 🎯 **Strategic Alignment** - Every project supports a company goal
- 💰 **Financial Justification** - ROI calculated before spending
- 👔 **Executive Visibility** - Leadership knows about major initiatives
- 📊 **Data-Driven Decisions** - Structured information for approvals
- ✅ **Controlled Spending** - Budget tiers with appropriate oversight
- 📝 **Complete Audit Trail** - From request to decision
- 🚀 **Fast for Small Projects** - No bureaucracy under $500/mo

**Result: AI-driven labor that generates measurable business value with executive oversight.**
