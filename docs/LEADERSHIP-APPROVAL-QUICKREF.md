# Leadership Approval - Quick Reference

## Approval Tiers (Budget-Based)

| Budget/Month | Approval Tier | Auto-Approve? |
|--------------|---------------|---------------|
| < $500 | Team Lead Only | ✅ Yes |
| $500 - $2K | Manager | ❌ Requires approval |
| $2K - $10K | Director | ❌ Requires approval |
| $10K - $50K | VP | ❌ Requires approval |
| > $50K | Executive | ❌ Requires approval |

**Strategic Override:** "Enter New Market" or "Product Innovation" → Executive approval (any budget)

## Workflow Summary

```
1. Run: create-governed-project.sh
   ↓
2. Answer questions (including business alignment)
   ↓
3. System determines approval tier
   ↓
4a. Budget < $500 → Project created immediately ✅
4b. Budget >= $500 → Approval request generated ⏸️
   ↓
5. Submit to Jira: submit-project-approval.py
   ↓
6. Leadership reviews & approves in Jira
   ↓
7. Re-run create-governed-project.sh (now approved)
```

## Required Business Information

Every project must provide:

### Strategic Alignment
- Which strategic goal? (9 options)
- How does it support the goal?

### Revenue Impact
- Impact type (revenue, cost reduction, efficiency, etc.)
- Estimated annual value ($)
- Confidence level (High/Medium/Low)
- Explanation of calculation

### Priority
- Critical / High / Medium / Low

## Strategic Goals

1. Increase Revenue
2. Reduce Costs
3. Improve Customer Experience
4. Enter New Market ⚡ (Executive approval)
5. Product Innovation ⚡ (Executive approval)
6. Operational Excellence
7. Compliance & Risk Management
8. Technical Debt Reduction
9. Team Productivity

## Revenue Impact Types

- Direct Revenue Generation
- Revenue Enablement
- Cost Reduction (OpEx)
- Cost Reduction (CapEx)
- Cost Avoidance
- Customer Retention
- Efficiency Gain
- Risk Mitigation
- None

## Commands

### Create Project (with approval gate)
```bash
~/projects/ai-agent-governance-framework/scripts/create-governed-project.sh
```

### Submit for Approval
```bash
python3 ~/projects/ai-agent-governance-framework/scripts/submit-project-approval.py \
  --request-file ~/projects/project-approval-requests/PCR-2025-XXXX.json
```

### Check Approval Status (Jira)
```bash
# Visit Jira issue
https://your-company.atlassian.net/browse/PROJAPPR-XXX
```

## Environment Setup

```bash
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT_APPROVAL_KEY="PROJAPPR"
export SLACK_LEADERSHIP_WEBHOOK="https://hooks.slack.com/..." # Optional
```

## What Leadership Sees in Jira

- Project name and description
- Owner and requester
- Strategic goal alignment
- Revenue impact type and annual value
- ROI ratio (e.g., 5.0:1)
- Payback period (e.g., 2.4 months)
- Monthly budget and annual cost
- Resource requirements
- Risk assessment
- Success metrics

## Decision Criteria

| ROI Ratio | Signal | Typical Action |
|-----------|--------|----------------|
| < 2:1 | ⚠️ Low | Requires strong justification |
| 2:1 to 5:1 | ✅ Standard | Normal approval |
| > 5:1 | 🚀 High | Fast-track |

| Payback Period | Signal |
|----------------|--------|
| < 6 months | ✅ Positive |
| 6-12 months | ⚠️ Moderate |
| > 12 months | ⚠️ Requires long-term rationale |

## Files & Locations

- Schema: `policies/schemas/project-creation-request.json`
- Approval requests: `~/projects/project-approval-requests/`
- Documentation: `docs/LEADERSHIP-APPROVAL-WORKFLOW.md`

## Key Benefits

✅ Strategic alignment enforced
✅ ROI calculated upfront
✅ Leadership visibility before spending
✅ Fast approval for small projects (<$500)
✅ Structured Jira workflow
✅ Complete audit trail
✅ Slack notifications (optional)
