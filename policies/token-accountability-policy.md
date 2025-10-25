# Token Accountability Policy

**Version:** 1.1 (Gap Analysis Updates)
**Effective Date:** 2025-11-01
**Last Updated:** 2025-10-23
**Owner:** AI Governance Team

---

## Purpose

This policy establishes requirements and enforcement mechanisms for tracking, analyzing, and optimizing AI agent token consumption to minimize waste and control costs.

---

## Scope

This policy applies to:
- All users who interact with AI agents (Claude, GPT, etc.)
- All AI agent systems deployed by the organization
- All projects using AI agent assistance
- Internal and external AI services

---

## Policy Statements

### 1. Token Usage Logging Requirements

**1.1 Mandatory Logging Thresholds**

AI agents MUST log token usage for sessions meeting any of these criteria:
- Total tokens consumed ≥50,000
- Estimated cost ≥$0.15 USD
- Files changed ≥10
- Session duration ≥30 minutes
- Tier 3 or Tier 4 agent operations
- Production environment changes

**1.2 Logging Format**

All logs MUST conform to the JSON schema defined in:
`policies/schemas/token-usage.json`

**1.3 Log Storage**

Token usage logs SHALL be stored in:
- **Location:** `logs/token-usage/`
- **Retention:** 2 years minimum
- **Access:** Restricted to AI Governance Team and leadership
- **Format:** One JSON file per session (`{session-id}.json`)

**1.4 Required Fields**

At minimum, logs must include:
- session_id, timestamp, user_email
- project_name, task_description
- tokens_used, tokens_optimal, efficiency_pct
- files_changed, root_cause, efficiency_category

### 2. Human Responsibilities

**2.1 Provide Complete Requirements**

Users SHALL:
- Provide exact file paths when known
- Specify all requirements upfront in a single message
- Clarify scope before AI agent begins work
- Answer clarifying questions completely

**2.2 Follow Interaction Patterns**

Users SHALL follow patterns defined in:
`docs/HUMAN-AI-INTERACTION-GUIDE.md`

**2.3 Document for Continuity**

Users SHALL create session notes for incomplete work:
- Document decisions made
- List remaining tasks
- Provide context for next session
- Commit notes to git

### 3. AI Agent Responsibilities

**3.1 Demand Clarity**

AI agents MUST:
- Ask clarifying questions before starting work
- Refuse to proceed with ambiguous requirements
- Request exact file paths when locations are unclear
- Confirm scope before destructive operations

**3.2 Optimize Execution**

AI agents MUST:
- Execute tasks in single-pass when possible
- Batch file operations
- Avoid redundant reads
- Minimize clarification rounds

**3.3 Report Token Usage**

AI agents MUST call the logging script at session end:
```bash
python3 scripts/log-token-usage.py \\
  --session-id [UUID] \\
  --user [email] \\
  --project [name] \\
  --task "[description]" \\
  --tokens-used [N] \\
  --tokens-optimal [N] \\
  --files-changed [N] \\
  --root-cause [cause] \\
  --human-score [0-100] \\
  --ai-score [0-100]
```

**3.4 Document Sessions**

AI agents MUST:
- Commit all changes before session ends
- Create SESSION-NOTES.md for incomplete work
- Document root causes of inefficiency
- Provide recommendations to improve efficiency
- **Provide session summary** with task description, tokens used, efficiency assessment

**3.5 Session Summary Requirement (NEW v1.1)**

At end of significant tasks (>20,000 tokens), AI agents MUST provide:
```
Task: [brief description]
Tokens used: [number]
Efficiency: [optimal/suboptimal + reason]
Files changed: [count]
```

### 4. Efficiency Thresholds

**4.1 Efficiency Categories (UPDATED v1.1)**

Base thresholds (adjusted by workflow_type and task_type):

| Category | Efficiency Range | Action Required |
|----------|------------------|-----------------|
| Optimal | 80-100% | None - recognize good practices |
| Acceptable | 60-79% | Optional - review guidelines |
| Inefficient | 40-59% | Recommended - training suggested |
| Severely Wasteful | 0-39% | Mandatory - immediate action |

**4.1.1 Adjusted Thresholds by Workflow Type (Gap #7)**

| Workflow Type | Optimal | Acceptable | Rationale |
|---------------|---------|------------|-----------|
| Waterfall | ≥80% | 60-79% | All requirements upfront expected |
| Iterative | ≥65% | 50-64% | Legitimate refinement loops |
| Exploratory | ≥60% | 45-59% | Discovery process expected |
| Emergency | ≥50% | 35-49% | Context switching penalty |

**4.1.2 Adjusted Thresholds by User Experience (Gap #4)**

| Experience Level | Optimal | Grace Period |
|------------------|---------|--------------|
| New (<30 days) | ≥70% | First 10 sessions excluded from enforcement |
| Intermediate (30-90 days) | ≥75% | None |
| Experienced (>90 days) | ≥80% | None |

**4.1.3 AI Agent Failure Exemption (Gap #5)**

If `ai_agent_failure=true` and `ai_quality_score <70`:
- Inefficiency NOT attributed to human
- Session marked "AI failure - no penalty"
- AI Governance Team reviews AI agent performance
- Human receives efficiency credit

**4.2 Enforcement Actions by Category**

**Severely Wasteful (<40% efficient):**
- Mandatory training on Human-AI Interaction Guide
- Require pre-approval for AI agent usage for 30 days
- One-on-one coaching with AI Governance Team
- Weekly efficiency check-ins
- Leadership notification

**Inefficient (40-59% efficient):**
- Training strongly recommended
- Review token optimization protocols
- Monthly efficiency monitoring

**Acceptable (60-79% efficient):**
- Optional: Review guidelines and best practices
- Quarterly efficiency check

**Optimal (≥80% efficient):**
- Recognition in monthly report
- Share best practices with team

### 5. Reporting and Review

**5.1 Monthly Waste Reports**

AI Governance Team SHALL generate token waste reports by the 5th of each month:

```bash
python3 scripts/analyze-token-waste.py \\
  --log-dir logs/token-usage \\
  --start-date [YYYY-MM-01] \\
  --end-date [YYYY-MM-31] \\
  --format markdown \\
  --output reports/token-waste-[YYYYMM].md
```

**5.2 Report Distribution**

Reports SHALL be distributed to:
- Leadership team (by 5th)
- Department managers (by 10th)
- Individual users (efficiency scores only, by 15th)

**5.3 Review Meetings**

- **Monthly:** AI Governance Team reviews trends
- **Quarterly:** Leadership reviews cost impact and policy effectiveness
- **Annually:** Comprehensive review and policy updates

### 6. Training Requirements

**6.1 New User Onboarding**

All new AI agent users MUST complete:
- Human-AI Interaction Guide review
- Token optimization protocol training
- Hands-on practice session with feedback

**6.2 Ongoing Training**

Users with efficiency <60% MUST complete:
- Refresher training within 14 days of notification
- Practical exercises with AI Governance Team
- Follow-up efficiency assessment after 30 days

**6.3 Training Effectiveness**

Training completion and effectiveness SHALL be tracked:
- Pre-training efficiency baseline
- Post-training efficiency measurement
- 30-day and 90-day follow-up assessments

### 7. Enforcement Mechanisms

**7.1 Git Commit Hooks**

For sessions >50,000 tokens, git commits MUST include token usage log:

```bash
# Pre-commit hook checks for token log
if [ tokens_used -gt 50000 ] && [ ! -f logs/token-usage/${session_id}.json ]; then
  echo "Error: Token usage log required for sessions >50k tokens"
  exit 1
fi
```

**7.2 AI Agent Configuration**

AI agent system prompts MUST include:
- Reference to this policy
- Requirement to log token usage
- Mandate to follow interaction patterns
- **Session summary requirement** for tasks >20,000 tokens

**7.3 API Wrapper (Future - Gap #1)**

Planned for Q1 2026:
- Infrastructure-level token tracking
- Automatic logging (no AI agent cooperation needed)
- Real-time cost monitoring
- Cannot be circumvented by users

**7.3 Budget Controls**

Users consistently exceeding efficiency thresholds MAY have:
- AI agent usage limits imposed
- Budget allocations reduced
- Pre-approval requirements for high-token tasks

### 8. Exceptions and Waivers

**8.1 Emergency Operations**

Token logging MAY be deferred during:
- Production incidents
- Security emergencies
- Critical deadlines

Deferred logs MUST be submitted within 24 hours.

**8.2 Research and Experimentation**

Research projects MAY request waivers for:
- Novel AI agent use cases
- Proof-of-concept work
- Training/learning activities

Waivers must be approved by AI Governance Team.

---

## Implementation Timeline

| Phase | Date | Milestone |
|-------|------|-----------|
| Phase 1 | 2025-10-23 | Policy published, tools released |
| Phase 2 | 2025-11-01 | Voluntary logging begins |
| Phase 3 | 2025-11-15 | Training program launches |
| Phase 4 | 2025-12-01 | Mandatory logging enforced |
| Phase 5 | 2026-01-01 | Git hooks and automated enforcement active |

---

## Metrics and KPIs

### Primary Metrics

1. **Overall Efficiency:** Target ≥80%
2. **Waste Cost:** Target <20% of total AI costs
3. **Training Effectiveness:** Target ≥20% efficiency improvement post-training
4. **Compliance Rate:** Target 100% logging for sessions >50k tokens

### Secondary Metrics

1. Users requiring training (trend: decreasing)
2. Average human quality score (trend: increasing)
3. Top root causes of waste (monitor for patterns)
4. Time to efficiency improvement after training
5. **AI agent failure rate** (Gap #5 - trend: decreasing)
6. **Session continuation overhead** (Gap #8 - trend: decreasing)
7. **Workflow type distribution** (Gap #7 - monitor for patterns)

---

## Roles and Responsibilities

### AI Governance Team

- Develop and maintain policy
- Generate monthly reports
- Conduct training
- Review and approve waivers
- Enforce policy violations

### Department Managers

- Ensure team compliance
- Review team efficiency reports
- Assign required training
- Support improvement initiatives

### Individual Users

- Follow interaction patterns
- Provide clear requirements
- Complete assigned training
- Review personal efficiency scores

### AI Agents (Systems)

- Log token usage per policy
- Follow interaction protocols
- Report inefficiencies
- Provide recommendations

---

## Policy Violations

### Minor Violations

**Examples:**
- Missed token log (first occurrence)
- Incomplete log data

**Consequence:** Warning and reminder

### Moderate Violations

**Examples:**
- Repeated missed logs
- Refusal to complete training
- Efficiency <40% for 3+ consecutive sessions

**Consequence:**
- Mandatory training
- AI usage restrictions
- Manager notification

### Serious Violations

**Examples:**
- Intentional circumvention of logging
- Falsified efficiency reports
- Persistent non-compliance

**Consequence:**
- AI agent access suspended
- Formal performance review
- Leadership escalation

---

## Related Documents

- [Human-AI Interaction Guide](docs/HUMAN-AI-INTERACTION-GUIDE.md)
- [Token Optimization Protocol](/prompts/context/token_optimization.md)
- [Token Usage Schema](policies/schemas/token-usage.json)
- [Logging Script](scripts/log-token-usage.py)
- [Analysis Script](scripts/analyze-token-waste.py)
- [Dashboard Template](templates/reports/token-waste-dashboard.md)

---

## Policy Review and Updates

This policy SHALL be reviewed:
- **Quarterly:** Q1 effectiveness review
- **Annually:** Comprehensive policy revision
- **Ad-hoc:** When technology or usage patterns change significantly

**Next Review Date:** 2026-01-15

---

## Approval and Authorization

| Role | Name | Signature | Date |
|------|------|-----------|------|
| AI Governance Lead | [NAME] | ____________ | [DATE] |
| CTO/Engineering Lead | [NAME] | ____________ | [DATE] |
| CFO/Finance Lead | [NAME] | ____________ | [DATE] |

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-23 | Initial policy release | AI Governance Team |
| 1.1 | 2025-10-23 | Gap analysis updates: Added workflow types, experience levels, AI failure exemptions, session continuation tracking, privacy controls | AI Governance Team |

---

## Gap Analysis Summary (v1.1)

**Critical gaps addressed:**
- **Gap #5:** AI agent failure exemption - inefficiency not blamed on humans when AI fails
- **Gap #8:** Session continuation tracking - parent sessions blamed for missing documentation
- **Gap #7:** Workflow type adjustments - iterative/exploratory work has lower efficiency targets
- **Gap #3:** Task type context - emergency/exploratory work expectations adjusted
- **Gap #4:** Experience level grace periods - new users get adjusted thresholds
- **Gap #11:** Privacy controls - task description sanitization required

**Future roadmap:**
- **Gap #1:** API wrapper (Q1 2026) - infrastructure-level enforcement
- **Gap #9:** Recommendation tracking system (Q4 2025)
- **Gap #10:** Positive reinforcement/rewards (Q4 2025)

**See:** `docs/gap-analysis-token-accountability.md` for full analysis

---

**Questions or concerns?** Contact AI Governance Team at youngs@suhlabs.com
