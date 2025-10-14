# Jira Integration for Multi-Agent Workflows

**Version:** 1.0
**Last Updated:** 2025-10-14
**Purpose:** Track issues, approvals, and change control across multi-agent development stages

---

## Overview

Integrate Jira with the PAR-PROTO multi-agent workflow to provide:
- **Issue Tracking**: Single source of truth for project status
- **Approval Workflows**: Quality gate approvals with audit trail
- **Change Control**: Document all decisions and changes
- **Traceability**: Link agents' work to business requirements
- **Reporting**: Real-time dashboards and metrics

---

## Jira Workflow Setup

### Issue Types

Create custom issue types for multi-agent projects:

```yaml
issue_types:
  - name: "Multi-Agent Project"
    description: "Parent issue for multi-agent development"
    key: "MAP"

  - name: "Agent Stage"
    description: "Sub-task for each agent stage"
    key: "STAGE"

  - name: "Quality Gate"
    description: "Sub-task for quality gate reviews"
    key: "QG"

  - name: "Integration Test"
    description: "Sub-task for testing activities"
    key: "TEST"
```

### Workflow States

```yaml
workflow_states:
  # Initial
  - "Backlog"
  - "To Do"

  # Stage 1: Prototype
  - "Stage 1: In Progress (Copilot)"
  - "Stage 1: Complete"
  - "Quality Gate 1: Review"
  - "Quality Gate 1: Approved"

  # Stage 2: Production
  - "Stage 2: In Progress (Claude)"
  - "Stage 2: Complete"
  - "Quality Gate 2: Review"
  - "Quality Gate 2: Approved"

  # Stage 3: Testing (if applicable)
  - "Stage 3: In Progress (Gemini)"
  - "Stage 3: Complete"
  - "Quality Gate 3: Review"
  - "Quality Gate 3: Approved"

  # Deployment
  - "Ready for Deployment"
  - "Deployed to Staging"
  - "Deployed to Production"
  - "Done"

  # Exception states
  - "Blocked"
  - "Rejected"
  - "On Hold"
```

---

## Issue Structure

### Parent Issue: Multi-Agent Project

```yaml
issue:
  type: "Multi-Agent Project"
  summary: "[PROJECT] Build Splunk Asset & Identity Framework"

  fields:
    description: |
      ## Problem Statement
      Need comprehensive asset/identity resolution framework for Splunk ES

      ## Success Criteria
      - Complete whitepaper documentation
      - Production-ready SPL examples
      - Configuration templates
      - 90%+ test coverage (if Stage 3)

    priority: "High"
    labels: ["multi-agent", "tier-3", "par-proto"]

    custom_fields:
      agent_pattern: "Three-Agent (Copilot → Claude → Gemini)"
      total_budget: "$100"
      expected_duration: "8 days"
      tier_level: "Tier 3"

    components:
      - "Documentation"
      - "Code"
      - "Testing"

    linked_issues:
      - "STAGE-101: Stage 1 - Prototype (Copilot)"
      - "STAGE-102: Stage 2 - Production (Claude)"
      - "STAGE-103: Stage 3 - Testing (Gemini)"
      - "QG-101: Quality Gate 1"
      - "QG-102: Quality Gate 2"
      - "QG-103: Quality Gate 3"
```

### Sub-task: Agent Stage

```yaml
subtask:
  type: "Agent Stage"
  summary: "[STAGE 1] Prototype with Copilot"
  parent: "MAP-123"

  fields:
    description: |
      ## Stage Objective
      Rapid prototyping and proof of concept

      ## Agent Details
      - Agent: GitHub Copilot
      - Environment: VS Code
      - Estimated Duration: 1-2 days
      - Estimated Cost: $5-10

      ## Deliverables
      - [ ] Working prototype
      - [ ] Architecture notes
      - [ ] Lessons learned document

      ## Handoff Artifacts
      - prototype_code/
      - architecture.md
      - open_questions.md

    assignee: "Copilot Agent (Operator: @johndoe)"
    labels: ["stage-1", "copilot", "prototype"]

    custom_fields:
      agent_type: "GitHub Copilot"
      stage_number: 1
      estimated_cost: "$8"
      actual_cost: "$7.50"  # Updated post-completion
      start_date: "2025-10-14"
      completion_date: "2025-10-15"
```

### Sub-task: Quality Gate

```yaml
subtask:
  type: "Quality Gate"
  summary: "[QG1] Prototype → Production Review"
  parent: "MAP-123"

  fields:
    description: |
      ## Quality Gate Review

      ### Checklist
      - [ ] Proof of concept works
      - [ ] Architecture is sound
      - [ ] No major technical blockers
      - [ ] Stakeholders approve approach
      - [ ] ROI projection positive

      ### Review Artifacts
      - Architecture notes
      - Prototype demo
      - Lessons learned

      ### Decision Criteria
      All required items must pass to proceed to Stage 2

    assignee: "@techlead"
    due_date: "2025-10-15"

    custom_fields:
      gate_number: 1
      required_approvers:
        - "Tech Lead"
        - "Product Owner"
      approval_status: "Pending"

  transitions:
    on_approval:
      next_status: "Quality Gate 1: Approved"
      trigger_action: "Start STAGE-102 (Stage 2)"
      slack_notification: "#project-channel"

    on_rejection:
      next_status: "Rejected"
      reopen_issue: "STAGE-101"
      required_action: "Address feedback and resubmit"
```

---

## Approval Workflows

### Quality Gate 1: Prototype → Production

```yaml
quality_gate_1_workflow:
  trigger:
    status: "Stage 1: Complete"
    action: "Create QG-XXX issue"

  approval_process:
    step_1:
      approver: "Tech Lead"
      checklist:
        - "Technical feasibility validated"
        - "Architecture approach sound"
        - "No critical blockers"
      decision: ["Approve", "Request Changes", "Reject"]
      sla: "4 hours"

    step_2:
      approver: "Product Owner"
      checklist:
        - "Meets business requirements"
        - "ROI projection acceptable"
        - "Timeline realistic"
      decision: ["Approve", "Request Changes"]
      sla: "8 hours"

  automation:
    on_all_approved:
      - action: "Transition parent to 'Quality Gate 1: Approved'"
      - action: "Create STAGE-102 (Stage 2) issue"
      - action: "Assign to Claude operator"
      - notification:
          slack: "#project-channel"
          message: "✅ QG1 approved. Starting Stage 2 with Claude."

    on_any_rejected:
      - action: "Transition to 'Quality Gate 1: Rejected'"
      - action: "Reopen STAGE-101"
      - action: "Add comment with feedback"
      - notification:
          slack: "#project-channel"
          message: "❌ QG1 rejected. See Jira for details."
```

### Quality Gate 2: Production → Testing

```yaml
quality_gate_2_workflow:
  trigger:
    status: "Stage 2: Complete"
    action: "Create QG-XXX issue"

  approval_process:
    step_1:
      approver: "Tech Lead"
      checklist:
        - "Code complete and reviewed"
        - "Documentation comprehensive"
        - "Error handling implemented"
        - "Configuration externalized"
      decision: ["Approve", "Request Changes", "Reject"]
      sla: "4 hours"

    step_2:
      approver: "Security Team"
      required_if: "tier >= 3"
      checklist:
        - "No obvious security issues"
        - "Secrets management correct"
        - "Authentication/authorization reviewed"
      decision: ["Approve", "Request Security Testing"]
      sla: "8 hours"

  automation:
    on_all_approved:
      - action: "Transition to 'Quality Gate 2: Approved'"
      - action: "Create STAGE-103 (Stage 3) issue"
      - action: "Assign to Gemini operator"
      - notification:
          slack: "#project-channel"
          message: "✅ QG2 approved. Starting Stage 3 with Gemini for testing."
```

### Quality Gate 3: Testing → Production

```yaml
quality_gate_3_workflow:
  trigger:
    status: "Stage 3: Complete"
    action: "Create QG-XXX issue"

  approval_process:
    step_1:
      approver: "QA Lead"
      checklist:
        - "Test coverage ≥90%"
        - "All tests passing"
        - "Performance tests passed"
      decision: ["Approve", "Request Fixes"]
      sla: "4 hours"

    step_2:
      approver: "Security Team"
      checklist:
        - "No critical vulnerabilities"
        - "High severity issues resolved"
        - "Medium issues documented/accepted"
      decision: ["Approve", "Block on Security"]
      sla: "8 hours"

    step_3:
      approver: "Tech Lead"
      checklist:
        - "Production readiness confirmed"
        - "Rollback plan documented"
        - "Monitoring configured"
      decision: ["Approve for Production"]
      sla: "4 hours"

  automation:
    on_all_approved:
      - action: "Transition to 'Ready for Deployment'"
      - action: "Create deployment ticket"
      - notification:
          slack: "#project-channel"
          message: "🚀 QG3 approved. Ready for production deployment!"
          mention: "@deployment-team"
```

---

## Change Control Documentation

### Change Request Fields

Add custom fields to track changes:

```yaml
custom_fields:
  # Change identification
  - name: "Change Type"
    options: ["New Feature", "Enhancement", "Bug Fix", "Refactoring"]

  - name: "Risk Level"
    options: ["Low", "Medium", "High", "Critical"]

  - name: "Impact Analysis"
    type: "Text (multi-line)"
    description: "What systems/users are affected?"

  # Agent tracking
  - name: "Agent Used"
    options: ["Copilot", "Claude", "Gemini", "Multiple"]

  - name: "Agent Cost"
    type: "Number"
    description: "Cost in dollars"

  - name: "Agent Iterations"
    type: "Number"
    description: "Number of agent interactions"

  # Quality metrics
  - name: "Test Coverage"
    type: "Percentage"
    description: "Unit test coverage %"

  - name: "Bugs Found"
    type: "Number"
    description: "Bugs found during Stage 3"

  - name: "Security Issues"
    type: "Number"
    description: "Security vulnerabilities identified"

  # Approvals
  - name: "Quality Gate Status"
    options: ["Pending", "Approved", "Rejected", "Skipped"]

  - name: "Approvers"
    type: "Multi-user select"
    description: "All required approvers"

  - name: "Approval Date"
    type: "Date"
```

### Change Log

Automatically populate change log from Jira:

```python
# Example: Generate change log from Jira API
import requests
from datetime import datetime

def generate_change_log(project_key, version):
    """
    Generate change log from Jira for a specific version
    """
    jira_url = "https://yourcompany.atlassian.net"
    jql = f"project = {project_key} AND fixVersion = {version} AND type = 'Multi-Agent Project'"

    headers = {
        "Authorization": f"Bearer {JIRA_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"{jira_url}/rest/api/3/search",
        headers=headers,
        params={"jql": jql, "fields": "summary,customfield_*"}
    )

    issues = response.json()["issues"]

    changelog = []
    for issue in issues:
        entry = {
            "issue_key": issue["key"],
            "summary": issue["fields"]["summary"],
            "agent_pattern": issue["fields"]["customfield_10050"],  # Custom field
            "total_cost": issue["fields"]["customfield_10051"],
            "completion_date": issue["fields"]["customfield_10052"],
            "test_coverage": issue["fields"]["customfield_10053"],
        }
        changelog.append(entry)

    return changelog
```

---

## Automation Rules

### Rule 1: Auto-create Stage Sub-tasks

```yaml
automation_rule_1:
  name: "Create Agent Stage Sub-tasks"
  trigger:
    event: "Issue Created"
    condition: "issueType = 'Multi-Agent Project'"

  actions:
    - action: "Create sub-task"
      fields:
        type: "Agent Stage"
        summary: "{{issue.key}} - Stage 1: Prototype (Copilot)"
        assignee: "{{customfield_copilot_operator}}"

    - action: "Create sub-task"
      fields:
        type: "Agent Stage"
        summary: "{{issue.key}} - Stage 2: Production (Claude)"
        assignee: "{{customfield_claude_operator}}"

    - action: "Create sub-task (if three-agent)"
      condition: "customfield_agent_pattern contains 'Three-Agent'"
      fields:
        type: "Agent Stage"
        summary: "{{issue.key}} - Stage 3: Testing (Gemini)"
        assignee: "{{customfield_gemini_operator}}"
```

### Rule 2: Auto-create Quality Gates

```yaml
automation_rule_2:
  name: "Create Quality Gate on Stage Complete"
  trigger:
    event: "Issue Transitioned"
    condition: "status = 'Stage X: Complete'"

  actions:
    - action: "Create sub-task"
      fields:
        type: "Quality Gate"
        summary: "{{issue.parent.key}} - Quality Gate {{stage_number}}"
        assignee: "{{customfield_approvers}}"
        due_date: "{{now + 1 day}}"
```

### Rule 3: Slack Notifications

```yaml
automation_rule_3:
  name: "Notify Slack on Quality Gate"
  trigger:
    event: "Issue Transitioned"
    condition: "issueType = 'Quality Gate'"

  actions:
    - action: "Send Slack message"
      webhook: "{{slack_webhook_url}}"
      channel: "#project-channel"
      message: |
        🔔 Quality Gate {{issue.key}} requires review

        *Project:* {{issue.parent.summary}}
        *Gate:* {{issue.summary}}
        *Assignee:* @{{issue.assignee.name}}
        *Due:* {{issue.dueDate}}

        👉 {{issue.url}}

    - action: "Mention approvers"
      users: "{{customfield_required_approvers}}"
```

### Rule 4: Cost Tracking

```yaml
automation_rule_4:
  name: "Update Total Cost on Stage Complete"
  trigger:
    event: "Issue Transitioned"
    condition: "issueType = 'Agent Stage' AND status = 'Complete'"

  actions:
    - action: "Calculate total cost"
      script: |
        # Sum all stage costs
        parent_issue = issue.parent
        stages = parent_issue.subtasks(type='Agent Stage')
        total_cost = sum([s.customfield_actual_cost for s in stages if s.customfield_actual_cost])

        # Update parent
        parent_issue.customfield_total_cost = total_cost
        parent_issue.update()

    - action: "Check budget alert"
      condition: "total_cost > parent.customfield_total_budget"
      notification:
        slack: "#project-channel"
        message: "⚠️ Budget exceeded on {{parent.key}}!"
```

---

## Dashboards & Reporting

### Multi-Agent Project Dashboard

```yaml
dashboard:
  name: "Multi-Agent Projects Overview"

  gadgets:
    - type: "Filter Results"
      jql: "project = PROJ AND type = 'Multi-Agent Project'"
      columns: ["Key", "Summary", "Status", "Agent Pattern", "Total Cost", "Assignee"]

    - type: "Pie Chart"
      title: "Projects by Stage"
      jql: "project = PROJ AND type = 'Multi-Agent Project'"
      stat_type: "statuses"

    - type: "Two Dimensional Filter Statistics"
      title: "Cost by Agent Pattern"
      jql: "project = PROJ AND type = 'Multi-Agent Project'"
      x_axis: "Agent Pattern"
      y_axis: "customfield_total_cost"
      calculation: "Average"

    - type: "Created vs Resolved Chart"
      title: "Project Completion Trend"
      period: "Monthly"

    - type: "Average Age"
      title: "Avg Time in Quality Gates"
      jql: "project = PROJ AND type = 'Quality Gate'"
```

### Quality Gate Metrics

```yaml
quality_gate_dashboard:
  name: "Quality Gate Performance"

  gadgets:
    - type: "Filter Results"
      title: "Pending Quality Gates"
      jql: "type = 'Quality Gate' AND status = 'Review'"
      sort: "dueDate ASC"

    - type: "Time Since Chart"
      title: "Quality Gate Approval Time"
      jql: "type = 'Quality Gate' AND status = 'Approved'"
      period: "Last 30 days"
      calculation: "Time from Created to Approved"

    - type: "Pie Chart"
      title: "Quality Gate Outcomes"
      jql: "type = 'Quality Gate' AND resolved is not EMPTY"
      stat_type: "statuses"
      labels: ["Approved", "Rejected", "Skipped"]
```

### Agent Performance Metrics

```yaml
agent_metrics_dashboard:
  name: "Agent Performance & Costs"

  gadgets:
    - type: "Bar Chart"
      title: "Cost by Agent Type"
      jql: "type = 'Agent Stage' AND resolved is not EMPTY"
      x_axis: "customfield_agent_type"
      y_axis: "customfield_actual_cost"
      calculation: "Average"

    - type: "Line Chart"
      title: "Agent Cost Trend"
      jql: "type = 'Agent Stage' AND resolved is not EMPTY"
      period: "Last 90 days"
      y_axis: "customfield_actual_cost"

    - type: "Table"
      title: "ROI by Project"
      jql: "type = 'Multi-Agent Project' AND resolved is not EMPTY"
      columns: ["Key", "Summary", "Total Cost", "Time Saved", "ROI Ratio"]
      calculation: "customfield_time_saved / customfield_total_cost"
```

---

## Best Practices

### DO ✅

1. **Always create parent Multi-Agent Project issue first**
   - Provides single source of truth
   - Links all related work

2. **Use sub-tasks for each stage**
   - Clear accountability
   - Easy to track progress

3. **Document all quality gate decisions**
   - Add comments with rationale
   - Attach supporting artifacts

4. **Update actual costs after each stage**
   - Helps with future estimation
   - Tracks budget vs. actual

5. **Link to external artifacts**
   - GitHub PRs
   - Slack threads
   - Documentation

6. **Set realistic due dates for quality gates**
   - Prevents bottlenecks
   - Ensures timely reviews

### DON'T ❌

1. **Don't skip quality gate issues**
   - Loses audit trail
   - Bypasses approval process

2. **Don't combine multiple stages in one issue**
   - Loses clarity
   - Harder to track metrics

3. **Don't forget to update status**
   - Dashboards become inaccurate
   - Stakeholders lose visibility

4. **Don't skip cost tracking**
   - Can't measure ROI
   - Budget overruns not detected

---

## Example Jira Board Configuration

```yaml
board:
  name: "Multi-Agent Projects"
  type: "Kanban"

  columns:
    - name: "Backlog"
      statuses: ["Backlog", "To Do"]

    - name: "Stage 1 (Copilot)"
      statuses: ["Stage 1: In Progress"]

    - name: "QG1"
      statuses: ["Quality Gate 1: Review"]

    - name: "Stage 2 (Claude)"
      statuses: ["Stage 2: In Progress"]

    - name: "QG2"
      statuses: ["Quality Gate 2: Review"]

    - name: "Stage 3 (Gemini)"
      statuses: ["Stage 3: In Progress"]

    - name: "QG3"
      statuses: ["Quality Gate 3: Review"]

    - name: "Deployment"
      statuses: ["Ready for Deployment", "Deployed to Staging"]

    - name: "Done"
      statuses: ["Deployed to Production", "Done"]

  swimlanes:
    type: "Query"
    queries:
      - "Tier 3-4 (Production Critical)"
      - "Tier 1-2 (Internal/Dev)"

  quick_filters:
    - name: "Blocked"
      jql: "status = 'Blocked'"

    - name: "Overdue QGs"
      jql: "type = 'Quality Gate' AND dueDate < now()"

    - name: "Over Budget"
      jql: "customfield_total_cost > customfield_total_budget"
```

---

## Related Documentation

- [Slack Integration](slack-integration.md) - Discussion tracking
- [Three-Agent Workflow](../three-agent-workflow.md) - Complete workflow guide
- [Quality Gate Templates](../templates/) - Checklist templates

---

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-14 | Initial Jira integration guide | AI Governance Framework |

---

**This integration provides complete traceability and accountability for multi-agent development workflows.**
