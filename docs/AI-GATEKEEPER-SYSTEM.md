# AI Gatekeeper System

## Overview
The **AI Project Gatekeeper** is an autonomous AI agent (Tier 3) that evaluates project creation requests BEFORE they reach human leadership. It acts as the first-line filter to prevent misaligned or poorly justified projects from consuming leadership time.

## Philosophy
**"AI agents enforce governance rules, humans make strategic decisions"**

The AI Gatekeeper:
- ✅ **Enforces** minimum standards for business alignment and financial viability
- ✅ **Filters out** projects that don't meet company goals
- ✅ **Auto-approves** small, well-justified projects (<$500/mo, high scores)
- ✅ **Escalates** complex or high-budget projects to human leadership
- ✅ **Provides feedback** to requesters for improvement

## How It Works

### Workflow

```
User submits project request
          ↓
  🤖 AI GATEKEEPER EVALUATION
          ↓
    ┌─────┴─────┐
    │  Scoring  │
    │  0-100    │
    └─────┬─────┘
          ↓
    Decision Tree:
          ↓
    ┌─────────────────────────┐
    │ Score < 50             │ → ❌ REJECTED (send feedback)
    ├─────────────────────────┤
    │ Score 50-59            │ → ⚠️  NEEDS REVISION (specific fixes)
    ├─────────────────────────┤
    │ Score 60-79 AND        │ → 👔 ESCALATE TO LEADERSHIP (Jira)
    │ Budget >= $500         │
    ├─────────────────────────┤
    │ Score 80+ AND          │ → ✅ AUTO-APPROVED (proceed immediately)
    │ Budget < $500 AND      │
    │ No red flags           │
    └─────────────────────────┘
```

### Evaluation Categories

The AI Gatekeeper scores projects across 5 categories:

| Category | Max Points | Weight | Purpose |
|----------|-----------|---------|---------|
| **Strategic Alignment** | 20 | 25% | Does project support company goals? |
| **Financial Viability** | 25 | 30% | Is the ROI acceptable? Is revenue calculation reasonable? |
| **Resource Feasibility** | 20 | 20% | Are resources adequate? Is budget appropriate for tier? |
| **Risk Assessment** | 20 | 15% | Are there red flags? Unrealistic claims? |
| **Business Case Quality** | 15 | 10% | Is the business case complete and clear? |
| **TOTAL** | **100** | **100%** | |

### Scoring Threshold

- **Pass Threshold**: 60/100
- **Auto-Approval Threshold**: 80/100 (with additional criteria)
- **Rejection Threshold**: <50/100

## Evaluation Details

### 1. Strategic Alignment (20 points, 25% weight)

**What it checks:**
- Is the strategic goal a recognized company priority?
- Does the explanation clearly connect to the goal?
- Does the project description align with the stated goal?
- Are high-priority goals given proper justification?

**Scoring:**
- 16-20: Strong alignment
- 12-15: Moderate alignment
- 8-11: Weak alignment
- 0-7: No meaningful alignment

**Red Flags:**
- Strategic goal not in company priority list
- Vague or missing explanation (<50 characters)
- Project description doesn't match goal keywords
- Critical priority on low-priority goal

### 2. Financial Viability (25 points, 30% weight)

**What it checks:**
- Is the ROI ratio acceptable for the revenue type?
- Is the confidence level justified?
- Is the revenue calculation explained in detail?
- Does it match ROI benchmarks for similar projects?

**ROI Benchmarks by Type:**
| Revenue Type | Min ROI | Typical ROI |
|--------------|---------|-------------|
| Direct Revenue Generation | 3.0:1 | 5.0:1 |
| Cost Reduction (OpEx) | 3.0:1 | 5.0:1 |
| Customer Retention | 4.0:1 | 6.0:1 |
| Revenue Enablement | 2.5:1 | 4.0:1 |
| Efficiency Gain | 2.5:1 | 4.0:1 |
| Cost Reduction (CapEx) | 2.0:1 | 3.5:1 |
| Cost Avoidance | 2.0:1 | 3.0:1 |
| Risk Mitigation | 1.5:1 | 2.5:1 |

**Scoring:**
- 20-25: Excellent ROI (>= typical), high confidence, detailed explanation
- 15-19: Good ROI (>= minimum), reasonable justification
- 10-14: Marginal ROI, concerns about calculation
- 0-9: ROI below benchmarks or poorly justified

**Red Flags:**
- ROI < 1.0:1 (negative return)
- ROI > 20:1 (unrealistic)
- Low confidence with high value claim
- No revenue impact declared

### 3. Resource Feasibility (20 points, 20% weight)

**What it checks:**
- Is budget appropriate for agent tier?
- Are human resources identified?
- Is tech stack/infrastructure clearly defined?

**Budget Ranges by Tier:**
| Tier | Typical Budget Range |
|------|---------------------|
| 1 (Observer) | $10 - $500/mo |
| 2 (Developer) | $50 - $5,000/mo |
| 3 (Operations) | $100 - $10,000/mo |
| 4 (Architect) | $500 - $50,000/mo |

**Scoring:**
- 16-20: Budget appropriate, resources clearly identified, tech stack defined
- 12-15: Reasonable but some gaps in resource planning
- 8-11: Resource planning incomplete or budget mismatched
- 0-7: Significant resource concerns

**Red Flags:**
- No human resources identified
- Budget way outside tier norms
- Vague technical details

### 4. Risk Assessment (20 points, 15% weight)

**What it checks:**
- Are there unrealistic claims (ROI > 20:1)?
- Is project description too vague?
- Are there compliance mismatches?
- Does budget/value make sense together?

**Scoring:**
- 16-20: Low risk, no red flags
- 12-15: Moderate risk, minor concerns
- 8-11: High risk, several red flags
- 0-7: Critical risk factors

**Red Flags:**
- ROI > 20:1 (unrealistic)
- ROI > 10:1 (verify carefully)
- Vague descriptions (<50 chars)
- Tier 3+ with no compliance declaration
- Huge value claim with tiny budget
- Critical priority on low-priority goal

### 5. Business Case Quality (15 points, 10% weight)

**What it checks:**
- Completeness: Are all required fields filled?
- Clarity: Is there sufficient detail?

**Scoring:**
- 12-15: Complete (100%), clear, detailed (>400 chars total)
- 8-11: Mostly complete (80%+), adequate detail (>200 chars)
- 4-7: Incomplete (<80%), brief descriptions
- 0-3: Significantly incomplete or vague

## Decision Outcomes

### ✅ APPROVED (Auto-Approval)

**Criteria (ALL must be met):**
- Total score >= 80/100
- Budget < $500/month
- Strategic alignment >= 16/20
- ROI meets benchmarks
- No critical red flags

**Result:**
- Project approved immediately
- NO leadership review required
- Project can be created right away
- Approval recorded in audit trail

**Typical use case:** Small productivity tools, documentation assistants, low-cost automation

### 👔 ESCALATE_TO_HUMAN

**Criteria:**
- Total score >= 60/100
- Budget >= $500/month OR score < 80

**Result:**
- Jira issue created for leadership review
- AI evaluation included in Jira description
- Leadership makes final decision
- Requester notified via Slack

**Typical use case:** Most projects requiring manager/director/VP approval

### ⚠️ NEEDS_REVISION

**Criteria:**
- Total score 50-59/100

**Result:**
- Project blocked with specific feedback
- List of required revisions provided
- Suggested fixes for each issue
- Requester must revise and resubmit

**Typical use case:** Projects with promise but gaps in justification or planning

### ❌ REJECTED

**Criteria:**
- Total score < 50/100

**Result:**
- Project rejected outright
- Does not reach leadership
- Detailed feedback provided
- Requester can revise substantially and resubmit

**Typical use case:** Projects with weak strategic alignment, poor ROI, or major gaps

## Usage

### Command Line

```bash
# Automatic (integrated into submit-project-approval.py)
python3 scripts/submit-project-approval.py \
  --request-file ~/projects/project-approval-requests/PCR-2025-0123.json

# Standalone evaluation
python3 scripts/ai-project-gatekeeper.py \
  --request-file ~/projects/project-approval-requests/PCR-2025-0123.json \
  --verbose
```

### Output Example

```
======================================================================
AI PROJECT GATEKEEPER EVALUATION
======================================================================
Agent: project-gatekeeper-agent-v1 (Tier 3)
Request ID: PCR-2025-0123
Project: customer-support-bot
======================================================================

✅ EVALUATION RESULT: ESCALATE_TO_HUMAN
📊 Total Score: 72/100 (Threshold: 60)
💡 Recommendation: PROCEED_TO_LEADERSHIP

Category Scores:
  Strategic Alignment: 17.0/20 (85%)
  Financial Viability: 19.5/25 (78%)
  Resource Feasibility: 16.0/20 (80%)
  Risk Assessment: 16.0/20 (80%)
  Business Case Quality: 13.0/15 (87%)

👔 Project requires human leadership review
```

## Integration Points

### 1. Project Creation Script
`create-governed-project.sh` generates approval request → triggers AI evaluation automatically

### 2. Approval Submission Script
`submit-project-approval.py` runs AI Gatekeeper before creating Jira issue

### 3. Jira Integration
- AI evaluation results included in Jira description
- Evaluation ID for audit trail
- Leadership sees AI score and recommendation

### 4. Audit Trail
- All evaluations saved as JSON (`PCR-YYYY-NNNN-evaluation.json`)
- Includes timestamp, score breakdown, findings, recommendations
- Complete audit trail from request → AI eval → human decision

## AI Agent Configuration

**Agent ID**: `project-gatekeeper-agent-v1`
**Agent Tier**: 3 (Operations - has authority to block projects)
**Evaluation Version**: 1.0.0
**Model**: Rule-based evaluation engine

**Governance:**
- Agent operates autonomously within defined rules
- Cannot be bypassed for projects requiring approval
- All decisions logged for audit
- Human leadership can override any decision

## Benefits

### For Leadership
✅ **Time Savings**: Only review projects that pass minimum standards
✅ **Quality Filter**: No poorly justified projects reach leadership
✅ **Data-Driven**: Consistent evaluation criteria applied to all projects
✅ **Audit Trail**: Complete record of AI + human decisions

### For Teams
✅ **Fast Feedback**: Immediate evaluation (not waiting days for leadership)
✅ **Specific Guidance**: Detailed feedback on what to improve
✅ **Auto-Approval**: Small projects (<$500, high quality) approved instantly
✅ **Transparency**: Clear scoring shows exactly why project passed/failed

### For the Company
✅ **Strategic Alignment**: Only goal-aligned projects proceed
✅ **Financial Discipline**: ROI benchmarks enforced
✅ **Resource Optimization**: Poor projects filtered before wasting resources
✅ **Consistent Standards**: Same rules applied to everyone
✅ **Scalability**: Can handle high volume of project requests

## Example Scenarios

### Scenario 1: Small Productivity Tool (Auto-Approved)
```
Project: Documentation search assistant
Budget: $200/month
Strategic Goal: Team Productivity
ROI: 5.0:1 ($12K value / $2.4K cost)

AI Evaluation:
- Strategic Alignment: 18/20 (Strong)
- Financial Viability: 22/25 (Excellent ROI)
- Resource Feasibility: 18/20 (Appropriate)
- Risk Assessment: 18/20 (Low risk)
- Business Case Quality: 14/15 (Complete)
Total: 90/100

✅ APPROVED - Auto-approved, no leadership review needed
```

### Scenario 2: Customer Support Bot (Escalate)
```
Project: AI customer support agent
Budget: $1,500/month
Strategic Goal: Reduce Costs
ROI: 4.4:1 ($80K value / $18K cost)

AI Evaluation:
- Strategic Alignment: 17/20 (Strong)
- Financial Viability: 19/25 (Good ROI)
- Resource Feasibility: 16/20 (Appropriate)
- Risk Assessment: 16/20 (Moderate)
- Business Case Quality: 13/15 (Good)
Total: 72/100

👔 ESCALATE_TO_HUMAN - Requires manager approval (budget > $500)
```

### Scenario 3: Vague Request (Needs Revision)
```
Project: AI automation thing
Budget: $800/month
Strategic Goal: Team Productivity
ROI: 10.0:1 (no details)

AI Evaluation:
- Strategic Alignment: 9/20 (Vague explanation)
- Financial Viability: 12/25 (ROI not justified)
- Resource Feasibility: 10/20 (Incomplete)
- Risk Assessment: 14/20 (Several concerns)
- Business Case Quality: 6/15 (Too brief)
Total: 51/100

⚠️ NEEDS_REVISION - Must improve strategic alignment and financial justification
```

### Scenario 4: Poor Alignment (Rejected)
```
Project: Personal productivity experiment
Budget: $600/month
Strategic Goal: Technical Debt Reduction (low priority)
ROI: 0.5:1 (negative return)

AI Evaluation:
- Strategic Alignment: 7/20 (Weak, personal project)
- Financial Viability: 4/25 (Negative ROI)
- Resource Feasibility: 8/20 (Budget too high for value)
- Risk Assessment: 10/20 (Multiple red flags)
- Business Case Quality: 5/15 (Incomplete)
Total: 34/100

❌ REJECTED - Does not meet minimum standards for company investment
```

## Audit and Accountability

### Evaluation Records
Every evaluation creates:
- JSON evaluation file (`PCR-YYYY-NNNN-evaluation.json`)
- Timestamp and duration
- Complete score breakdown
- Findings and rationale for each category
- Recommendation and confidence level
- Required revisions (if any)

### Human Override
Leadership can override AI Gatekeeper decisions:
- Approve a rejected project (with justification)
- Reject an approved project (rare)
- Override recorded in audit trail
- Reason for override documented

### Continuous Improvement
AI Gatekeeper rules can be updated based on:
- Feedback from leadership
- Analysis of approved vs. rejected project outcomes
- Company strategic priority changes
- ROI benchmark updates

## Future Enhancements

Potential improvements:
- **ML-based scoring**: Learn from historical project outcomes
- **Benchmark updates**: Dynamic ROI benchmarks based on actual performance
- **Department-specific rules**: Different standards for different teams
- **Integration with OKRs**: Automatic alignment check against current OKRs
- **Sentiment analysis**: Evaluate quality of written explanations
- **Competitor analysis**: Compare to industry benchmarks
- **Success prediction**: Estimate probability of project success

## Files and Schema

- **Schema**: `policies/schemas/ai-project-evaluation.json`
- **AI Agent Script**: `scripts/ai-project-gatekeeper.py`
- **Integration Script**: `scripts/submit-project-approval.py`
- **Documentation**: `docs/AI-GATEKEEPER-SYSTEM.md` (this file)

## Summary

The AI Project Gatekeeper:
- 🤖 **Autonomous Tier 3 agent** with authority to approve/reject projects
- 📊 **Consistent evaluation** using 5 categories, 100-point scale
- ✅ **Auto-approves** small, high-quality projects (<$500, score 80+)
- 👔 **Escalates** complex projects to human leadership
- ❌ **Rejects** poorly justified projects before they waste leadership time
- 📝 **Provides feedback** with specific revisions needed
- 🔍 **Complete audit trail** for every evaluation

**Result: Leadership focuses on strategic decisions, AI enforces quality standards.**
